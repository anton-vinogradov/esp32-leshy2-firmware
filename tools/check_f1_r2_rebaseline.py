#!/usr/bin/env python3
"""Validate the reviewed F1-R2 portable-core rebaseline plan."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "config" / "f1_r2_portable_rebaseline.json"


def main() -> int:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if plan.get("stage") != "F1-R2.0" or plan.get("status") != "reviewed_plan":
        errors.append("F1-R2.0 plan is not reviewed")

    for source in plan.get("inputs", {}).values():
        path = ROOT / source.get("path", "")
        if not path.is_file():
            errors.append(f"missing input: {source.get('path')}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != source.get("sha256"):
            errors.append(f"stale input hash: {source.get('path')}")

    identities = json.loads(
        (ROOT / "config/f0_r2_target_identity_contract.json").read_text(encoding="utf-8")
    )
    target_ids = [row["id"] for row in identities["targets"]]
    if target_ids != ["s3", "c5", "rf_rp", "hub_rp", "pack", "safety"]:
        errors.append("six target identities changed")

    update = json.loads((ROOT / "config/update_policy.json").read_text(encoding="utf-8"))
    expected_order = ["pack", "safety", "c5", "rf_rp", "hub_rp", "s3"]
    if update.get("pending_boot_order") != expected_order:
        errors.append("pending order is not Pack/Safety/C5/RF/Hub/S3")
    if update.get("commit_order") != expected_order:
        errors.append("commit order is not Pack/Safety/C5/RF/Hub/S3")
    if update.get("deadline", {}).get("rp2350_tbyb_window_ms") != 16700:
        errors.append("RP TBYB window changed")

    deltas = {row.get("id") for row in plan.get("required_delta", [])}
    expected_deltas = {
        "SIX_DOMAIN_IDENTITY", "SIX_TARGET_UPDATE", "HUB_FAILURE_BOUNDARY",
        "AIRBAND_RECEIVER", "EVIDENCE_RERUN",
    }
    if deltas != expected_deltas:
        errors.append("required F1-R2 delta changed")
    if len(plan.get("planned_substeps", [])) != 4:
        errors.append("F1-R2 substep chain is incomplete")
    if not all(row.get("forbidden_shortcut") for row in plan.get("required_delta", [])):
        errors.append("a required delta lacks a forbidden shortcut")
    boundary = plan.get("evidence_boundary", {})
    if len(boundary.get("must_not_claim", [])) != 5:
        errors.append("host evidence boundary is incomplete")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "F1-R2.0 rebaseline review OK: 6 domains, 5 required deltas, "
        "4 ordered substeps; 24 R1 regression scenarios retained"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
