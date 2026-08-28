#!/usr/bin/env python3
"""Review six F2-R2.2 SDK project trees without claiming BSP or execution."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "config" / "f2_r2_target_projects.json"
TARGET_IDS = ["s3", "c5", "rf_rp", "hub_rp", "pack", "safety"]
R2_DOMAINS = TARGET_IDS
R1_GENERATED_DOMAINS = ["S3", "C5", "RP", "PACK", "SAFETY"]
NEW_RP_FILES = {
    "rf_rp": {
        "targets/rf_rp/CMakeLists.txt",
        "targets/rf_rp/boards/leshy2_rp2354b.h",
        "targets/rf_rp/main.c",
    },
    "hub_rp": {
        "targets/hub_rp/CMakeLists.txt",
        "targets/hub_rp/boards/leshy2_rp2354b.h",
        "targets/hub_rp/main.c",
    },
}
PIN_RE = re.compile(r"\b(?:GPIO(?:_NUM_)?\d+|PIN_[A-Z0-9_]+)\b")


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def main() -> int:
    review = load("config/f2_r2_target_projects.json")
    errors: list[str] = []
    if review.get("stage") != "F2-R2.2" or review.get("status") != "reviewed_structure":
        errors.append("F2-R2.2 project-tree structure is not reviewed")

    for locked in review.get("inputs", {}).values():
        path = ROOT / locked.get("path", "")
        if not path.is_file():
            errors.append(f"missing locked input: {locked.get('path')}")
        elif digest(path) != locked.get("sha256"):
            errors.append(f"stale locked input: {locked.get('path')}")

    identities = load("config/f0_r2_target_identity_contract.json")
    matrix = load("config/f2_r2_build_matrix.json")
    hardware = load("config/h0_r2_hardware_contract.json")
    identity_rows = identities.get("targets", [])
    matrix_rows = matrix.get("targets", [])
    project_rows = review.get("projects", [])
    if [row.get("id") for row in identity_rows] != TARGET_IDS:
        errors.append("target-identity order is not the exact six-domain order")
    if [row.get("id") for row in matrix_rows] != TARGET_IDS:
        errors.append("build-matrix order is not the exact six-domain order")
    if [row.get("id") for row in project_rows] != TARGET_IDS:
        errors.append("project-tree review is not the exact six-domain order")
    if [row.get("id") for row in hardware.get("domains", [])] != R2_DOMAINS:
        errors.append("current hardware projection is not the six-domain R2 contract")

    identity_by_id = {row["id"]: row for row in identity_rows}
    matrix_by_id = {row["id"]: row for row in matrix_rows}
    projects = {row["id"]: row for row in project_rows}
    for target_id in TARGET_IDS:
        actual = projects.get(target_id, {})
        identity = identity_by_id.get(target_id, {})
        matrix_target = matrix_by_id.get(target_id, {})
        for field in (
            "family",
            "sdk_target",
            "project_dir",
            "project_name",
        ):
            expected = identity.get(field)
            if actual.get(field) != expected or matrix_target.get(field) != expected:
                errors.append(f"{target_id}: {field} differs across identity/matrix/project review")
        if actual.get("application_image") != identity.get("application_image"):
            errors.append(f"{target_id}: application image differs from the identity contract")
        if actual.get("r2_bsp_domain") != target_id:
            errors.append(f"{target_id}: R2 BSP owner differs from target identity")
        if actual.get("r2_bsp_binding") != "pending_F2-R2.3":
            errors.append(f"{target_id}: BSP binding skips the F2-R2.3 gate")
        if actual.get("configure_or_build_eligible") is not False:
            errors.append(f"{target_id}: project is build-eligible before the generated R2 BSP")
        if matrix_target.get("execution_gate", {}).get("target_build") != "not_run_until_F2-R2.4":
            errors.append(f"{target_id}: matrix build gate is not fail-closed through F2-R2.3")

        project_dir = ROOT / actual.get("project_dir", "")
        identity_file = ROOT / actual.get("identity_file", "")
        entry_file = ROOT / actual.get("entry_file", "")
        if not project_dir.is_dir() or project_dir.is_symlink():
            errors.append(f"{target_id}: project root is missing or aliased")
        if not identity_file.is_file() or not entry_file.is_file():
            errors.append(f"{target_id}: identity or entry file is missing")
            continue
        build_text = identity_file.read_text(encoding="utf-8")
        if target_id in {"s3", "c5", "rf_rp", "hub_rp"}:
            if f"project({actual['project_name']}" not in build_text:
                errors.append(f"{target_id}: production-SDK project identity is absent")
        else:
            for image in (actual["application_image"], actual.get("boot_image")):
                if image and image not in build_text:
                    errors.append(f"{target_id}: output identity {image} is absent")

    boundary = review.get("bsp_boundary", {})
    if boundary.get("current_contract") != "config/h0_r2_hardware_contract.json":
        errors.append("project boundary is not tied to the current R2 hardware projection")
    if boundary.get("current_domains") != R2_DOMAINS:
        errors.append("project boundary does not name all six R2 domains")
    if boundary.get("generated_r2_bsp_status") != "pending_F2-R2.3":
        errors.append("generated R2 BSP was claimed before F2-R2.3")
    if boundary.get("historical_generated_tree_is_r2_build_input") is not False:
        errors.append("historical five-domain BSP is admitted as an R2 build input")
    if boundary.get("handwritten_production_pins_allowed") is not False:
        errors.append("handwritten production pins are allowed")

    old_manifest = load("generated/source_manifest.json")
    old_domains: list[str] = []
    for row in old_manifest.get("files", []):
        domain = row.get("domain")
        if domain != "COMMON" and domain not in old_domains:
            old_domains.append(domain)
    if old_manifest.get("source_contract") != "config/hardware_bsp_contract.json":
        errors.append("historical generated BSP no longer identifies its R1 source")
    if set(old_domains) != set(R1_GENERATED_DOMAINS):
        errors.append("historical generated BSP inventory changed unexpectedly")

    for target_id, expected_files in NEW_RP_FILES.items():
        project_root = ROOT / "targets" / target_id
        actual_files = {
            str(path.relative_to(ROOT))
            for path in project_root.rglob("*")
            if path.is_file()
        }
        if actual_files != expected_files:
            errors.append(
                f"{target_id}: minimal tree mismatch: "
                f"missing={sorted(expected_files - actual_files)}, "
                f"extra={sorted(actual_files - expected_files)}"
            )
        combined = "\n".join(source(relative) for relative in sorted(expected_files))
        required = (
            "PICO_SDK_FETCH_FROM_GIT OFF",
            "FETCHCONTENT_FULLY_DISCONNECTED ON",
            "PICO_BOARD_HEADER_DIRS",
            "pico_sdk_init()",
            f"project(leshy2_{target_id} C CXX ASM)",
            f"add_executable(leshy2_{target_id} main.c)",
            f"pico_add_extra_outputs(leshy2_{target_id})",
            "PICO_PLATFORM, rp2350-arm-s",
            "PICO_FLASH_SIZE_BYTES, (2 * 1024 * 1024)",
        )
        for token in required:
            if token not in combined:
                errors.append(f"{target_id}: missing production-SDK token {token!r}")
        for forbidden in (
            "generated/hardware",
            "rp_bsp",
            "leshy2/hardware/",
            "targets/rp",
        ):
            if forbidden in combined:
                errors.append(f"{target_id}: consumes forbidden R1/shared source {forbidden!r}")
        if PIN_RE.search(combined):
            errors.append(f"{target_id}: contains a handwritten production pin")
        symbol = projects[target_id].get("image_identity_symbol", "")
        if not symbol or symbol not in source(projects[target_id]["entry_file"]):
            errors.append(f"{target_id}: independent image identity is absent")

    rf = projects.get("rf_rp", {})
    hub = projects.get("hub_rp", {})
    for key in ("project_dir", "project_name", "application_image", "entry_file", "image_identity_symbol"):
        if rf.get(key) == hub.get(key):
            errors.append(f"RF-RP and Hub-RP share {key}")
    if (ROOT / rf.get("entry_file", "")).read_bytes() == (ROOT / hub.get("entry_file", "")).read_bytes():
        errors.append("RF-RP and Hub-RP entry sources are byte-identical")

    claims = review.get("claims", {})
    expected_claims = {
        "six_production_sdk_project_roots_reviewed": True,
        "retained_sdk_project_roots": 4,
        "new_independent_sdk_project_roots": 2,
        "independent_application_image_identities": 6,
        "independent_protected_boot_image_identities": 2,
        "rf_and_hub_share_project_tree": False,
        "rf_and_hub_share_entry_source": False,
        "rf_and_hub_share_application_image": False,
        "rf_and_hub_share_target_local_state": False,
        "r2_bsp_generated": False,
        "r2_bsp_consumed": False,
        "r2_configure_run": False,
        "r2_build_run": False,
        "r2_emulator_run": False,
        "r2_devboard_run": False,
        "r2_physical_run": False,
    }
    if claims != expected_claims:
        errors.append("F2-R2.2 claim boundary changed")
    if review.get("next") != "F2-R2.3":
        errors.append("F2-R2.2 does not advance exactly to F2-R2.3")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "F2-R2.2 target projects OK: 6 production-SDK roots, "
        "2 independent RP trees, 0 BSP/configure/build/execution claims"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
