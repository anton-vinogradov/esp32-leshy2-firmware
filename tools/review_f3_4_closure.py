#!/usr/bin/env python3
"""Consolidate F3 evidence and assign every residual to a physical gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "config/f3_4_review.json"
INPUTS = {
    "capability_matrix": "config/f3_execution_capability_matrix.json",
    "debug_boot": "config/f3_1_s3_debug_runtime_review.json",
    "release_boot": "config/f3_1_s3_release_runtime_review.json",
    "fault_scenarios": "config/f3_2_runtime_review.json",
    "resource_boundaries": "config/f3_3_boundary_review.json",
}


def load(relative: str) -> dict:
    return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))


def sha256(relative: str) -> str:
    return hashlib.sha256((REPO_ROOT / relative).read_bytes()).hexdigest()


def build_review() -> dict:
    source = {name: load(path) for name, path in INPUTS.items()}
    for name in ("debug_boot", "release_boot", "fault_scenarios", "resource_boundaries"):
        if source[name].get("status") != "reviewed":
            raise RuntimeError(f"F3 closure input is not reviewed: {name}")
    if source["capability_matrix"].get("status") != "reviewed":
        raise RuntimeError("F3 capability matrix is not reviewed")
    boundaries = source["resource_boundaries"]
    if boundaries["totals"] != {
        "targets": 5,
        "configurations": 10,
        "byte_reproducible_artifacts": 52,
        "image_gates_passed": 10,
        "static_rollback_topologies": 5,
        "physical_rollback_transitions": 0,
    }:
        raise RuntimeError("F3.3 boundary totals changed")
    scenarios = source["fault_scenarios"]
    if scenarios["execution_counts"] != {
        "s3_target_emulator_runs": 2,
        "host_sanitizer_scenarios": 24,
        "hardware_runs": 0,
    }:
        raise RuntimeError("F3.2 execution totals changed")

    return {
        "schema_version": 1,
        "stage": "F3",
        "closure_substep": "F3.4",
        "status": "reviewed",
        "scope": "boot, memory, virtual fault execution and honest physical deferrals",
        "inputs": {
            name: {"path": path, "sha256": sha256(path)}
            for name, path in INPUTS.items()
        },
        "result": {
            "official_exact_target_emulator": "ESP32-S3 QEMU",
            "s3_debug_release_boot_runs": 2,
            "latest_s3_debug_release_scenario_runs": 2,
            "portable_sanitized_scenarios": 24,
            "byte_reproducible_artifacts": 52,
            "image_and_linked_memory_gates": 10,
            "static_rollback_topologies": 5,
            "physical_runs": 0,
        },
        "target_closure": [
            {
                "target": "s3",
                "accepted": [
                    "exact target boot chain in debug and release",
                    "app_main and UART control flow",
                    "8-MiB octal-PSRAM initialization and memory test",
                    "self-test, retained-first-fault and failed-update RAM-model paths",
                    "current image, linked-memory and dual-slot static fit",
                ],
                "physical_gate": "Leshy2 H7/H8 and firmware F10 HIL",
                "deferred": [
                    "display, touch, microSD, audio, radio and external GPIO timing",
                    "first-boot OTA-data write and nonvolatile retained fault",
                    "signed flash readback, pending-slot confirmation and bootloader rollback",
                ],
            },
            {
                "target": "c5",
                "accepted": [
                    "reproducible debug/release target artifacts",
                    "portable contracts and current image/linked-memory/dual-slot static fit",
                ],
                "physical_gate": "ESP32-C5-DevKitC-1-N8R8, then Leshy2 H7/H8 and firmware F10",
                "deferred": [
                    "target boot and 8-MiB external-PSRAM runtime test",
                    "Wi-Fi 2.4/5 GHz, BLE, IEEE 802.15.4, IR and SDIO",
                    "flash activation and rollback",
                ],
            },
            {
                "target": "rp",
                "accepted": [
                    "reproducible RP2354B Arm-secure debug/release target artifacts",
                    "portable contracts and current image/SRAM/A-B static fit",
                ],
                "physical_gate": "SC1512-A4 carrier or Leshy2 H7 through SWD/UART, then firmware F10",
                "deferred": [
                    "target boot, Boot ROM/TBYB transition and nonvolatile fault log",
                    "PIO, DMA, nRF24, Sub-GHz, voice and Cap-Bus timing",
                ],
            },
            {
                "target": "pack",
                "accepted": [
                    "reproducible application/boot-manager artifacts",
                    "portable safety model and current flash/SRAM/A-B static fit",
                ],
                "physical_gate": "LP-MSPM0C1106, then Leshy2 H7/H8 and firmware F10",
                "deferred": [
                    "target boot, ADC/I2C and pack-admission timing",
                    "signed flash activation, confirmation, brownout and rollback",
                ],
            },
            {
                "target": "safety",
                "accepted": [
                    "reproducible application/boot-manager artifacts",
                    "portable safety model and current flash/SRAM/A-B static fit",
                ],
                "physical_gate": "LP-MSPM0C1106, then Leshy2 H7/H8 and firmware F10",
                "deferred": [
                    "target boot, watchdog, thermal ADC, FAULT_KILL and TX-lease timing",
                    "signed flash activation, confirmation, brownout and rollback",
                ],
            },
        ],
        "claims": {
            "f3_exit_criteria_pass": True,
            "s3_exact_virtual_execution_proven": True,
            "non_s3_target_boot_proven": False,
            "physical_peripherals_proven": False,
            "physical_flash_or_rollback_proven": False,
            "hardware_order_authorized": False,
            "pcb_layout_authorized": False,
        },
        "next": "F4.0.0",
        "hardware_intersection": "H4.0.1 prerequisite closes; hardware may begin H4.1 joined read-only review",
        "runner": "tools/review_f3_4_closure.py",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        review = build_review()
    except (OSError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    serialized = json.dumps(review, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        OUTPUT_PATH.write_text(serialized, encoding="utf-8")
    elif not OUTPUT_PATH.is_file() or OUTPUT_PATH.read_text(encoding="utf-8") != serialized:
        print("ERROR: F3 closure evidence is stale", file=sys.stderr)
        return 1
    print(
        "F3 closure review OK: exact S3 virtual execution, 52 reproducible artifacts, "
        "5 physical target/HIL gates retained"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
