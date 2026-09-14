#!/usr/bin/env python3
"""Import the reviewed H3-R2.4 digital-interface boundary into firmware."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h3_current_scope import inspect_current_power, bind_scope


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "esp32-leshy2/hardware/verification/generated/H3-R2-digital-interfaces.json"
OUTPUT = ROOT / "config/h3_r2_digital_interfaces.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def all_true(value: dict) -> bool:
    return bool(value) and all(item is True for item in value.values())


def validate_c5_diagnostics(source: dict) -> None:
    """Import failed diagnostics too, but never missing proof or new authority."""
    control = source.get("c5_mux_control", {})
    checks = control.get("checks", {})
    if (not isinstance(checks, dict) or not checks
            or any(type(value) is not bool for value in checks.values())
            or control.get("source_topology_status") != ("pass" if all_true(checks) else "fail")
            or not control.get("scope")):
        raise ValueError("C5 source-topology diagnostic is missing or inconsistent")
    for key in ("timing_qualified", "power_sequences_qualified",
                "firmware_service_manager_implemented", "production_release_allowed"):
        if control.get(key) is not False:
            raise ValueError("C5 diagnostic must retain false qualification: " + key)
    usb = source.get("usb_and_service_ownership", {})
    loading = source.get("loading", {})
    for checks, key in (
        (usb, "service_switch_has_usb_full_speed_capability"),
        (usb, "power_off_port_leakage_limit_is_2ua"),
        (loading.get("checks", {}), "c5_mux_typical_bandwidth_screen_is_at_least_10x_bus_clock"),
    ):
        if type(checks.get(key)) is not bool:
            raise ValueError("current C5 diagnostic key is missing: " + key)
    if loading.get("models", {}).get("hub_c5_sdio", {}).get("bandwidth_is_typical_not_timing_proof") is not True:
        raise ValueError("C5 bandwidth must remain a typical-only comparison")


def build() -> dict:
    scope = inspect_current_power([(SOURCE, "H3-R2-digital-interfaces")])
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    validate_c5_diagnostics(source)
    timing = source["display_timing"]
    margins = source["logic_level_margins"]
    loading = source["loading"]
    if scope["current_analytical_scope_complete"] and (
        source.get("marker") != "H3-R2.4"
        or source.get("status") != "pass"
        or source.get("errors") != []
        or not all_true(source.get("display_topology", {}))
        or not all_true(timing.get("checks", {}))
        or not all_true(source.get("usb_and_service_ownership", {}))
        or not all_true(source.get("m1", {}).get("checks", {}))
        or not all_true(loading.get("checks", {}))
        or not all_true(source["c5_mux_control"]["checks"])
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

    imported = {
        "schema_version": 1,
        "artifact": "FW-H3-R2.4-digital-interface-import",
        "status": "reviewed_hardware_contract_imported",
        "hardware_marker": source["marker"],
        "current_hardware_substep": "H4-R2.2",
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
        "c5_mux_control": source["c5_mux_control"],
        "loading": loading,
        "c5_boot_strap": source["c5_boot_strap"],
        "m1": source["m1"],
        "transport_timing": source["transport_timing"],
        "runtime_invariants": {
            "display_clock": "request and verify exactly 20 MHz; reject any divider result above 25 MHz",
            "display_owner": "S3 owns all direct i8080 traffic; UI/buttons/encoder remain S3-local",
            "service_usb": "Hub RP, RF RP and C5 service paths never power the product",
            "c5_mux": "source requirements: SEL=R; VALID=!(O&R); OE=!(A&VALID&P&F); HUB_HOLD=O|L|!R, using NOT(Q), not raw Q_N. Before changing R, request A=0/L=1 and establish reset/pad-high-Z; settle before A=1 and retain Hub hold through the C5 strap/ready interval. Waits are conditional, not measured. Preserve independent physical KILL; no firmware service manager or recovery/timing qualification is implemented/proven.",
            "c5_bandwidth": "1000 MHz is a datasheet typical-only comparison, not a guaranteed SDIO bandwidth or switching-timing qualification",
            "m1_reserve": "contacts 60-64 and 77-80 remain true NC",
        },
        "physical_residuals": source["physical_residuals"],
        "claims": {
            "target_driver_implemented": False,
            "pcb_routing_or_signal_integrity_measured": False,
            "purchasing_or_fabrication_authorized": False,
        },
    }
    return bind_scope(imported, scope)


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
    print("ok: current H3-R2.4 digital-interface contract is synchronized (see imported qualification status)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
