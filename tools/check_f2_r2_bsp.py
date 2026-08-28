#!/usr/bin/env python3
"""Review deterministic F2-R2.3 generation and one-owner SDK consumption."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET_IDS = ["s3", "c5", "rf_rp", "hub_rp", "pack", "safety"]
MAPPING_COUNTS = {
    "s3": ("exact_pins", 33, 0),
    "c5": ("partial_exact_pins", 6, 0),
    "rf_rp": ("exact_pins", 48, 0),
    "hub_rp": ("exact_pins", 48, 0),
    "pack": ("identity_only", 0, 0),
    "safety": ("identity_only", 0, 0),
}


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    model = load("config/f2_r2_bsp_generation.json")
    consumption = load("config/f2_r2_bsp_consumption.json")
    projects = load("config/f2_r2_target_projects.json")
    manifest = load("generated/r2/source_manifest.json")

    if model.get("stage") != "F2-R2.3" or model.get("status") != "reviewed_generated_boundary":
        errors.append("F2-R2.3 generation model is not reviewed")
    source = model.get("source", {})
    source_path = ROOT / source.get("path", "")
    if not source_path.is_file() or digest(source_path) != source.get("sha256"):
        errors.append("F2-R2.3 source projection is missing or hash-stale")
    if source.get("hardware_marker") != "H1-R2.31":
        errors.append("F2-R2.3 is not bound to H1-R2.31")
    if [row.get("id") for row in model.get("domains", [])] != TARGET_IDS:
        errors.append("generation model does not contain the exact six domains")
    for row in model.get("domains", []):
        expected = MAPPING_COUNTS.get(row.get("id"), (None, None, None))[0]
        if row.get("mapping") != expected:
            errors.append(f"{row.get('id')}: mapping completeness changed")

    boundary = model.get("contract_boundary", {})
    expected_boundary = {
        "exact_gpio_assignments_are_generated_only_when_explicit_in_source": True,
        "c5_partial_map_contains_only_official_fixed_sdio_contacts": True,
        "dual_rp_exact_maps_are_pre_h2_working_authority": True,
        "identity_only_domains_do_not_claim_unpublished_pin_assignments": True,
        "handwritten_production_pins_allowed": False,
        "historical_r1_tree_is_r2_input": False,
    }
    if boundary != expected_boundary:
        errors.append("F2-R2.3 honest mapping boundary changed")
    execution = model.get("execution", {})
    if execution != {
        "generator_run": True,
        "host_syntax_check": True,
        "target_configure_run": False,
        "target_build_run": False,
        "emulator_run": False,
        "devboard_run": False,
        "physical_run": False,
    }:
        errors.append("F2-R2.3 execution claims changed")
    if model.get("next") != "F2-R2.4":
        errors.append("F2-R2.3 does not advance exactly to F2-R2.4")

    generated = subprocess.run(
        (sys.executable, "tools/generate_f2_r2_bsp.py", "--check"),
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if generated.returncode != 0:
        errors.append(f"generated R2 BSP is stale: {generated.stdout.strip()}")

    if manifest.get("stage") != "F2-R2.3" or manifest.get("status") != "generated":
        errors.append("generated R2 manifest stage/status changed")
    if manifest.get("source") != source:
        errors.append("generated R2 manifest lost its hash-bound source")
    inventory = manifest.get("domains", [])
    if [row.get("id") for row in inventory] != TARGET_IDS:
        errors.append("generated R2 manifest does not have six ordered domains")
    for row in inventory:
        expected = MAPPING_COUNTS.get(row.get("id"))
        actual = (row.get("mapping"), row.get("pins"), row.get("groups"))
        if actual != expected:
            errors.append(f"{row.get('id')}: generated mapping/count differs: {actual!r}")
    if len(manifest.get("files", [])) != 13:
        errors.append("R2 manifest must cover 13 generated C/header files")

    include_root = ROOT / model["outputs"]["include_root"]
    sources = [ROOT / row["source"] for row in inventory]
    with tempfile.TemporaryDirectory(prefix="leshy2-r2-bsp-") as temporary:
        output_root = Path(temporary)
        command = [
            os.environ.get("CC", "cc"),
            "-std=c17",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Wconversion",
            "-Wpedantic",
            "-fsyntax-only",
            f"-I{include_root}",
            *[str(path) for path in sources],
        ]
        syntax = subprocess.run(
            command,
            cwd=output_root,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    if syntax.returncode != 0:
        errors.append(f"generated R2 C17 syntax check failed: {syntax.stdout.strip()}")

    if consumption.get("stage") != "F2-R2.3" or consumption.get("status") != "reviewed":
        errors.append("F2-R2.3 consumption contract is not reviewed")
    rows = consumption.get("projects", [])
    if [row.get("id") for row in rows] != TARGET_IDS:
        errors.append("consumption contract is not the exact six-project order")
    registered = {row["id"]: row for row in projects.get("projects", [])}
    assigned_sources: list[str] = []
    for row in rows:
        target_id = row.get("id")
        if row.get("domain") != target_id or registered.get(target_id, {}).get("r2_bsp_domain") != target_id:
            errors.append(f"{target_id}: project/domain ownership differs")
        build_path = ROOT / row.get("build_input", "")
        entry_path = ROOT / row.get("entrypoint", "")
        if not build_path.is_file() or not entry_path.is_file():
            errors.append(f"{target_id}: build input or entrypoint missing")
            continue
        build = build_path.read_text(encoding="utf-8")
        entry = entry_path.read_text(encoding="utf-8")
        source_name = Path(row["source"]).name
        if build.count(source_name) != 1:
            errors.append(f"{target_id}: generated source is not present exactly once")
        if "generated/r2/hardware" not in build and "generated/r2/hardware" not in str(build_path):
            if "generated/r2/hardware" not in build.replace("${LESHY2_REPO_ROOT}/", ""):
                # Relative CMake/Make paths still must carry the unique r2/hardware suffix.
                if "generated/r2/hardware" not in build:
                    errors.append(f"{target_id}: generated R2 include/source root is absent")
        if "generated/hardware" in build:
            errors.append(f"{target_id}: historical R1 generated tree is an active input")
        if f'#include "{row["header"]}"' not in entry:
            errors.append(f"{target_id}: entrypoint does not include its generated R2 header")
        if row["symbol"] not in entry:
            errors.append(f"{target_id}: entrypoint does not consume its domain descriptor")
        if target_id in {"rf_rp", "hub_rp"}:
            if "L2_R2_MAPPING_EXACT_PINS" not in entry:
                errors.append(f"{target_id}: entrypoint does not enforce exact-pin mapping")
            if "pin_count != UINT8_C(48)" not in entry:
                errors.append(f"{target_id}: entrypoint does not enforce the complete 48-GPIO map")
        for foreign in set(TARGET_IDS) - {target_id}:
            if f"{foreign}_bsp.c" in build:
                errors.append(f"{target_id}: foreign R2 domain source is an active input")
        assigned_sources.append(row["source"])
    if len(assigned_sources) != len(set(assigned_sources)):
        errors.append("one generated R2 source is assigned to multiple projects")

    # ESP-IDF discovers component directories independently of link references.
    # Keep the obsolete R1 point-to-point S3/C5 endpoint sources outside the
    # active R2 component set rather than merely leaving them unreferenced by main.
    s3_root = (ROOT / "targets/s3/CMakeLists.txt").read_text(encoding="utf-8")
    c5_root = (ROOT / "targets/c5/CMakeLists.txt").read_text(encoding="utf-8")
    s3_boundary = (
        ROOT / "targets/s3/components/leshy2_s3_c5/CMakeLists.txt"
    ).read_text(encoding="utf-8")
    if "set(COMPONENTS main leshy2_portable leshy2_s3_c5)" not in s3_root:
        errors.append("s3: active R2 component set is not explicit")
    if "set(COMPONENTS main leshy2_portable)" not in c5_root:
        errors.append("c5: obsolete R1 endpoint component is not excluded")
    c5_main = (ROOT / "targets/c5/main/CMakeLists.txt").read_text(encoding="utf-8")
    if "leshy2_s3_c5" in c5_main:
        errors.append("c5: main still requires the obsolete R1 endpoint component")
    if "s3_c5_host.c" in s3_boundary:
        errors.append("s3: obsolete R1 physical endpoint remains active")

    active_build_inputs = [
        "targets/s3/CMakeLists.txt",
        "targets/s3/main/CMakeLists.txt",
        "targets/s3/components/leshy2_portable/CMakeLists.txt",
        "targets/s3/components/leshy2_s3_c5/CMakeLists.txt",
        "targets/c5/CMakeLists.txt",
        "targets/c5/main/CMakeLists.txt",
        "targets/c5/components/leshy2_portable/CMakeLists.txt",
        "targets/rf_rp/CMakeLists.txt",
        "targets/hub_rp/CMakeLists.txt",
        "targets/pack/Makefile",
        "targets/safety/Makefile",
    ]
    for relative in active_build_inputs:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if "generated/hardware" in text or "leshy2/hardware/" in text:
            errors.append(f"{relative}: active build still admits historical R1 BSP")

    copied = [
        path
        for target_id in TARGET_IDS
        for path in (ROOT / "targets" / target_id).rglob("*_bsp.[ch]")
    ]
    if copied:
        errors.append(f"generated R2 BSP files were copied into targets: {copied}")

    if consumption.get("claims") != {
        "one_generated_domain_per_project": True,
        "historical_r1_bsp_is_active_input": False,
        "generated_sources_copied_into_targets": False,
        "handwritten_production_pins": False,
        "target_configure_run": False,
        "target_build_run": False,
    }:
        errors.append("F2-R2.3 consumption claims changed")
    if consumption.get("next") != "F2-R2.4":
        errors.append("consumption contract skips F2-R2.4")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "F2-R2.3 BSP OK: 6 deterministic H1-R2.31 domains, "
        "6 unique SDK owners, C17 host syntax; 0 target configure/build runs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
