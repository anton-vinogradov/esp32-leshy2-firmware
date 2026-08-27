#!/usr/bin/env python3
"""Check the honest six-target emulator, dev-board and HIL gate matrix."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "config" / "f0_r2_execution_gate_matrix.json"
IDENTITY_PATH = ROOT / "config" / "f0_r2_target_identity_contract.json"


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    identities = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
    if matrix.get("stage") != "F0-R2.4" or matrix.get("status") != "reviewed_contract":
        return fail("execution matrix is not reviewed at F0-R2.4")

    identity_ids = {row["id"] for row in identities.get("targets", [])}
    rows = matrix.get("targets", [])
    targets = {row["id"]: row for row in rows}
    if len(rows) != 6 or set(targets) != identity_ids:
        return fail("execution gates are not one-to-one with the six target identities")

    layers = {row["id"] for row in matrix.get("evidence_layers", [])}
    if layers != {"host", "target_build", "official_emulator", "development_board", "leshy2_hil"}:
        return fail("a non-substitutable evidence layer disappeared")
    source_ids = {row["id"] for row in matrix.get("sources", [])}
    required_sources = {
        "ESP_QEMU_FEATURES", "ESP32S3_QEMU", "ESP32S3_DEVKIT",
        "ESP32C5_DEVKIT", "PICO_HOST_PLATFORM", "PICO2_DATASHEET",
        "MSPM0_LAUNCHPAD",
    }
    if source_ids != required_sources:
        return fail("current official source set changed")
    if any(not row.get("url", "").startswith("https://") for row in matrix["sources"]):
        return fail("execution source is not an HTTPS primary reference")

    emulator_targets = {
        target_id for target_id, row in targets.items()
        if row.get("official_emulator", {}).get("available") is True
    }
    if emulator_targets != {"s3"} or targets["s3"]["official_emulator"].get("machine") != "esp32s3":
        return fail("only the official ESP32-S3 machine may be claimed as exact")
    for target_id in identity_ids - {"s3"}:
        emulator = targets[target_id]["official_emulator"]
        if emulator.get("available") is not False or emulator.get("machine") is not None:
            return fail(f"{target_id}: nonexistent exact emulator is being claimed")

    for target_id in ("rf_rp", "hub_rp"):
        board = targets[target_id]["development_board"]
        if board.get("exact_selected_module") is not False:
            return fail(f"{target_id}: Pico 2 must remain an explicitly non-exact surrogate")
        not_covered = " ".join(board.get("not_covered", []))
        for token in ("B-package", "stacked 2-MB flash", "exact partition boot"):
            if token not in not_covered:
                return fail(f"{target_id}: surrogate limitation missing: {token}")

    for target_id in identity_ids:
        row = targets[target_id]
        for gate in ("host_gate", "target_build_gate", "development_board", "leshy2_hil"):
            if not row.get(gate):
                return fail(f"{target_id}: missing {gate}")
    claims = matrix.get("claims", {})
    expected_claims = {
        "six_target_execution_gate_matrix_reviewed": True,
        "exact_vendor_emulator_targets": ["s3"],
        "exact_vendor_emulator_target_count": 1,
        "exact_selected_module_or_mcu_devboards": ["s3", "c5", "pack", "safety"],
        "surrogate_devboard_targets": ["rf_rp", "hub_rp"],
        "r2_target_builds_run": False,
        "r2_devboard_runs": 0,
        "r2_leshy2_hil_runs": 0,
        "non_s3_target_boot_proven": False,
        "physical_peripherals_or_transports_proven": False,
    }
    if claims != expected_claims:
        return fail("F0-R2.4 claims changed or overstate execution evidence")

    print(
        "F0-R2.4 execution gates OK: 6 targets, 5 evidence layers, "
        "1 exact emulator, 4 exact-chip/module dev boards, 2 explicit surrogates; 0 R2 runs claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
