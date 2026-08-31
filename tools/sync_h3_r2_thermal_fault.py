#!/usr/bin/env python3
"""Import the reviewed H3-R2.6 thermal/fault boundary into firmware."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "esp32-leshy2/hardware/verification/generated/H3-R2-thermal-fault.json"
OUTPUT = ROOT / "config/h3_r2_thermal_fault.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    summary = source.get("summary", {})
    checks = source.get("checks", {})
    thermal = source.get("thermal", {})
    single_fault = source.get("single_fault", {})
    unattended = source.get("unattended", {})
    faults = single_fault.get("faults", [])
    if (
        source.get("marker") != "H3-R2.6"
        or source.get("status") != "pass"
        or source.get("errors") != []
        or not checks
        or not all(value is True for value in checks.values())
        or summary.get("checks") != 25
        or summary.get("thermal_profiles") != 56
        or summary.get("single_fault_cases") != 30
        or summary.get("analytical_findings_open") != 0
        or len(thermal.get("profiles", [])) != 56
        or len(faults) != 30
        or {row.get("classification") for row in faults} != {"contained", "detected_no_admission"}
        or unattended.get("full_fault_plane_proof", {}).get("default") != "EVERY_48_H"
        or not unattended.get("runtime_claim", "").startswith("none")
    ):
        raise ValueError("hardware H3-R2.6 thermal/fault evidence is not closed")

    return {
        "schema_version": 1,
        "artifact": "FW-H3-R2.6-thermal-fault-import",
        "status": "reviewed_hardware_contract_imported",
        "hardware_marker": source["marker"],
        "current_hardware_substep": "H4-R2.2",
        "source": {
            "path": "../esp32-leshy2/hardware/verification/generated/H3-R2-thermal-fault.json",
            "sha256": sha256(SOURCE),
        },
        "thermal_contract": {
            "ambient_design_target_c": thermal["ambient_design_target_c"],
            "warning_c": thermal["warning_c"],
            "fault_kill_c": thermal["fault_kill_c"],
            "rearm_below_c": thermal["rearm_below_c"],
            "board_zone_thermistors": thermal["board_zone_thermistors"],
            "worst_sustained_profile": thermal["worst_sustained_profile"],
            "electrical_absolute_profile": thermal["electrical_absolute_profile"],
        },
        "fault_contract": {
            "claim": single_fault["claim"],
            "faults": faults,
            "automatic_or_software_rearm": False,
            "maximum_analytical_detection_ms": summary["maximum_watchdog_detection_ms"],
        },
        "extended_operation_contract": unattended,
        "firmware_invariants": {
            "thermal": "firmware may stop earlier but cannot raise warning, FAULT_KILL or re-arm limits above the reviewed contract",
            "fault": "a fault-only screen never clears FAULT_KILL or enables a payload; recovery requires physical KILL-to-RUN",
            "proof": "expiry revokes TX leases before session stop and a local setting cannot change watchdog/thermal/power-fault deadlines",
            "runtime": "24/48 hours are proof and H8 soak intervals, never an autonomy or uptime promise",
            "support_worst": "SUPPORT_WORST is an electrical corner and never a sustained admission",
        },
        "physical_residuals": source["physical_residuals"],
        "claims": {
            "runtime_safety_policy_implemented": False,
            "target_thermal_adc_or_fault_timing_proven": False,
            "purchasing_or_fabrication_authorized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
        print(f"stale: {OUTPUT.relative_to(ROOT)}")
        return 1
    print("ok: reviewed H3-R2.6 thermal/fault contract is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
