#!/usr/bin/env python3
"""Run and verify the F4.1.3 exact-build and S3 fake-SDIO QEMU review."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from run_f3_acceptance import check_evidence, evidence_path, execute_s3


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = REPO_ROOT / "config" / "f4_1_3_s3_c5_qemu_plan.json"
ENDPOINT_PATH = REPO_ROOT / "config" / "f4_1_2_s3_c5_endpoint_review.json"
OUTPUT_PATH = REPO_ROOT / "config" / "f4_1_3_s3_c5_qemu_review.json"
STAGE = "F4.1.3"
CONFIGURATIONS = ("debug", "release")
FAKE_SOURCES = [
    "targets/s3/main/app_main.c",
    "targets/s3/components/leshy2_s3_c5/CMakeLists.txt",
    "targets/s3/components/leshy2_s3_c5/include/leshy2/s3_c5_fake.h",
    "targets/s3/components/leshy2_s3_c5/s3_c5_fake.c",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_plan() -> list[str]:
    plan = load(PLAN_PATH)
    errors: list[str] = []
    if plan.get("stage") != STAGE or plan.get("status") != "reviewed_plan":
        errors.append("F4.1.3 QEMU plan is not reviewed")
    policy = plan.get("policy", {})
    for required in (
        "fake_boundary_is_not_a_phy_emulator",
        "debug_and_release_must_pass_identical_markers",
        "every_target_build_uses_the_locked_offline_toolchain",
        "failure_aborts_the_review",
        "physical_sdio_and_usb_coexistence_remain_deferred",
    ):
        if policy.get(required) is not True:
            errors.append(f"F4.1.3 policy must remain true: {required}")
    scenarios = plan.get("scenarios", [])
    expected_ids = [
        "handshake_and_full_cell",
        "partial_cell_fault",
        "slave_reset_fault",
        "interrupt_loss_fault",
        "priority_under_bulk",
        "link_loss_side_effect_gate",
    ]
    if [row.get("id") for row in scenarios] != expected_ids:
        errors.append("F4.1.3 fake-SDIO scenario set changed")
    markers = plan.get("observation", {}).get("ordered_success_markers", [])
    if len(markers) != 12 or any(row.get("marker") not in markers for row in scenarios):
        errors.append("F4.1.3 ordered marker contract is incomplete")
    if plan.get("next") != "F4.1.4":
        errors.append("F4.1.3 next marker changed")
    return errors


def build_command(target: str, configuration: str) -> list[str]:
    return [
        "make",
        "locked-target-build",
        f"TARGET={target}",
        f"CONFIG={configuration}",
    ]


def run_c5_builds() -> None:
    for configuration in CONFIGURATIONS:
        command = build_command("c5", configuration)
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode != 0 or "Project build complete" not in result.stdout:
            raise RuntimeError(
                f"C5 {configuration} exact build failed:\n{result.stdout}"
            )


def run_qemu() -> list[dict]:
    records = []
    for configuration in CONFIGURATIONS:
        record, transcript = execute_s3(configuration, STAGE)
        if record.get("status") != "reviewed":
            raise RuntimeError(
                f"S3 {configuration} fake-SDIO QEMU run failed:\n{transcript[-6000:]}"
            )
        path = evidence_path(configuration, STAGE)
        path.write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        errors = check_evidence(configuration, STAGE)
        if errors:
            raise RuntimeError("\n".join(errors))
        records.append(
            {
                "configuration": configuration,
                "path": str(path.relative_to(REPO_ROOT)),
                "sha256": sha256(path),
                "status": "reviewed",
            }
        )
    return records


def create_review() -> dict:
    errors = validate_plan()
    if errors:
        raise RuntimeError("\n".join(errors))
    run_c5_builds()
    qemu_runs = run_qemu()
    plan = load(PLAN_PATH)
    return {
        "schema_version": 1,
        "stage": STAGE,
        "status": "reviewed",
        "reviewed_on": "2026-08-26",
        "locked_inputs": {
            "endpoint_review_sha256": sha256(ENDPOINT_PATH),
            "qemu_plan_sha256": sha256(PLAN_PATH),
        },
        "fake_sources": [
            {"path": relative, "sha256": sha256(REPO_ROOT / relative)}
            for relative in FAKE_SOURCES
        ],
        "target_builds": [
            {
                "target": target,
                "configuration": configuration,
                "command": build_command(target, configuration),
                "status": "passed",
            }
            for target in ("s3", "c5")
            for configuration in CONFIGURATIONS
        ],
        "qemu_runs": qemu_runs,
        "scenarios": plan["scenarios"],
        "accepted_claims": plan["result_contract"]["accepted_claims"] + [
            "s3_and_c5_debug_release_endpoint_images_compile_and_link"
        ],
        "deferred_claims": plan["result_contract"]["deferred_claims"],
        "execution_counts": {
            "exact_target_adapter_builds": 4,
            "s3_qemu_fake_runs": 2,
            "physical_transport_runs": 0,
        },
        "next": "F4.1.4",
    }


def check_review() -> list[str]:
    errors = validate_plan()
    if not OUTPUT_PATH.is_file():
        return errors + ["F4.1.3 QEMU review does not exist"]
    record = load(OUTPUT_PATH)
    plan = load(PLAN_PATH)
    if record.get("stage") != STAGE or record.get("status") != "reviewed":
        errors.append("F4.1.3 QEMU review is not reviewed")
    if record.get("locked_inputs") != {
        "endpoint_review_sha256": sha256(ENDPOINT_PATH),
        "qemu_plan_sha256": sha256(PLAN_PATH),
    }:
        errors.append("F4.1.3 locked input changed")
    expected_sources = [
        {"path": relative, "sha256": sha256(REPO_ROOT / relative)}
        for relative in FAKE_SOURCES
    ]
    if record.get("fake_sources") != expected_sources:
        errors.append("F4.1.3 fake-boundary source changed")
    expected_builds = [
        {
            "target": target,
            "configuration": configuration,
            "command": build_command(target, configuration),
            "status": "passed",
        }
        for target in ("s3", "c5")
        for configuration in CONFIGURATIONS
    ]
    if record.get("target_builds") != expected_builds:
        errors.append("F4.1.3 exact target build record changed")
    expected_qemu = []
    for configuration in CONFIGURATIONS:
        errors.extend(check_evidence(configuration, STAGE))
        path = evidence_path(configuration, STAGE)
        if path.is_file():
            expected_qemu.append(
                {
                    "configuration": configuration,
                    "path": str(path.relative_to(REPO_ROOT)),
                    "sha256": sha256(path),
                    "status": "reviewed",
                }
            )
    if record.get("qemu_runs") != expected_qemu:
        errors.append("F4.1.3 QEMU evidence hash changed")
    if record.get("scenarios") != plan.get("scenarios"):
        errors.append("F4.1.3 scenario evidence changed")
    if record.get("execution_counts") != {
        "exact_target_adapter_builds": 4,
        "s3_qemu_fake_runs": 2,
        "physical_transport_runs": 0,
    }:
        errors.append("F4.1.3 execution counts changed")
    if record.get("next") != "F4.1.4":
        errors.append("F4.1.3 next marker changed")
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
            print("ERROR: F4.1.3 run requires --write evidence", file=sys.stderr)
            return 1
        try:
            record = create_review()
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
        OUTPUT_PATH.write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    errors = check_review()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("F4.1.3 QEMU review OK: 4 exact builds, 2 fake-SDIO runs, 0 PHY runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
