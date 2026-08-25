#!/usr/bin/env python3
"""Reconcile current target artifacts with image, RAM and rollback boundaries."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from capture_target_build_review import input_manifest
from check_image_size import classify, load_limits


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "config" / "f3_3_boundary_review.json"
IDF_SIZE = REPO_ROOT / ".toolchains/src/esp-idf/tools/idf_size.py"
LOCKED_PYTHON = REPO_ROOT / ".toolchains/python/idf6_py3.12_env/bin/python"
ARM_SIZE = (
    REPO_ROOT
    / ".toolchains/tools/arm-gnu-toolchain-15.2.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-size"
)
TARGETS = ("s3", "c5", "rp", "pack", "safety")
CONFIGURATIONS = ("debug", "release")
ESP_INPUTS = {
    "s3": {
        "partition": "config/partitions_16m.csv",
        "flash_bytes": 16 * 1024 * 1024,
        "image": "leshy2_s3.bin",
        "elf": "leshy2_s3.elf",
        "map": "leshy2_s3.map",
        "bootloader_partition_bytes": 32768,
        "external_ram_bytes": 8 * 1024 * 1024,
        "external_ram_runtime_proven": True,
    },
    "c5": {
        "partition": "config/partitions_8m_c5.csv",
        "flash_bytes": 8 * 1024 * 1024,
        "image": "leshy2_c5.bin",
        "elf": "leshy2_c5.elf",
        "map": "leshy2_c5.map",
        "bootloader_partition_bytes": 24576,
        "external_ram_bytes": 8 * 1024 * 1024,
        "external_ram_runtime_proven": False,
    },
}
TI_MAP_RE = re.compile(
    r"^\s+(FLASH|SRAM)\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})"
    r"\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+"
)
SIZE_ROW_RE = re.compile(r"^(\S+)\s+(\d+)\s+(\d+)\s*$")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict:
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def parse_esp_partitions(relative: str, flash_bytes: int) -> list[dict]:
    rows: list[dict] = []
    path = REPO_ROOT / relative
    with path.open(encoding="utf-8", newline="") as source:
        for raw in csv.reader(source):
            if not raw or raw[0].lstrip().startswith("#"):
                continue
            fields = [field.strip() for field in raw]
            offset = int(fields[3], 0)
            size = int(fields[4], 0)
            rows.append(
                {
                    "name": fields[0],
                    "type": fields[1],
                    "subtype": fields[2],
                    "offset": offset,
                    "size": size,
                    "end": offset + size,
                }
            )
    previous_end = 0
    for row in rows:
        if row["offset"] < previous_end or row["end"] > flash_bytes:
            raise RuntimeError(f"invalid or overlapping partition: {relative}:{row['name']}")
        previous_end = row["end"]
    if not rows or rows[-1]["end"] != flash_bytes:
        raise RuntimeError(f"partition table does not close exact flash size: {relative}")
    return rows


def idf_memory(map_path: Path) -> list[dict]:
    result = subprocess.run(
        [str(LOCKED_PYTHON), str(IDF_SIZE), "--format", "json2", str(map_path)],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"idf_size failed for {map_path}:\n{result.stdout}")
    report = json.loads(result.stdout)
    return [
        {
            "name": row["name"],
            "total_bytes": row["total"],
            "used_bytes": row["used"],
            "free_bytes": row["free"],
        }
        for row in report["layout"]
        if row["total"] > 0
    ]


def esp_target(target: str) -> dict:
    spec = ESP_INPUTS[target]
    partitions = parse_esp_partitions(spec["partition"], spec["flash_bytes"])
    ota = [row for row in partitions if row["name"] in {"ota_0", "ota_1"}]
    limits = load_limits(target)
    if len(ota) != 2 or any(row["size"] != limits["slot_bytes"] for row in ota):
        raise RuntimeError(f"{target}: dual OTA slots diverge from the image limit")

    configurations: dict[str, dict] = {}
    for configuration in CONFIGURATIONS:
        root = REPO_ROOT / "build/targets" / target / configuration
        image = root / spec["image"]
        bootloader = root / "bootloader/bootloader.bin"
        image_bytes = image.stat().st_size
        result = classify(image_bytes, limits)
        if result == "reject":
            raise RuntimeError(f"{target}:{configuration}: application image rejected")
        boot_bytes = bootloader.stat().st_size
        if boot_bytes > spec["bootloader_partition_bytes"]:
            raise RuntimeError(f"{target}:{configuration}: bootloader partition overflow")
        configurations[configuration] = {
            "application": artifact(image),
            "target_elf": artifact(root / spec["elf"]),
            "map_sha256": sha256(root / spec["map"]),
            "image_gate": {
                "result": result,
                "slot_bytes": limits["slot_bytes"],
                "maximum_image_bytes": limits["maximum_image_bytes"],
                "free_before_maximum_bytes": limits["maximum_image_bytes"] - image_bytes,
                "free_in_slot_bytes": limits["slot_bytes"] - image_bytes,
            },
            "bootloader": {
                **artifact(bootloader),
                "partition_bytes": spec["bootloader_partition_bytes"],
                "free_bytes": spec["bootloader_partition_bytes"] - boot_bytes,
            },
            "linked_memory": idf_memory(root / spec["map"]),
        }
    return {
        "target": target,
        "project_input_manifest_sha256": input_manifest(target)["manifest_sha256"],
        "flash_bytes": spec["flash_bytes"],
        "partition_table": {
            "path": spec["partition"],
            "sha256": sha256(REPO_ROOT / spec["partition"]),
            "regions": partitions,
            "ends_at_flash_boundary": True,
        },
        "rollback": {
            "topology": "two equal OTA application slots plus OTA state",
            "slot_names": [row["name"] for row in ota],
            "slot_bytes": limits["slot_bytes"],
            "static_topology_proven": True,
            "ram_model_transition_proven": target == "s3",
            "flash_or_bootloader_transition_proven": False,
        },
        "external_ram": {
            "selected_bytes": spec["external_ram_bytes"],
            "target_configuration_present": True,
            "runtime_init_and_memory_test_proven": spec["external_ram_runtime_proven"],
        },
        "configurations": configurations,
    }


def parse_size_sections(elf: Path) -> list[dict]:
    result = subprocess.run(
        [str(ARM_SIZE), "-A", str(elf)],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"arm-none-eabi-size failed for {elf}:\n{result.stdout}")
    sections = []
    for line in result.stdout.splitlines():
        match = SIZE_ROW_RE.match(line)
        if match:
            sections.append(
                {
                    "name": match.group(1),
                    "bytes": int(match.group(2)),
                    "address": int(match.group(3)),
                }
            )
    return sections


def rp_target() -> dict:
    partitions_path = REPO_ROOT / "config/rp2354b_partitions.json"
    partitions = load(partitions_path)
    image_slots = [
        row for row in partitions["partitions"] if row["name"].startswith("Leshy2 RP image")
    ]
    limits = load_limits("rp2354b")
    if len(image_slots) != 2 or any(row["size"] != "896K" for row in image_slots):
        raise RuntimeError("RP A/B image partitions changed")
    partition_bytes = 8192 + sum(
        int(row["size"][:-1]) * 1024 for row in partitions["partitions"]
    )
    if partition_bytes != 2 * 1024 * 1024:
        raise RuntimeError("RP partition sequence does not end at the 2-MiB boundary")
    configurations: dict[str, dict] = {}
    for configuration in CONFIGURATIONS:
        root = REPO_ROOT / "build/targets/rp" / configuration
        image = root / "leshy2_rp.bin"
        elf = root / "leshy2_rp.elf"
        image_bytes = image.stat().st_size
        result = classify(image_bytes, limits)
        if result == "reject":
            raise RuntimeError(f"rp:{configuration}: application image rejected")
        sections = parse_size_sections(elf)
        ram_used = sum(
            row["bytes"]
            for row in sections
            if 0x20000000 <= row["address"] < 0x20082000
        )
        ram_total = 0x82000
        if ram_used > ram_total:
            raise RuntimeError(f"rp:{configuration}: static SRAM overflow")
        configurations[configuration] = {
            "application": artifact(image),
            "target_elf": artifact(elf),
            "map_sha256": sha256(root / "leshy2_rp.elf.map"),
            "image_gate": {
                "result": result,
                "slot_bytes": limits["slot_bytes"],
                "maximum_image_bytes": limits["maximum_image_bytes"],
                "free_before_maximum_bytes": limits["maximum_image_bytes"] - image_bytes,
                "free_in_slot_bytes": limits["slot_bytes"] - image_bytes,
            },
            "linked_memory": [
                {
                    "name": "main_and_scratch_sram",
                    "total_bytes": ram_total,
                    "used_or_reserved_bytes": ram_used,
                    "free_bytes": ram_total - ram_used,
                }
            ],
        }
    return {
        "target": "rp",
        "project_input_manifest_sha256": input_manifest("rp")["manifest_sha256"],
        "flash_bytes": 2 * 1024 * 1024,
        "partition_table": {
            "path": "config/rp2354b_partitions.json",
            "sha256": sha256(partitions_path),
            "image_slots": [row["name"] for row in image_slots],
            "slot_bytes": limits["slot_bytes"],
            "mirrored_data_partitions": ["Leshy2 RP data A", "Leshy2 RP data B"],
            "ends_at_flash_boundary": True,
        },
        "rollback": {
            "topology": "RP2350 A/B partitions with TBYB policy",
            "static_topology_proven": True,
            "ram_model_transition_proven": False,
            "flash_or_bootrom_transition_proven": False,
        },
        "configurations": configurations,
    }


def ti_memory(map_path: Path) -> dict[str, dict]:
    regions: dict[str, dict] = {}
    for line in map_path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = TI_MAP_RE.match(line)
        if match:
            name = match.group(1).lower()
            regions[name] = {
                "origin": int(match.group(2), 16),
                "total_bytes": int(match.group(3), 16),
                "used_bytes": int(match.group(4), 16),
                "free_bytes": int(match.group(5), 16),
            }
    if set(regions) != {"flash", "sram"}:
        raise RuntimeError(f"TI memory table incomplete: {map_path}")
    return regions


def ti_target(target: str) -> dict:
    memory_path = REPO_ROOT / "config/mspm0c1106_memory.json"
    memory = load(memory_path)
    application_slots = [
        row for row in memory["regions"] if row["name"] in {"application_a", "application_b"}
    ]
    if len(application_slots) != 2 or any(
        row["size"] != memory["slot_bytes"] for row in application_slots
    ):
        raise RuntimeError(f"{target}: controller A/B application slots changed")
    expected_offset = 0
    for region in memory["regions"]:
        if region["offset"] != expected_offset:
            raise RuntimeError(f"{target}: controller memory regions are not contiguous")
        expected_offset += region["size"]
    if expected_offset != memory["flash_bytes"]:
        raise RuntimeError(f"{target}: controller memory map does not end at flash boundary")
    configurations: dict[str, dict] = {}
    for configuration in CONFIGURATIONS:
        root = REPO_ROOT / "build/targets" / target / configuration
        app = root / f"leshy2_{target}.bin"
        boot = root / f"leshy2_{target}_boot.bin"
        app_map = root / f"leshy2_{target}.map"
        boot_map = root / f"leshy2_{target}_boot.map"
        app_bytes = app.stat().st_size
        result = classify(app_bytes, memory)
        if result == "reject":
            raise RuntimeError(f"{target}:{configuration}: application image rejected")
        configurations[configuration] = {
            "application": artifact(app),
            "boot_manager": artifact(boot),
            "application_map_sha256": sha256(app_map),
            "boot_map_sha256": sha256(boot_map),
            "image_gate": {
                "result": result,
                "slot_bytes": memory["slot_bytes"],
                "maximum_image_bytes": memory["maximum_image_bytes"],
                "free_before_maximum_bytes": memory["maximum_image_bytes"] - app_bytes,
                "free_in_slot_bytes": memory["slot_bytes"] - app_bytes,
            },
            "application_linked_memory": ti_memory(app_map),
            "boot_linked_memory": ti_memory(boot_map),
        }
    return {
        "target": target,
        "project_input_manifest_sha256": input_manifest(target)["manifest_sha256"],
        "flash_bytes": memory["flash_bytes"],
        "sram_bytes": memory["sram_bytes"],
        "memory_map": {
            "path": "config/mspm0c1106_memory.json",
            "sha256": sha256(memory_path),
            "regions": memory["regions"],
            "ends_at_flash_boundary": True,
        },
        "rollback": {
            "topology": "protected boot manager, equal application A/B slots and duplicated boot state",
            "static_topology_proven": True,
            "ram_model_transition_proven": False,
            "flash_or_boot_manager_transition_proven": False,
        },
        "configurations": configurations,
    }


def build_review() -> dict:
    f2_repro = REPO_ROOT / "config/f2_5_reproducibility_review.json"
    f3_runtime = REPO_ROOT / "config/f3_2_runtime_review.json"
    targets = [esp_target("s3"), esp_target("c5"), rp_target(), ti_target("pack"), ti_target("safety")]
    for target in targets:
        reviewed = load(REPO_ROOT / f"config/f2_4_{target['target']}_build_review.json")
        if reviewed["project_inputs"]["manifest_sha256"] != target["project_input_manifest_sha256"]:
            raise RuntimeError(f"{target['target']}: target-build input evidence is stale")
    if load(f2_repro).get("byte_identical_artifacts") != 52:
        raise RuntimeError("current all-target reproducibility evidence is incomplete")
    if load(f3_runtime).get("status") != "reviewed":
        raise RuntimeError("F3.2 runtime evidence is not reviewed")
    return {
        "schema_version": 1,
        "stage": "F3.3",
        "status": "reviewed",
        "scope": "current image, linked-memory, partition and rollback boundaries for five firmware targets",
        "inputs": {
            "reproducibility_evidence": {
                "path": "config/f2_5_reproducibility_review.json",
                "sha256": sha256(f2_repro),
            },
            "runtime_evidence": {
                "path": "config/f3_2_runtime_review.json",
                "sha256": sha256(f3_runtime),
            },
        },
        "targets": targets,
        "totals": {
            "targets": 5,
            "configurations": 10,
            "byte_reproducible_artifacts": 52,
            "image_gates_passed": 10,
            "static_rollback_topologies": 5,
            "physical_rollback_transitions": 0,
        },
        "claims": {
            "current_target_inputs_match_build_evidence": True,
            "all_current_artifacts_are_byte_reproducible": True,
            "all_image_and_linked_memory_gates_pass": True,
            "all_five_static_rollback_topologies_fit": True,
            "s3_8m_psram_runtime_init_and_test_passed": True,
            "nonvolatile_fault_retention_proven": False,
            "physical_flash_or_rollback_transition_proven": False,
            "physical_board_proven": False,
        },
        "deferred_to_hil": [
            "C5 external-PSRAM initialization and memory test",
            "nonvolatile retained-fault write/read across power loss",
            "signed image flash readback on every domain",
            "pending-slot boot, confirmation, deadline and rollback on every domain",
            "brownout during each flash and boot-state mutation",
            "physical watchdog, FAULT_KILL and peripheral timing",
        ],
        "next": "F3.4",
        "runner": "tools/review_f3_3_boundaries.py",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        review = build_review()
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    serialized = json.dumps(review, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        OUTPUT_PATH.write_text(serialized, encoding="utf-8")
    elif not OUTPUT_PATH.is_file() or OUTPUT_PATH.read_text(encoding="utf-8") != serialized:
        print("ERROR: F3.3 boundary evidence is stale", file=sys.stderr)
        return 1
    print(
        "F3.3 boundary review OK: 5 targets, 10 image/RAM gates, "
        "5 static rollback topologies, 0 physical transitions claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
