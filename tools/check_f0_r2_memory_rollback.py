#!/usr/bin/env python3
"""Check the six-domain R2 memory and local rollback ownership contract."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config" / "f0_r2_memory_rollback_contract.json"
IDENTITY_PATH = ROOT / "config" / "f0_r2_target_identity_contract.json"


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def esp_partitions(relative: str) -> dict[str, tuple[int, int]]:
    rows: dict[str, tuple[int, int]] = {}
    with (ROOT / relative).open(encoding="utf-8", newline="") as handle:
        for row in csv.reader(line for line in handle if not line.lstrip().startswith("#")):
            if not row:
                continue
            name = row[0].strip()
            rows[name] = (int(row[3].strip(), 0), int(row[4].strip(), 0))
    return rows


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    identities = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
    if contract.get("stage") != "F0-R2.2" or contract.get("status") != "reviewed_contract":
        return fail("memory contract is not reviewed at F0-R2.2")

    target_rows = contract.get("targets", [])
    targets = {row["id"]: row for row in target_rows}
    identity_ids = {row["id"] for row in identities.get("targets", [])}
    if len(target_rows) != 6 or set(targets) != identity_ids:
        return fail("memory ownership is not one-to-one with the six target identities")

    for target_id in ("s3", "c5"):
        target = targets[target_id]
        partitions = esp_partitions(target["partition_source"])
        expected_slots = target["rollback_slots"]
        if any(slot not in partitions for slot in expected_slots):
            return fail(f"{target_id}: an OTA slot is absent from the partition source")
        for slot in expected_slots:
            if partitions[slot][1] != target["slot_bytes"]:
                return fail(f"{target_id}: slot geometry differs from the contract")
        last_end = max(offset + size for offset, size in partitions.values())
        if last_end != target["flash_bytes"]:
            return fail(f"{target_id}: partition source does not close exact flash capacity")
        limits = json.loads((ROOT / target["image_limit_source"]).read_text(encoding="utf-8"))
        if limits["slot_bytes"] != target["slot_bytes"] or limits["maximum_image_bytes"] != target["maximum_image_bytes"]:
            return fail(f"{target_id}: image limit differs from slot contract")

    rp_partitions = json.loads((ROOT / "config/rp2354b_partitions.json").read_text(encoding="utf-8"))
    rp_images = {
        row["name"]: int(row["size"][:-1]) * 1024
        for row in rp_partitions["partitions"]
        if row["name"].startswith("Leshy2 RP image")
    }
    rp_total = 8192 + sum(int(row["size"][:-1]) * 1024 for row in rp_partitions["partitions"])
    rp_limits = json.loads((ROOT / "config/rp2354b_image_limits.json").read_text(encoding="utf-8"))
    if rp_total != 2097152 or set(rp_images) != {"Leshy2 RP image A", "Leshy2 RP image B"}:
        return fail("RP2354B partition geometry changed")
    for target_id in ("rf_rp", "hub_rp"):
        target = targets[target_id]
        if any(rp_images[slot] != target["slot_bytes"] for slot in target["rollback_slots"]):
            return fail(f"{target_id}: RP slot geometry differs")
        if rp_limits["maximum_image_bytes"] != target["maximum_image_bytes"]:
            return fail(f"{target_id}: RP image limit differs")

    msp = json.loads((ROOT / "config/mspm0c1106_memory.json").read_text(encoding="utf-8"))
    regions = {row["name"]: row for row in msp["regions"]}
    if sum(row["size"] for row in msp["regions"]) != msp["flash_bytes"]:
        return fail("MSPM0 regions do not close exact flash capacity")
    for target_id in ("pack", "safety"):
        target = targets[target_id]
        if any(regions[slot]["size"] != target["slot_bytes"] for slot in target["rollback_slots"]):
            return fail(f"{target_id}: MSPM0 slot geometry differs")
        if msp["maximum_image_bytes"] != target["maximum_image_bytes"]:
            return fail(f"{target_id}: MSPM0 image limit differs")

    if len({targets[row]["rollback_owner"] for row in targets}) != 6:
        return fail("every target must name an independent local rollback owner")
    claims = contract.get("claims", {})
    expected_claims = {
        "memory_and_rollback_ownership_reviewed": True,
        "target_count": 6,
        "independent_local_rollback_domains": 6,
        "static_dual_slot_topologies": 6,
        "r2_target_projects_created": False,
        "r2_target_builds_run": False,
        "physical_rollback_transitions_proven": 0,
        "production_signature_verifier_fit_proven": False,
        "six_image_activation_order_reviewed_here": False,
        "emulator_or_devboard_gate_reviewed_here": False,
    }
    if claims != expected_claims:
        return fail("F0-R2.2 claims changed or overstate the reviewed scope")
    ownership = contract.get("ownership", {})
    if ownership.get("global_bundle_coordinator") != "s3":
        return fail("global coordinator ownership changed")
    if ownership.get("irreversible_lock_default") is not False:
        return fail("the owner-open recovery default changed")

    print(
        "F0-R2.2 memory/rollback contract OK: 6 independent dual-slot domains, "
        "0 physical rollback transitions and 0 R2 builds claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
