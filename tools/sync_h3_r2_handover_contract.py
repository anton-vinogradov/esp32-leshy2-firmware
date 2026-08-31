#!/usr/bin/env python3
"""Import the reviewed hardware USB/pack/DPM contract into firmware authority."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "esp32-leshy2" / "hardware/verification/generated/H3-R2-handover.json"
OUTPUT = ROOT / "config/h3_r2_handover_contract.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    summary = source.get("summary", {})
    if (
        source.get("marker") != "H3-R2.2.2"
        or source.get("status") != "reviewed_usb_pack_handover_dpm_brownout_and_source_loss"
        or summary.get("transition_cases") != summary.get("passed_cases")
        or summary.get("failed_cases") != 0
        or summary.get("unsafe_admissions") != 0
        or summary.get("automatic_restarts") != 0
        or not all(source.get("topology_checks", {}).values())
        or not all(source.get("configuration_checks", {}).values())
    ):
        raise ValueError("hardware H3-R2.2.2 handover result is not reviewed and complete")

    config = source["configuration"]
    if config["reverse_power_modes"] != {
        "en_otg": False,
        "en_backup": False,
        "reason": "ordinary SYS handover uses the integrated BATFET path; reverse VBUS/PMID generation is outside the product contract",
    }:
        raise ValueError("charger reverse-power policy changed")

    return {
        "schema_version": 1,
        "artifact": "FW-H3-R2.2.2-handover-import",
        "status": "reviewed_hardware_contract_imported",
        "hardware_marker": source["marker"],
        "current_hardware_substep": "H3-R2.3",
        "source": {
            "path": "../esp32-leshy2/hardware/verification/generated/H3-R2-handover.json",
            "sha256": sha256(SOURCE),
            "source_sha256": source["source_sha256"],
        },
        "charger": {
            "device_id": source["exact_charger"]["device_id"],
            "mpn": source["exact_charger"]["mpn"],
            "minimum_system_voltage_v": config["minimum_system_voltage_v"],
            "charge_current_a_max": config["charge_current_a_max"],
            "input_dpm_profiles": config["input_dpm_profiles"],
            "otg_enabled": False,
            "backup_enabled": False,
            "masked_readback_required": True,
        },
        "runtime_contract": {
            "unqualified_5v": "AON diagnostics only; RUN and charging remain off",
            "load_priority": "system load first; reduce charging to zero before reducing an admitted system load",
            "dpm_interrupt": "VINDPM_STAT or IINDPM_STAT triggers source telemetry and reevaluation",
            "pack_supplement": "allowed only for a healthy admitted pack and within the 8-A PF-R2-03 boundary",
            "usb_only_source_loss": "enter monotonic safe reset/shutdown; no hold-up time is assumed",
            "brownout_recovery": "source recovery cannot re-arm RUN; a fresh qualified physical KILL-to-RUN remains mandatory",
        },
        "evidence": {
            "transition_cases": summary["transition_cases"],
            "failed_cases": summary["failed_cases"],
            "topology_checks": summary["topology_checks"],
            "configuration_checks": summary["configuration_checks"],
        },
        "claims": {
            "target_implementation_or_execution_proven": False,
            "physical_droop_or_handover_time_proven": False,
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
    print("ok: reviewed H3-R2.2.2 handover contract is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
