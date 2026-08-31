#!/usr/bin/env python3
"""Import the reviewed H3-R2.2 power-transition closure into firmware."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "esp32-leshy2" / "hardware/verification/generated/H3-R2-inrush-watchdog.json"
RESULT = ROOT.parent / "esp32-leshy2" / "hardware/verification/generated/H3-R2-transition-result.json"
OUTPUT = ROOT / "config/h3_r2_inrush_watchdog_contract.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    summary = source.get("summary", {})
    if (
        source.get("marker") != "H3-R2.2.3"
        or source.get("status") != "reviewed_inrush_load_steps_watchdog_and_retained_fault_display"
        or summary.get("startup_envelopes") != summary.get("passed_startup_envelopes")
        or summary.get("load_step_rails") != summary.get("passed_load_step_rails")
        or summary.get("fault_scenarios") != summary.get("passed_fault_scenarios")
        or summary.get("analytical_failures") != 0
        or summary.get("automatic_restarts") != 0
        or not all(source.get("topology_checks", {}).values())
        or result.get("marker") != "H3-R2.2.4"
        or result.get("status") != "reviewed_h3_r2_2_power_transitions_complete"
        or not all(result.get("checks", {}).values())
    ):
        raise ValueError("hardware H3-R2.2 power-transition result is not reviewed and complete")

    watchdog = source["watchdog"]
    record = source["fault_record"]
    if watchdog["checks"] != {key: True for key in watchdog["checks"]}:
        raise ValueError("watchdog exact-part or topology check changed")
    if record["slots"] != 2 or record["sector_bytes_each"] != 1024:
        raise ValueError("fault journal geometry changed")

    return {
        "schema_version": 1,
        "artifact": "FW-H3-R2.2.4-power-transition-import",
        "status": "reviewed_hardware_contract_imported",
        "hardware_marker": result["marker"],
        "current_hardware_substep": "H3-R2.5",
        "source": {
            "inrush_watchdog": {
                "path": "../esp32-leshy2/hardware/verification/generated/H3-R2-inrush-watchdog.json",
                "sha256": sha256(SOURCE),
            },
            "transition_result": {
                "path": "../esp32-leshy2/hardware/verification/generated/H3-R2-transition-result.json",
                "sha256": sha256(RESULT),
            },
        },
        "watchdog": {
            "device_id": watchdog["device_id"],
            "mpn": watchdog["mpn"],
            "device_startup_time_us_max": watchdog["device_startup_time_us_max"],
            "watchdog_startup_delay_ms": watchdog["watchdog_startup_delay_ms"],
            "timeout_ms": watchdog["timeout_ms"],
            "wdo_low_ms": watchdog["wdo_low_ms"],
            "service_period_ms": watchdog["service_period_ms"],
            "s3_heartbeat_period_ms": watchdog["s3_heartbeat_period_ms"],
            "s3_heartbeat_deadline_ms": watchdog["s3_heartbeat_deadline_ms"],
            "wdo_is_output_duration_not_extra_detection_latency": True,
        },
        "fault_journal": record,
        "fault_display": source["fault_display"],
        "fault_scenarios": source["fault_scenarios"],
        "external_accessory_admission": source["external_accessory_admission"],
        "startup_envelopes": source["startup_envelopes"],
        "load_steps": source["load_steps"],
        "runtime_invariants": {
            "watchdog_owner": "always-on safety controller toggles WDI; S3 does not service TPS3435 directly",
            "s3_lease": "two missed 500-ms heartbeat periods request a fault",
            "fault_latch": "software, recovered WDI or a recovered source cannot clear FAULT_KILL",
            "restart": "a fresh qualified physical KILL-to-RUN edge is mandatory",
            "fault_only_mode": "may render and read diagnostics only; every payload and TX enable remains blocked",
            "power_cut_commit": "write and verify the inactive slot before its final commit marker; retain the previous CRC-valid slot",
        },
        "evidence": {
            "startup_envelopes": summary["startup_envelopes"],
            "load_step_rails": summary["load_step_rails"],
            "fault_scenarios": summary["fault_scenarios"],
            "analytical_failures": summary["analytical_failures"],
            "automatic_restarts": summary["automatic_restarts"],
        },
        "claims": {
            "target_implementation_or_execution_proven": False,
            "physical_droop_ringing_or_fault_injection_proven": False,
            "pcb_placement_or_routing_authorized": False,
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
    print("ok: reviewed H3-R2.2 power-transition contract is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
