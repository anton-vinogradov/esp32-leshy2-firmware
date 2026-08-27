#!/usr/bin/env python3
"""Review the F1-R2.2 rear-RP Airband portable receiver model."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    review = json.loads(
        (ROOT / "config/f1_r2_receiver_review.json").read_text(encoding="utf-8")
    )
    hardware = json.loads(
        (ROOT / "config/h0_r2_hardware_contract.json").read_text(encoding="utf-8")
    )
    errors: list[str] = []
    if review.get("stage") != "F1-R2.2" or review.get("status") != "reviewed":
        errors.append("F1-R2.2 review is not closed")
    air = hardware.get("airband", {})
    plan = review.get("frequency_plan_khz", {})
    if (review.get("owner") != air.get("owner") or
        review.get("signal_group") not in air.get("signal_group", "")):
        errors.append("receiver ownership differs from hardware")
    if [plan.get("user_min") / 1000, plan.get("user_max") / 1000] != air.get("user_range_mhz"):
        errors.append("Airband user range differs from hardware")
    if plan.get("lo") / 1000 != air.get("lo_mhz"):
        errors.append("Airband LO differs from hardware")
    if [plan.get("if_min") / 1000, plan.get("if_max") / 1000] != air.get("if_range_mhz"):
        errors.append("Airband IF range differs from hardware")

    header = (ROOT / "common/include/leshy2/receiver_core.h").read_text(encoding="utf-8")
    for state in review.get("states", []):
        if state not in header:
            errors.append(f"missing receiver state: {state}")
    if "AIRBAND_TX" in header:
        errors.append("forbidden Airband TX surface exists")

    for target in ("host-test", "host-sanitize"):
        result = subprocess.run(
            ["make", target], cwd=ROOT, check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        if result.returncode != 0 or "host receiver core: 6 scenarios passed" not in result.stdout:
            errors.append(f"{target} did not pass six receiver scenarios")
    claims = review.get("claims", {})
    if claims.get("portable_receive_state_machine_implemented") is not True:
        errors.append("portable receiver claim missing")
    for name in (
        "airband_tx_surface_present",
        "physical_rf_switch_or_lo_timing_proven",
        "airband_reception_proven",
        "target_build_or_execution_run",
    ):
        if claims.get(name) is not False:
            errors.append(f"receiver review overstates: {name}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "F1-R2.2 review OK: 5 receive-only states and 6 scenarios pass normal "
        "plus ASan/UBSan; 0 target/RF runs claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
