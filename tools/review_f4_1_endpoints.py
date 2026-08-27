#!/usr/bin/env python3
"""Build and verify the F4.1.2 S3/C5 SDIO endpoint review."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = REPO_ROOT / "config" / "f4_1_2_s3_c5_endpoint_review.json"
CONTRACT_PATH = REPO_ROOT / "config" / "f4_0_1_adapter_contract.json"
HARDWARE_CONTRACT_PATH = REPO_ROOT / "config" / "hardware_bsp_contract.json"
VENDOR_LOCK_PATH = REPO_ROOT / "third_party" / "esp_serial_slave_link.vendor-lock.json"
SOURCES = [
    "targets/s3/CMakeLists.txt",
    "targets/s3/main/CMakeLists.txt",
    "targets/s3/components/leshy2_portable/CMakeLists.txt",
    "targets/s3/components/leshy2_s3_c5/CMakeLists.txt",
    "targets/s3/components/leshy2_s3_c5/include/leshy2/s3_c5_host.h",
    "targets/s3/components/leshy2_s3_c5/s3_c5_host.c",
    "targets/c5/main/CMakeLists.txt",
    "targets/c5/components/leshy2_portable/CMakeLists.txt",
    "targets/c5/components/leshy2_s3_c5/CMakeLists.txt",
    "targets/c5/components/leshy2_s3_c5/include/leshy2/s3_c5_slave.h",
    "targets/c5/components/leshy2_s3_c5/s3_c5_slave.c",
]
BUILDS = [
    {"target": "s3", "config": "debug"},
    {"target": "c5", "config": "debug"},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_records() -> list[dict]:
    return [
        {"path": relative, "sha256": sha256(REPO_ROOT / relative)}
        for relative in SOURCES
    ]


def build_records() -> list[dict]:
    records = []
    for build in BUILDS:
        command = [
            "make",
            "locked-target-build",
            f"TARGET={build['target']}",
            f"CONFIG={build['config']}",
        ]
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"{build['target']} {build['config']} build failed:\n{result.stdout}"
            )
        if "Project build complete" not in result.stdout:
            raise RuntimeError(
                f"{build['target']} {build['config']} build lacks success marker"
            )
        records.append(
            {
                **build,
                "command": command,
                "status": "passed",
                "success_marker": "Project build complete",
            }
        )
    return records


def create_review() -> dict:
    return {
        "schema_version": 1,
        "stage": "F4.1.2",
        "status": "reviewed",
        "reviewed_on": "2026-08-27",
        "locked_inputs": {
            "adapter_contract_sha256": sha256(CONTRACT_PATH),
            "hardware_contract_sha256": sha256(HARDWARE_CONTRACT_PATH),
            "essl_vendor_lock_sha256": sha256(VENDOR_LOCK_PATH),
        },
        "sources": source_records(),
        "builds": build_records(),
        "endpoint_contract": {
            "s3_host": {
                "sdk_surface": "SDMMC host plus vendored ESSL 1.1.2",
                "bus_width_bits": 1,
                "frequency_khz": 20000,
                "generated_gpio": {"clk": 10, "cmd": 11, "d0": 12, "d1_irq": 13},
                "cell_bytes": 512,
            },
            "c5_slave": {
                "sdk_surface": "locked ESP-IDF esp_driver_sdio packet mode",
                "generated_gpio": {"d1_irq": 7, "d0": 8, "clk": 9, "cmd": 10},
                "dma_receive_cells": 8,
                "dma_send_cells": 8,
                "cell_bytes": 512,
                "timing": "SDIO_SLAVE_TIMING_PSEND_NSAMPLE",
                "flags": ["SDIO_SLAVE_FLAG_DAT2_DISABLED", "SDIO_SLAVE_FLAG_HIGH_SPEED"],
            },
            "usb_coexistence": "one-bit SDIO leaves C5 module GPIO13/GPIO14 D3/D2 contacts unused by SDIO for native USB D-/D+",
        },
        "accepted_claims": [
            "S3 host endpoint uses generated H2 contacts, one-bit SDMMC and the exact offline ESSL source",
            "C5 slave endpoint uses generated H2 contacts, eight 512-byte DMA RX cells and eight 512-byte DMA TX cells",
            "both endpoints compile the reviewed portable adapter and fail its lifecycle closed on transport errors",
            "locked ESP-IDF debug images compile and link both endpoint implementations",
        ],
        "deferred_claims": [
            "runtime execution above an S3 QEMU fake-SDIO boundary",
            "physical SDIO signaling, throughput, timing margin and USB coexistence",
        ],
        "execution_counts": {
            "host_sanitized_scenarios": 0,
            "exact_target_adapter_builds": 2,
            "s3_qemu_fake_runs": 0,
            "physical_transport_runs": 0,
        },
        "next": "F4.1.3",
    }


def check_review() -> list[str]:
    if not REVIEW_PATH.is_file():
        return ["F4.1.2 endpoint review does not exist"]
    record = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if record.get("stage") != "F4.1.2" or record.get("status") != "reviewed":
        errors.append("F4.1.2 endpoints are not reviewed")
    expected_inputs = {
        "adapter_contract_sha256": sha256(CONTRACT_PATH),
        "hardware_contract_sha256": sha256(HARDWARE_CONTRACT_PATH),
        "essl_vendor_lock_sha256": sha256(VENDOR_LOCK_PATH),
    }
    if record.get("locked_inputs") != expected_inputs:
        errors.append("F4.1.2 locked input hash changed")
    if record.get("sources") != source_records():
        errors.append("F4.1.2 endpoint source hash changed")
    expected_builds = [
        {
            **build,
            "command": [
                "make",
                "locked-target-build",
                f"TARGET={build['target']}",
                f"CONFIG={build['config']}",
            ],
            "status": "passed",
            "success_marker": "Project build complete",
        }
        for build in BUILDS
    ]
    if record.get("builds") != expected_builds:
        errors.append("F4.1.2 exact build record changed")
    endpoint = record.get("endpoint_contract", {})
    if endpoint.get("s3_host", {}).get("generated_gpio") != {
        "clk": 10,
        "cmd": 11,
        "d0": 12,
        "d1_irq": 13,
    }:
        errors.append("F4.1.2 S3 generated GPIO contract changed")
    if endpoint.get("c5_slave", {}).get("generated_gpio") != {
        "d1_irq": 7,
        "d0": 8,
        "clk": 9,
        "cmd": 10,
    }:
        errors.append("F4.1.2 C5 generated GPIO contract changed")
    if endpoint.get("s3_host", {}).get("bus_width_bits") != 1:
        errors.append("F4.1.2 must retain one-bit SDIO")
    if endpoint.get("s3_host", {}).get("frequency_khz") != 20000:
        errors.append("F4.1.2 reviewed SDIO frequency changed")
    if endpoint.get("c5_slave", {}).get("dma_receive_cells") != 8:
        errors.append("F4.1.2 C5 receive ring changed")
    if endpoint.get("c5_slave", {}).get("dma_send_cells") != 8:
        errors.append("F4.1.2 C5 send ring changed")
    if endpoint.get("c5_slave", {}).get("flags") != [
        "SDIO_SLAVE_FLAG_DAT2_DISABLED",
        "SDIO_SLAVE_FLAG_HIGH_SPEED",
    ]:
        errors.append("F4.1.2 C5 SDIO flags changed")
    if record.get("execution_counts") != {
        "host_sanitized_scenarios": 0,
        "exact_target_adapter_builds": 2,
        "s3_qemu_fake_runs": 0,
        "physical_transport_runs": 0,
    }:
        errors.append("F4.1.2 execution counts changed")
    if record.get("next") != "F4.1.3":
        errors.append("F4.1.2 next marker changed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if args.run:
        if not args.write:
            print("ERROR: F4.1.2 run requires --write evidence", file=sys.stderr)
            return 1
        try:
            record = create_review()
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
        REVIEW_PATH.write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    errors = check_review()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("F4.1.2 endpoint review OK: S3+C5 debug builds passed; 0 QEMU/PHY runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
