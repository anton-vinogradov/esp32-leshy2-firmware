#!/usr/bin/env python3
"""Import the reviewed H3-R2.4 digital-interface boundary into firmware."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "esp32-leshy2/hardware/verification/generated/H3-R2-digital-interfaces.json"
OUTPUT = ROOT / "config/h3_r2_digital_interfaces.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def all_true(value: dict) -> bool:
    return bool(value) and all(item is True for item in value.values())


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    timing = source["display_timing"]
    margins = source["logic_level_margins"]
    loading = source["loading"]
    if (
        source.get("marker") != "H3-R2.4"
        or source.get("status") != "pass"
        or source.get("errors") != []
        or not all_true(source.get("display_topology", {}))
        or not all_true(timing.get("checks", {}))
        or not all_true(source.get("usb_and_service_ownership", {}))
        or not all_true(source.get("m1", {}).get("checks", {}))
        or not all_true(loading.get("checks", {}))
        or any(float(row["minimum_margin"]) <= 0 for row in margins)
    ):
        raise ValueError("hardware H3-R2.4 digital-interface evidence is not closed")
    if timing["clock"] != {
        "requested_hz": 20_000_000,
        "actual_hz": 20_000_000,
        "integer_prescale": 4,
        "forbidden_24mhz_request_actual_hz": 26_666_666.667,
    }:
        raise ValueError("display clock/divider contract changed")

    return {
        "schema_version": 1,
        "artifact": "FW-H3-R2.4-digital-interface-import",
        "status": "reviewed_hardware_contract_imported",
        "hardware_marker": source["marker"],
        "current_hardware_substep": "H4-R2.0.2",
        "source": {
            "path": "../esp32-leshy2/hardware/verification/generated/H3-R2-digital-interfaces.json",
            "sha256": sha256(SOURCE),
        },
        "display": {
            "mode": "direct i8080-8",
            "requested_clock_hz": timing["clock"]["requested_hz"],
            "actual_clock_hz": timing["clock"]["actual_hz"],
            "integer_prescale": timing["clock"]["integer_prescale"],
            "full_frame_wire_ms": timing["throughput"]["full_frame_wire_ms"],
            "theoretical_full_frame_fps": timing["throughput"]["theoretical_full_frame_fps"],
            "forbidden_request_hz": 24_000_000,
            "forbidden_request_actual_hz": timing["clock"]["forbidden_24mhz_request_actual_hz"],
        },
        "logic_level_margins": margins,
        "usb_and_service_ownership": source["usb_and_service_ownership"],
        "m1": source["m1"],
        "transport_timing": source["transport_timing"],
        "runtime_invariants": {
            "display_clock": "request and verify exactly 20 MHz; reject any divider result above 25 MHz",
            "display_owner": "S3 owns all direct i8080 traffic; UI/buttons/encoder remain S3-local",
            "service_usb": "Hub RP, RF RP and C5 service paths never power the product",
            "c5_mux": "hardware service-VBUS latch owns C5 USB versus SDIO selection before firmware",
            "m1_reserve": "contacts 60-64 and 77-80 remain true NC",
        },
        "physical_residuals": source["physical_residuals"],
        "claims": {
            "target_driver_implemented": False,
            "pcb_routing_or_signal_integrity_measured": False,
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
    print("ok: reviewed H3-R2.4 digital-interface contract is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
