#!/usr/bin/env python3
"""Fail closed if the reviewed six-target R2 identity contract drifts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config" / "f0_r2_target_identity_contract.json"
HARDWARE_PATH = ROOT / "config" / "h0_r2_hardware_contract.json"


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    hardware = json.loads(HARDWARE_PATH.read_text(encoding="utf-8"))

    if contract.get("stage") != "F0-R2.1" or contract.get("status") != "reviewed_contract":
        return fail("target identity contract is not reviewed at F0-R2.1")
    if contract.get("configurations") != ["debug", "release"]:
        return fail("the canonical debug/release configurations changed")

    hardware_domains = {row["id"]: row for row in hardware.get("domains", [])}
    targets = contract.get("targets", [])
    target_by_id = {row["id"]: row for row in targets}
    expected_ids = {"s3", "c5", "rf_rp", "hub_rp", "pack", "safety"}
    if len(targets) != 6 or set(target_by_id) != expected_ids:
        return fail("target contract must contain exactly the six R2 hardware domains")
    if set(hardware_domains) != expected_ids:
        return fail("projected hardware contract does not contain the same six domains")

    identities: set[tuple[str, str]] = set()
    application_images: set[str] = set()
    boot_images: set[str] = set()
    for target_id in sorted(expected_ids):
        target = target_by_id[target_id]
        hardware_domain = hardware_domains[target_id]
        if target.get("hardware_domain") != target_id:
            return fail(f"{target_id}: hardware domain is not one-to-one")
        if target.get("mpn") != hardware_domain.get("mpn"):
            return fail(f"{target_id}: MPN differs from the H0-R2 projection")
        if target.get("r2_project_created") is not False or target.get("r2_build_run") is not False:
            return fail(f"{target_id}: F0-R2.1 cannot claim project creation or a target build")
        identity = (target.get("project_name", ""), target.get("project_dir", ""))
        if not all(identity) or identity in identities:
            return fail(f"{target_id}: project identity is missing or duplicated")
        identities.add(identity)
        image = target.get("application_image", "")
        if not image or image in application_images:
            return fail(f"{target_id}: application image identity is missing or duplicated")
        application_images.add(image)
        if "boot_image" in target:
            boot_image = target["boot_image"]
            if not boot_image or boot_image in boot_images:
                return fail(f"{target_id}: boot image identity is missing or duplicated")
            boot_images.add(boot_image)

    for rp_id in ("rf_rp", "hub_rp"):
        target = target_by_id[rp_id]
        if target.get("family") != "pico_sdk" or target.get("sdk_target") != "rp2350-arm-s":
            return fail(f"{rp_id}: RP2354B SDK identity changed")
    for target_id in ("pack", "safety"):
        target = target_by_id[target_id]
        if target.get("family") != "ti_mspm0_sdk" or target.get("sdk_target") != "MSPM0C1106":
            return fail(f"{target_id}: MSPM0 SDK identity changed")

    claims = contract.get("claims", {})
    expected_claims = {
        "target_identities_reviewed": True,
        "target_count": 6,
        "application_image_count": 6,
        "boot_image_count": 2,
        "new_project_identities": ["rf_rp", "hub_rp"],
        "r1_target_build_evidence_is_historical_only": True,
        "r2_target_projects_created": False,
        "r2_target_builds_run": False,
        "memory_or_partition_layout_reviewed_here": False,
        "update_activation_order_reviewed_here": False,
        "emulator_or_devboard_gate_reviewed_here": False,
    }
    if claims != expected_claims:
        return fail("F0-R2.1 claims changed or overstate the reviewed scope")

    print(
        "F0-R2.1 target identity contract OK: 6 application images, "
        "2 protected-controller boot images; 0 R2 projects and 0 R2 builds claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
