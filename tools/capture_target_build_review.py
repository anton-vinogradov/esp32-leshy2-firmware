#!/usr/bin/env python3
"""Capture deterministic evidence for one completed F2.4 target build."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from check_image_size import classify, load_limits


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = REPO_ROOT / "config/build_matrix.json"
STAGES = {
    "s3": ("F2.4.1", "F2.4.2"),
    "c5": ("F2.4.2", "F2.4.3"),
    "rp": ("F2.4.3", "F2.4.4"),
    "pack": ("F2.4.4", "F2.4.5"),
    "safety": ("F2.4.5", "F2.4.6"),
}
LIMIT_INPUTS = {
    "s3": "s3_image_limits.json",
    "c5": "c5_image_limits.json",
    "rp": "rp2354b_image_limits.json",
    "pack": "mspm0c1106_memory.json",
    "safety": "mspm0c1106_memory.json",
}
ESP_BOOTLOADER_PARTITION_BYTES = {
    "s3": 32768,
    "c5": 24576,
}
BOOTLOADER_MARGIN_WARNING_BYTES = 4096


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def artifact_record(build_root: Path, relative: str) -> dict[str, int | str]:
    path = build_root / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def input_paths(target_id: str) -> list[Path]:
    domain = "rp" if target_id == "rp" else target_id
    candidates = [
        REPO_ROOT / "config/build_matrix.json",
        REPO_ROOT / "config/build_policy.json",
        REPO_ROOT / "config" / LIMIT_INPUTS[target_id],
        REPO_ROOT / "generated/hardware/include/leshy2/hardware" / f"{domain}_bsp.h",
        REPO_ROOT / "generated/hardware/src" / f"{domain}_bsp.c",
    ]
    candidates.extend((REPO_ROOT / "common").rglob("*"))
    candidates.extend((REPO_ROOT / "targets" / target_id).rglob("*"))
    if target_id in {"pack", "safety"}:
        candidates.append(REPO_ROOT / "tools" / "normalize_ti_map.py")
    return sorted({path for path in candidates if path.is_file()})


def input_manifest(target_id: str) -> dict[str, object]:
    records = [
        {
            "path": str(path.relative_to(REPO_ROOT)),
            "sha256": sha256(path),
        }
        for path in input_paths(target_id)
    ]
    manifest = hashlib.sha256()
    for record in records:
        manifest.update(record["path"].encode("utf-8"))
        manifest.update(b"\0")
        manifest.update(record["sha256"].encode("ascii"))
        manifest.update(b"\n")
    return {
        "files": records,
        "manifest_sha256": manifest.hexdigest(),
    }


def capture(target_id: str) -> dict[str, object]:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    target = next(row for row in matrix["targets"] if row["id"] == target_id)
    stage, next_stage = STAGES[target_id]
    configurations: dict[str, object] = {}
    for configuration in ("debug", "release"):
        build_root = REPO_ROOT / "build/targets" / target_id / configuration
        artifacts = [
            artifact_record(build_root, relative) for relative in target["artifacts"]
        ]
        image_relative = target["size_gate"]["image"]
        image_path = build_root / image_relative
        limits = load_limits(target["size_gate"]["target"])
        image_size = image_path.stat().st_size
        gate_result = classify(image_size, limits)
        if gate_result == "reject":
            raise RuntimeError(f"{target_id}:{configuration}: image-size gate rejected")
        configurations[configuration] = {
            "status": "passed",
            "artifacts": artifacts,
            "image_gate": {
                "image": str(image_path.relative_to(REPO_ROOT)),
                "size_bytes": image_size,
                "result": gate_result,
                "warning_bytes": limits["warning_bytes"],
                "maximum_image_bytes": limits["maximum_image_bytes"],
                "slot_bytes": limits["slot_bytes"],
            },
        }
        if target_id in ESP_BOOTLOADER_PARTITION_BYTES:
            bootloader_size = (build_root / "bootloader/bootloader.bin").stat().st_size
            partition_size = ESP_BOOTLOADER_PARTITION_BYTES[target_id]
            free_bytes = partition_size - bootloader_size
            if free_bytes < 0:
                raise RuntimeError(
                    f"{target_id}:{configuration}: bootloader exceeds partition"
                )
            configurations[configuration]["bootloader_margin"] = {
                "partition_bytes": partition_size,
                "image_bytes": bootloader_size,
                "free_bytes": free_bytes,
                "warning_below_bytes": BOOTLOADER_MARGIN_WARNING_BYTES,
                "result": "watch"
                if free_bytes < BOOTLOADER_MARGIN_WARNING_BYTES
                else "ok",
            }
    return {
        "schema_version": 1,
        "stage": stage,
        "status": "reviewed",
        "target": target_id,
        "sdk_target": target["sdk_target"],
        "family": target["family"],
        "configurations": configurations,
        "project_inputs": input_manifest(target_id),
        "execution": {
            "configure_runs": 2,
            "build_runs": 2,
            "artifact_verify_runs": 2,
            "emulator_runs": 0,
            "hardware_runs": 0,
            "network_during_configure_or_build": False,
        },
        "claims": {
            "target_compilation_and_link_passed": True,
            "all_declared_artifacts_present": True,
            "image_size_gate_passed": True,
            "runtime_boot_proven": False,
            "byte_reproducibility_proven": False,
        },
        "next": next_stage,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=tuple(STAGES), required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = REPO_ROOT / "config" / f"f2_4_{args.target}_build_review.json"
    try:
        result = capture(args.target)
    except (FileNotFoundError, RuntimeError, StopIteration) as error:
        print(f"ERROR: {error}")
        return 1
    serialized = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        output.write_text(serialized, encoding="utf-8")
    elif not output.is_file() or output.read_text(encoding="utf-8") != serialized:
        print(f"ERROR: stale target-build evidence: {output}")
        return 1
    print(
        f"{result['stage']} target-build review OK: {args.target} debug/release, "
        f"{sum(len(row['artifacts']) for row in result['configurations'].values())} artifacts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
