#!/usr/bin/env python3
"""Validate the reviewed six-target F2-R2 build-system rebaseline plan."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "config" / "f2_r2_target_rebaseline.json"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    plan = load("config/f2_r2_target_rebaseline.json")
    errors: list[str] = []
    if plan.get("stage") != "F2-R2.0" or plan.get("status") != "reviewed_plan":
        errors.append("F2-R2.0 plan is not reviewed")

    for source in plan.get("inputs", {}).values():
        path = ROOT / source.get("path", "")
        if not path.is_file():
            errors.append(f"missing input: {source.get('path')}")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != source.get("sha256"):
            errors.append(f"stale input hash: {source.get('path')}")

    identities = load("config/f0_r2_target_identity_contract.json")
    expected_ids = ["s3", "c5", "rf_rp", "hub_rp", "pack", "safety"]
    if [row.get("id") for row in identities.get("targets", [])] != expected_ids:
        errors.append("six target identities changed")
    target_plan = plan.get("r2_target_plan", [])
    if [row.get("id") for row in target_plan] != expected_ids:
        errors.append("R2 project order or identity changed")
    if len({row.get("project_dir") for row in target_plan}) != 6:
        errors.append("R2 projects do not have six independent directories")

    historical = load("config/build_matrix.json")
    historical_ids = [row.get("id") for row in historical.get("targets", [])]
    if historical_ids != ["s3", "c5", "rp", "pack", "safety"]:
        errors.append("retained R1 build inventory changed")
    inventory = plan.get("retained_r1_inventory", {})
    if inventory.get("target_ids") != historical_ids:
        errors.append("R1 target inventory is inconsistent")
    if inventory.get("configuration_count") != 10:
        errors.append("R1 configuration count is not 5x2")
    if inventory.get("status") != "historical_only":
        errors.append("R1 evidence is not explicitly historical")

    memories = {row.get("id"): row for row in load(
        "config/f0_r2_memory_rollback_contract.json"
    ).get("targets", [])}
    if set(memories) != set(expected_ids):
        errors.append("six rollback owners changed")
    if memories.get("rf_rp", {}).get("rollback_owner") == memories.get(
        "hub_rp", {}
    ).get("rollback_owner"):
        errors.append("RF and Hub rollback identities are not independent")

    expected_deltas = {
        "SIX_PROJECT_IDENTITIES",
        "TWELVE_CONFIGURATIONS",
        "SIX_DOMAIN_BSP",
        "INDEPENDENT_ROLLBACK_IMAGES",
        "REPRODUCIBLE_BUILD_EVIDENCE",
    }
    deltas = plan.get("required_delta", [])
    if {row.get("id") for row in deltas} != expected_deltas:
        errors.append("required F2-R2 delta changed")
    if not all(row.get("forbidden_shortcut") for row in deltas):
        errors.append("a required delta lacks a forbidden shortcut")

    expected_steps = [f"F2-R2.{index}" for index in range(1, 6)]
    if [row.get("stage") for row in plan.get("planned_substeps", [])] != expected_steps:
        errors.append("F2-R2 implementation order is incomplete")
    if plan.get("next") != "F2-R2.1":
        errors.append("F2-R2 next marker changed")
    if any(plan.get("execution_counts", {}).values()):
        errors.append("F2-R2.0 may not claim project, build or execution evidence")
    if len(plan.get("evidence_boundary", {}).get("must_not_claim", [])) != 4:
        errors.append("F2-R2 evidence boundary is incomplete")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "F2-R2.0 rebaseline review OK: 5 historical targets -> 6 R2 targets, "
        "12 planned configurations, 5 ordered substeps; 0 R2 builds/runs claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
