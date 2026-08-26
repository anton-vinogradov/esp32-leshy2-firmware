#!/usr/bin/env python3
"""Fail-closed review of the F4.1.0 vendored-source boundary."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from vendor_essl import check_vendor


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "config" / "f4_1_s3_c5_source_boundary.json"
SOURCE_LAYOUT_PATH = REPO_ROOT / "config" / "source_layout.json"
S3_CMAKE_PATH = REPO_ROOT / "targets" / "s3" / "CMakeLists.txt"


def main() -> int:
    errors = check_vendor()
    boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
    layout = json.loads(SOURCE_LAYOUT_PATH.read_text(encoding="utf-8"))
    if boundary.get("stage") != "F4.1.0" or boundary.get("status") != "reviewed":
        errors.append("F4.1.0 source boundary is not reviewed")
    vendor = boundary.get("vendor", {})
    if vendor.get("component") != "espressif/esp_serial_slave_link":
        errors.append("F4.1.0 vendor component changed")
    if vendor.get("version") != "1.1.2" or vendor.get("files") != 30:
        errors.append("F4.1.0 ESSL version or file count changed")
    if vendor.get("canonical_payload_sha256") != "9f217846a90d97a4897350b0c8cfafd4bbe1a2dd8af5619fd3463ea9dbe36053":
        errors.append("F4.1.0 ESSL payload hash changed")
    if vendor.get("component_manager_enabled"):
        errors.append("F4.1.0 may not enable Registry resolution")
    if 'set(ENV{IDF_COMPONENT_MANAGER} "0")' not in S3_CMAKE_PATH.read_text(encoding="utf-8"):
        errors.append("S3 target no longer disables Component Manager")

    ownership = {row["owner"]: row for row in boundary.get("source_ownership", [])}
    if set(ownership) != {"portable_core", "s3_target_adapter", "c5_target_adapter"}:
        errors.append("F4.1 source ownership set changed")
    if ownership.get("portable_core", {}).get("introduced_at") != "F4.1.1":
        errors.append("portable high-speed implementation boundary changed")
    for owner in ("s3_target_adapter", "c5_target_adapter"):
        if ownership.get(owner, {}).get("introduced_at") != "F4.1.2":
            errors.append(f"{owner} implementation boundary changed")

    vendor_areas = [
        area for area in layout.get("areas", []) if area.get("owner") == "upstream_vendor_import"
    ]
    if len(vendor_areas) != 1:
        errors.append("source layout must contain one upstream vendor area")
    elif vendor_areas[0].get("producer") != "tools/vendor_essl.py":
        errors.append("ESSL vendor area producer changed")

    expected_counts = {
        "vendored_files": 30,
        "implemented_adapter_files": 0,
        "target_adapter_builds": 0,
        "qemu_fake_runs": 0,
        "physical_transport_runs": 0,
    }
    if boundary.get("counts") != expected_counts:
        errors.append("F4.1.0 reviewed counts changed")
    if boundary.get("build_boundary", {}).get("current_target_build_claim"):
        errors.append("F4.1.0 may not claim a target adapter build")
    if boundary.get("next") != "F4.1.1":
        errors.append("F4.1.0 next marker changed")
    if any(boundary.get("authorization", {}).values()):
        errors.append("F4.1.0 may not authorize hardware work")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        "F4.1.0 source boundary OK: exact offline ESSL 1.1.2, 30 files, "
        "3 single-owner adapter areas, 0 build/PHY claims"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
