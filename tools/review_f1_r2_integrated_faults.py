#!/usr/bin/env python3
"""Review integrated six-domain F1-R2.3 host fault behavior."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    review = json.loads(
        (ROOT / "config/f1_r2_integrated_fault_review.json").read_text(encoding="utf-8")
    )
    errors: list[str] = []
    if review.get("stage") != "F1-R2.3" or review.get("status") != "reviewed":
        errors.append("F1-R2.3 review is not closed")
    if {row.get("id") for row in review.get("fault_paths", [])} != {
        "HUB_LOSS", "PACK_LOSS", "SAFETY_LOSS",
    }:
        errors.append("integrated fault set changed")
    counts = review.get("scenario_counts_per_run", {})
    if sum(counts.get(name, 0) for name in (
        "safety", "l2ip", "update", "receiver", "integrated_system",
    )) != counts.get("f1_total") or counts.get("f1_total") != 34:
        errors.append("F1 scenario count is not 34")

    markers = (
        "host safety core: 8 scenarios passed",
        "host L2IP core: 4 scenarios passed",
        "host update core: 6 scenarios passed",
        "host receiver core: 6 scenarios passed",
        "host six-domain model: 10 scenarios passed",
    )
    for target in ("host-test", "host-sanitize"):
        result = subprocess.run(
            ["make", target], cwd=ROOT, check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        if result.returncode != 0:
            errors.append(f"{target} failed")
        for marker in markers:
            if marker not in result.stdout:
                errors.append(f"{target} missed marker: {marker}")

    system_source = (ROOT / "common/src/system_model.c").read_text(encoding="utf-8")
    for required in (
        "L2_UPDATE_HUB_RP", "L2_UPDATE_PACK", "L2_UPDATE_SAFETY",
        "l2_receiver_observe", "l2_safety_set_power_fault",
        "l2_safety_watchdog_must_trip",
    ):
        if required not in system_source:
            errors.append(f"integrated model lost {required}")
    claims = review.get("claims", {})
    for name in (
        "hub_pack_safety_fault_paths_reviewed",
        "safety_authority_remains_local",
        "host_fault_suite_passed",
    ):
        if claims.get(name) is not True:
            errors.append(f"missing integrated claim: {name}")
    for name in (
        "physical_watchdog_or_fault_kill_proven",
        "transport_or_receiver_hardware_proven",
    ):
        if claims.get(name) is not False:
            errors.append(f"integrated review overstates: {name}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "F1-R2.3 review OK: 34 scenarios pass normal plus ASan/UBSan; Hub, "
        "Pack and Safety failures are fail-closed; 0 target/physical runs claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
