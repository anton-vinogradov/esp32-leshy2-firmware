#!/usr/bin/env python3
"""Run and verify the sanitized F4.1.1 high-speed adapter review."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = REPO_ROOT / "config" / "f4_1_1_high_speed_core_review.json"
CONTRACT_PATH = REPO_ROOT / "config" / "f4_0_1_adapter_contract.json"
SOURCES = [
    "common/include/leshy2/high_speed_adapter.h",
    "common/src/high_speed_adapter.c",
    "host/tests/test_high_speed_adapter.c",
]
SCENARIOS = [
    "fresh_boot_handshake_and_non_ready_gate",
    "incompatible_handshake_faults_closed",
    "reset_cannot_jump_to_ready",
    "tx_ownership_requires_phy_completion",
    "rx_ownership_requires_validation_dispatch_release",
    "safety_queue_exhaustion_faults_closed",
    "control_queue_exhaustion_faults_closed",
    "interactive_queue_backpressure",
    "telemetry_overflow_preserves_newest",
    "bulk_zero_credit_does_not_block_control",
    "bulk_credit_returns_only_after_rx_release",
    "monotonic_remote_grant_is_duplicate_safe",
    "pending_duplicate_coalesces",
    "cached_duplicate_returns_same_result",
    "evicted_duplicate_is_stale",
    "deadline_expiry_prevents_commit",
    "post_commit_result_survives_deadline",
    "peer_boot_change_clears_session_credit_and_results",
    "liveness_gap_faults_closed",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_records() -> list[dict]:
    return [
        {"path": relative, "sha256": sha256(REPO_ROOT / relative)}
        for relative in SOURCES
    ]


def current_baseline_is_r2() -> bool:
    state = json.loads(
        (REPO_ROOT / "config" / "firmware_roadmap_state.json").read_text(
            encoding="utf-8"
        )
    )
    return state.get("baseline") == "R2"


def create_review() -> dict:
    command = ["make", "host-sanitize"]
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    marker = "host high-speed adapter: 19 scenarios passed"
    if result.returncode != 0:
        raise RuntimeError("sanitized host suite failed:\n" + result.stdout)
    if marker not in result.stdout:
        raise RuntimeError("sanitized host suite lacks the high-speed marker")
    return {
        "schema_version": 1,
        "stage": "F4.1.1",
        "status": "reviewed",
        "reviewed_on": "2026-08-26",
        "contract_sha256": sha256(CONTRACT_PATH),
        "sources": source_records(),
        "command": command,
        "sanitizers": ["address", "undefined"],
        "success_marker": marker,
        "scenarios": SCENARIOS,
        "review_finding": {
            "id": "F4-FND-0001",
            "problem": "an absolute free-buffer value can re-grant capacity while cells are in flight",
            "correction": "CREDIT now carries monotonic granted_total and sender availability is granted_total minus locally consumed_total",
            "functional_or_cost_change": "no hardware, memory-pool or BOM change; duplicate credit updates can no longer over-admit bulk RX"
        },
        "accepted_claims": [
            "portable seven-state high-speed lifecycle implemented",
            "fixed 4/8/8/4/8 per-direction queue ownership implemented",
            "duplicate-safe cumulative bulk grants implemented",
            "pending/result duplicate handling and deadlines implemented",
            "19 host scenarios pass ASan and UBSan"
        ],
        "deferred_claims": [
            "S3 and C5 target adapter build",
            "ESSL integration",
            "S3 QEMU fake-SDIO integration",
            "physical SDIO execution and timing"
        ],
        "execution_counts": {
            "host_sanitized_scenarios": 19,
            "exact_target_adapter_builds": 0,
            "s3_qemu_fake_runs": 0,
            "physical_transport_runs": 0
        },
        "next": "F4.1.2",
    }


def check_review() -> list[str]:
    if not REVIEW_PATH.is_file():
        return ["F4.1.1 high-speed core review does not exist"]
    record = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if record.get("stage") != "F4.1.1" or record.get("status") != "reviewed":
        errors.append("F4.1.1 high-speed core is not reviewed")
    if record.get("contract_sha256") != sha256(CONTRACT_PATH):
        errors.append("F4.1.1 adapter contract hash changed")
    if record.get("sources") != source_records():
        errors.append("F4.1.1 source or host-test hash changed")
    if record.get("command") != ["make", "host-sanitize"]:
        errors.append("F4.1.1 sanitizer command changed")
    if record.get("sanitizers") != ["address", "undefined"]:
        errors.append("F4.1.1 sanitizer set changed")
    if record.get("success_marker") != "host high-speed adapter: 19 scenarios passed":
        errors.append("F4.1.1 success marker changed")
    if record.get("scenarios") != SCENARIOS:
        errors.append("F4.1.1 scenario set changed")
    finding = record.get("review_finding", {})
    if finding.get("id") != "F4-FND-0001" or "granted_total" not in finding.get("correction", ""):
        errors.append("F4.1.1 credit-safety finding is missing")
    if record.get("execution_counts") != {
        "host_sanitized_scenarios": 19,
        "exact_target_adapter_builds": 0,
        "s3_qemu_fake_runs": 0,
        "physical_transport_runs": 0,
    }:
        errors.append("F4.1.1 execution counts changed")
    if record.get("next") != "F4.1.2":
        errors.append("F4.1.1 next marker changed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if args.run:
        if current_baseline_is_r2():
            print(
                "ERROR: historical R1 F4.1.1 is superseded by R2; its evidence is immutable",
                file=sys.stderr,
            )
            return 1
        if not args.write:
            print("ERROR: F4.1.1 run requires --write evidence", file=sys.stderr)
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
    print("F4.1.1 high-speed core review OK: 19 ASan/UBSan scenarios, 0 target/QEMU/PHY runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
