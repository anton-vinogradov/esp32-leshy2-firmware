#!/usr/bin/env python3
"""Import the reviewed hardware transition contract into firmware authority."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT.parent
    / "esp32-leshy2"
    / "hardware/verification/generated/H3-R2-transition-sequences.json"
)
OUTPUT = ROOT / "config/h3_r2_transition_contract.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if (
        source.get("marker") != "H3-R2.2.1"
        or source.get("status") != "reviewed_startup_shutdown_reset_and_recovery"
        or source.get("summary", {}).get("passed_scenarios") != 14
        or source.get("summary", {}).get("scenarios") != source.get("summary", {}).get("passed_scenarios")
        or source.get("summary", {}).get("errors") != 0
        or not all(source.get("topology_checks", {}).values())
        or not all(source.get("net_checks", {}).values())
    ):
        raise ValueError("hardware H3-R2.2.1 transition result is not reviewed and complete")

    firmware = source["firmware_contract"]
    timing = source["timing"]
    expected_states = [
        "BOOT_HOLD_FAULT",
        "WAIT_KILL",
        "KILL_QUALIFY",
        "ARMED_WAIT_RUN",
        "RUNNING",
        "FAULT_LATCHED",
    ]
    if firmware.get("states") != expected_states:
        raise ValueError("hardware transition state identities changed")
    if timing.get("rearm_rc", {}).get("qualified_kill_ms") != 500:
        raise ValueError("qualified physical KILL interval changed")

    return {
        "schema_version": 1,
        "artifact": "FW-H3-R2.2.1-transition-import",
        "status": "reviewed_hardware_contract_imported",
        "hardware_marker": source["marker"],
        "current_hardware_substep": "H3-R2.6",
        "source": {
            "path": "../esp32-leshy2/hardware/verification/generated/H3-R2-transition-sequences.json",
            "sha256": sha256(SOURCE),
            "source_sha256": source["source_sha256"],
        },
        "firmware_contract": firmware,
        "timing_contract": {
            "qualified_kill_ms": timing["rearm_rc"]["qualified_kill_ms"],
            "watchdog_service_period_ms": timing["watchdog_service_period_ms"],
            "watchdog_timeout_s": timing["watchdog_timeout_s"],
            "watchdog_assert_time_ms": timing["watchdog_assert_time_ms"],
            "supervisor_reset_delay_ms": timing["supervisor_ct_open_reset_delay_ms"],
        },
        "evidence": {
            "passed_scenarios": source["summary"]["passed_scenarios"],
            "failed_scenarios": source["summary"]["scenarios"] - source["summary"]["passed_scenarios"],
            "checked_topology_endpoints": len(source["topology_checks"]),
            "checked_nets": len(source["net_checks"]),
        },
        "claims": {
            "automatic_restart_allowed": False,
            "fresh_qualified_kill_to_run_required": True,
            "c5_and_rf_rp_direct_fault_reset": True,
            "s3_fault_ui_reset_independent": True,
            "target_implementation_or_execution_proven": False,
            "order_authorized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
        print(f"stale: {OUTPUT.relative_to(ROOT)}")
        return 1
    print("ok: reviewed H3-R2.2.1 transition contract is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
