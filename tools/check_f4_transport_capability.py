#!/usr/bin/env python3
"""Fail-closed review of the F4.0.0 transport capability matrix."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = REPO_ROOT / "config" / "f4_0_transport_capability_matrix.json"
LOCK_PATH = REPO_ROOT / "environment" / "toolchains.lock.json"
PROTOCOL_PATH = REPO_ROOT / "config" / "interdomain_protocol.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))

    if matrix.get("stage") != "F4.0.0" or matrix.get("status") != "reviewed":
        errors.append("F4.0.0 matrix is not reviewed")

    revisions = {row["id"]: row["commit"] for row in lock["source_revisions"]}
    if matrix.get("locked_sdk_revisions") != {
        "esp-idf": revisions.get("esp-idf"),
        "pico-sdk": revisions.get("pico-sdk"),
        "mspm0-sdk": revisions.get("mspm0-sdk"),
    }:
        errors.append("F4 SDK revisions do not match the reviewed toolchain lock")

    evidence_ids: set[str] = set()
    for record in matrix.get("source_evidence", []):
        record_id = record["id"]
        if record_id in evidence_ids:
            errors.append(f"duplicate source evidence: {record_id}")
        evidence_ids.add(record_id)
        path = REPO_ROOT / record["path"]
        if not path.is_file():
            errors.append(f"missing locked source evidence: {record_id}")
            continue
        if sha256(path) != record["sha256"]:
            errors.append(f"stale locked source evidence: {record_id}")
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in record["required_tokens"]:
            if token not in text:
                errors.append(f"{record_id} no longer contains {token!r}")

    expected_evidence = {
        "S3_SOC_CAPS",
        "C5_SOC_CAPS",
        "S3_SDMMC_HOST",
        "S3_SDIO_COMMANDS",
        "C5_SDIO_SLAVE",
        "S3_SPI_MASTER",
        "S3_I2C_MASTER",
        "IDF_SDIO_HOST_DEPENDENCY",
        "RP_SPI_SLAVE",
        "RP_DMA",
        "RP2350_DREQ",
        "MSPM0_I2C_TARGET",
        "MSPM0C1106_I2C_TARGET_EXAMPLE",
    }
    if evidence_ids != expected_evidence:
        errors.append("F4 source evidence set changed")

    transports = {row["id"]: row for row in matrix.get("transports", [])}
    protocol_transports = {row["id"] for row in protocol["transports"]}
    expected_transports = {"S3_C5", "S3_RP", "S3_PACK", "S3_SAFETY"}
    if set(transports) != expected_transports or protocol_transports != expected_transports:
        errors.append("F4 transport set differs from the reviewed L2IP contract")
    for transport in transports.values():
        if not transport.get("sdk_path_complete"):
            errors.append(f"{transport['id']} lacks a complete exact-SDK path")
        if transport.get("qemu_phy_execution"):
            errors.append(f"{transport['id']} overclaims a QEMU physical path")
        if not transport.get("physical_gate") or not transport.get("host_executable"):
            errors.append(f"{transport['id']} lacks an explicit evidence boundary")
        if len(transport.get("endpoints", {})) != 2:
            errors.append(f"{transport['id']} must bind exactly two endpoints")

    dependency = matrix.get("dependency_decision", {})
    if dependency.get("component") != "espressif/esp_serial_slave_link":
        errors.append("ESSL host dependency is not explicit")
    if dependency.get("selected_exact_version") != "1.1.2":
        errors.append("ESSL exact version changed")
    if dependency.get("floating_constraint_allowed"):
        errors.append("floating ESSL version is forbidden")

    counts = matrix.get("counts", {})
    if counts != {
        "production_transports": 4,
        "exact_sdk_endpoint_bindings": 8,
        "sdk_paths_complete": 4,
        "qemu_phy_paths": 0,
        "physical_transport_runs": 0,
    }:
        errors.append("F4.0.0 capability counts changed")
    if matrix.get("next") != "F4.0.1":
        errors.append("F4.0.0 next marker changed")
    if any(matrix.get("authorization", {}).values()):
        errors.append("F4.0.0 may not authorize hardware work")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        "F4.0.0 transport capability review OK: 4 transports, "
        "8 exact SDK endpoint bindings, 0 physical/QEMU PHY runs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
