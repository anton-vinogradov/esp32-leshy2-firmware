#!/usr/bin/env python3
"""Validate the retained, superseded R1 F4 evidence without advancing it."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = REPO_ROOT / "config" / "f4_0_2_acceptance_matrix.json"
SNAPSHOT_PATH = REPO_ROOT / "config" / "f4_0_2_acceptance_snapshot.json"
HISTORICAL_EVIDENCE_PATH = REPO_ROOT / "config" / "f4_acceptance_current.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expand(command: list[str]) -> list[str]:
    replacements = {
        "{python}": sys.executable,
        "{locked_python}": str(
            REPO_ROOT / ".toolchains/python/idf6_py3.12_env/bin/python"
        ),
    }
    return [replacements.get(token, token) for token in command]


def validate_plan() -> list[str]:
    errors: list[str] = []
    matrix = load(MATRIX_PATH)
    if matrix.get("stage") != "F4.0.2" or matrix.get("status") != "reviewed":
        errors.append("F4.0.2 acceptance matrix is not reviewed")

    input_ids: set[str] = set()
    for record in matrix.get("locked_inputs", []):
        if record["id"] in input_ids:
            errors.append(f"duplicate locked input: {record['id']}")
        input_ids.add(record["id"])
        path = REPO_ROOT / record["path"]
        if not path.is_file():
            errors.append(f"missing locked input: {record['id']}")
        elif sha256(path) != record["sha256"]:
            errors.append(f"stale locked input: {record['id']}")
    if input_ids != {"L2IP", "F4_CAPABILITY", "F4_ADAPTER"}:
        errors.append("F4.0.2 locked input set changed")

    policy = matrix.get("policy", {})
    required_true = {
        "one_runner",
        "a_failure_aborts_the_requested_run",
        "missing_required_evidence_is_failure_not_skip",
        "physical_evidence_requires_exact_fixture_identity",
        "prototype_order_gate_is_stricter_than_plan_review",
        "no_purchase_authorized",
    }
    for name in required_true:
        if policy.get(name) is not True:
            errors.append(f"runner policy must remain true: {name}")
    if policy.get("evidence_class_substitution_allowed") is not False:
        errors.append("evidence-class substitution must remain forbidden")
    if policy.get("qemu_fake_transport_may_claim_physical_execution") is not False:
        errors.append("QEMU fake transport may not claim PHY execution")

    runner = matrix.get("runner", {})
    if runner.get("path") != "tools/run_f4_acceptance.py":
        errors.append("F4 runner path changed")
    for name in (
        "plan_check",
        "dry_run",
        "baseline_run",
        "baseline_check",
        "future_integrated_run",
        "future_integrated_check",
    ):
        if not runner.get(name):
            errors.append(f"runner command is missing: {name}")

    class_rows = matrix.get("evidence_classes", [])
    classes = {row["id"]: row for row in class_rows}
    expected_classes = {
        "STATIC_CONTRACT",
        "HOST_SANITIZED_MODEL",
        "EXACT_TARGET_BUILD",
        "S3_QEMU_FAKE_BOUNDARY",
        "DEV_BOARD_PHY",
        "ASSEMBLED_HIL",
    }
    if len(class_rows) != len(classes) or set(classes) != expected_classes:
        errors.append("F4 evidence taxonomy changed")
    for class_id, row in classes.items():
        if not row.get("proves") or not row.get("cannot_prove"):
            errors.append(f"{class_id} lacks an explicit evidence boundary")
    if "physical" not in classes.get("S3_QEMU_FAKE_BOUNDARY", {}).get("cannot_prove", ""):
        errors.append("QEMU physical non-claim is missing")

    tracks = {row["id"]: row for row in matrix.get("transport_tracks", [])}
    expected_transports = {"S3_C5", "S3_RP", "S3_PACK", "S3_SAFETY"}
    if set(tracks) != expected_transports:
        errors.append("F4 transport track set changed")
    required_for_f4 = expected_classes - {"ASSEMBLED_HIL"}
    for transport_id, track in tracks.items():
        required = set(track.get("required_for_f4_review", []))
        deferred = set(track.get("deferred_to_f10", []))
        if required != required_for_f4:
            errors.append(f"{transport_id} F4 evidence classes changed")
        if deferred != {"ASSEMBLED_HIL"}:
            errors.append(f"{transport_id} assembled HIL deferral changed")
        if len(track.get("endpoint_targets", [])) != 2:
            errors.append(f"{transport_id} must name two exact endpoints")

    preorder = matrix.get("prototype_order_gate", {})
    expected_preorder = {
        "STATIC_CONTRACT",
        "HOST_SANITIZED_MODEL",
        "EXACT_TARGET_BUILD",
        "S3_QEMU_FAKE_BOUNDARY",
    }
    if set(preorder.get("required_for_each_transport", [])) != expected_preorder:
        errors.append("firmware pre-order confidence gate changed")
    if "does not authorize an order" not in preorder.get("rule", ""):
        errors.append("pre-order gate may be mistaken for purchase authorization")

    campaign = matrix.get("scenario_campaign", {})
    common = campaign.get("common", [])
    if len(common) != 17 or len(common) != len(set(common)):
        errors.append("common F4 scenario campaign must contain 17 unique cases")
    specific = campaign.get("transport_specific", {})
    if set(specific) != expected_transports:
        errors.append("transport-specific scenario set changed")
    for transport_id, scenarios in specific.items():
        if len(scenarios) != 5 or len(scenarios) != len(set(scenarios)):
            errors.append(f"{transport_id} must contain five unique fault cases")

    baseline = matrix.get("baseline", {})
    if baseline.get("artifact") != "config/f4_0_2_acceptance_snapshot.json":
        errors.append("F4.0.2 snapshot path changed")
    if baseline.get("commands") != [
        ["{python}", "tools/check_f4_transport_capability.py"],
        ["{python}", "tools/check_f4_adapter_contract.py"],
    ]:
        errors.append("F4.0.2 baseline command set changed")
    if not baseline.get("accepted_claims") or not baseline.get("deferred_claims"):
        errors.append("F4.0.2 baseline claims are incomplete")

    expected_counts = {
        "static_contract_checks": 2,
        "host_sanitized_scenarios": 0,
        "exact_target_adapter_builds": 0,
        "s3_qemu_fake_runs": 0,
        "dev_board_phy_runs": 0,
        "assembled_hil_runs": 0,
    }
    if matrix.get("execution_counts") != expected_counts:
        errors.append("F4.0.2 execution counts changed")
    if matrix.get("next") != "F4.1.0":
        errors.append("F4.0.2 next marker changed")
    if any(matrix.get("authorization", {}).values()):
        errors.append("F4.0.2 may not authorize hardware work")
    return errors


def create_snapshot() -> dict:
    matrix = load(MATRIX_PATH)
    checks = []
    for command in matrix["baseline"]["commands"]:
        expanded = expand(command)
        result = subprocess.run(
            expanded,
            cwd=REPO_ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "baseline command failed: " + " ".join(expanded) + "\n" + result.stdout
            )
        checks.append(
            {
                "command": command,
                "status": "passed",
                "output_last_line": result.stdout.strip().splitlines()[-1],
            }
        )
    return {
        "schema_version": 1,
        "stage": "F4.0.2",
        "status": "reviewed_plan",
        "matrix_sha256": sha256(MATRIX_PATH),
        "locked_inputs": matrix["locked_inputs"],
        "checks": checks,
        "accepted_claims": matrix["baseline"]["accepted_claims"],
        "deferred_claims": matrix["baseline"]["deferred_claims"],
        "execution_counts": matrix["execution_counts"],
        "next": matrix["next"],
        "runner": "tools/run_f4_acceptance.py",
    }


def check_snapshot() -> list[str]:
    if not SNAPSHOT_PATH.is_file():
        return ["F4.0.2 acceptance snapshot does not exist"]
    matrix = load(MATRIX_PATH)
    snapshot = load(SNAPSHOT_PATH)
    errors: list[str] = []
    if snapshot.get("stage") != "F4.0.2" or snapshot.get("status") != "reviewed_plan":
        errors.append("F4.0.2 snapshot is not reviewed")
    if snapshot.get("matrix_sha256") != sha256(MATRIX_PATH):
        errors.append("F4.0.2 snapshot matrix hash changed")
    if snapshot.get("locked_inputs") != matrix.get("locked_inputs"):
        errors.append("F4.0.2 snapshot input lock changed")
    checks = snapshot.get("checks", [])
    if [row.get("command") for row in checks] != matrix["baseline"]["commands"]:
        errors.append("F4.0.2 snapshot command set changed")
    if any(row.get("status") != "passed" for row in checks):
        errors.append("F4.0.2 baseline contains a failed check")
    if snapshot.get("accepted_claims") != matrix["baseline"]["accepted_claims"]:
        errors.append("F4.0.2 accepted claims changed")
    if snapshot.get("deferred_claims") != matrix["baseline"]["deferred_claims"]:
        errors.append("F4.0.2 deferred claims changed")
    if snapshot.get("execution_counts") != matrix["execution_counts"]:
        errors.append("F4.0.2 execution counts changed")
    if snapshot.get("next") != "F4.1.0":
        errors.append("F4.0.2 snapshot next marker changed")
    return errors


def dry_run_plan() -> dict:
    matrix = load(MATRIX_PATH)
    rows = []
    for track in matrix["transport_tracks"]:
        for evidence in matrix["evidence_classes"]:
            class_id = evidence["id"]
            if class_id == "STATIC_CONTRACT":
                state = "reviewed"
            elif class_id == "ASSEMBLED_HIL":
                state = "deferred_to_F10"
            else:
                state = "planned"
            rows.append(
                {
                    "transport": track["id"],
                    "implementation_stage": track["implementation_stage"],
                    "evidence_class": class_id,
                    "state": state,
                }
            )
    return {
        "stage": matrix["stage"],
        "status": "historical_superseded_by_r2",
        "authority": {
            "baseline": "R1",
            "allowed_as_r2_current_progress": False,
        },
        "tracks": rows,
        "prototype_order_gate": matrix["prototype_order_gate"]["name"],
        "authorized_purchase": False,
        "next": None,
    }


def create_historical_evidence() -> dict:
    provider_specs = [
        {
            "stage": "F4.1.1",
            "command": [sys.executable, "tools/review_f4_1_core.py", "--run", "--write"],
            "path": REPO_ROOT / "config" / "f4_1_1_high_speed_core_review.json",
            "evidence_class": "HOST_SANITIZED_MODEL",
            "applies_to": ["S3_C5", "S3_RP"],
        },
        {
            "stage": "F4.1.2",
            "command": [sys.executable, "tools/review_f4_1_endpoints.py", "--run", "--write"],
            "path": REPO_ROOT / "config" / "f4_1_2_s3_c5_endpoint_review.json",
            "evidence_class": "EXACT_TARGET_BUILD",
            "applies_to": ["S3_C5"],
        },
        {
            "stage": "F4.1.3",
            "command": [sys.executable, "tools/review_f4_1_qemu.py", "--run", "--write"],
            "path": REPO_ROOT / "config" / "f4_1_3_s3_c5_qemu_review.json",
            "evidence_class": "S3_QEMU_FAKE_BOUNDARY",
            "applies_to": ["S3_C5"],
        },
    ]
    providers = []
    records = []
    for spec in provider_specs:
        result = subprocess.run(
            spec["command"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"{spec['stage']} evidence provider failed:\n" + result.stdout
            )
        provider = load(spec["path"])
        records.append(provider)
        providers.append(
            {
                "stage": spec["stage"],
                "evidence_class": spec["evidence_class"],
                "applies_to": spec["applies_to"],
                "path": str(spec["path"].relative_to(REPO_ROOT)),
                "sha256": sha256(spec["path"]),
                "status": provider["status"],
            }
        )
    return {
        "schema_version": 1,
        "phase": "F4",
        "historical_last_reviewed_substep": "F4.1.3",
        "status": "historical_superseded_by_r2",
        "authority": {
            "baseline": "R1",
            "lifecycle": "historical_integrated_evidence",
            "allowed_as_r2_physical_authority": False,
            "superseded_by": "config/h0_r2_hardware_contract.json",
        },
        "matrix_sha256": sha256(MATRIX_PATH),
        "providers": providers,
        "accepted_claims": (
            records[0]["accepted_claims"]
            + records[1]["accepted_claims"]
            + records[2]["accepted_claims"]
        ),
        "deferred_claims": records[2]["deferred_claims"],
        "execution_counts": {
            "host_sanitized_scenarios": 19,
            "exact_target_adapter_builds": 4,
            "s3_qemu_fake_runs": 2,
            "physical_transport_runs": 0,
        },
        "superseded_physical_gate": {
            "stage": "F4.1.4",
            "status": "not_run_superseded_by_r2",
            "physical_transport_runs": 0,
        },
        "next": None,
        "runner": "tools/run_f4_acceptance.py",
    }


def check_historical_evidence() -> list[str]:
    if not HISTORICAL_EVIDENCE_PATH.is_file():
        return ["historical integrated R1 F4 evidence does not exist"]
    record = load(HISTORICAL_EVIDENCE_PATH)
    core_path = REPO_ROOT / "config" / "f4_1_1_high_speed_core_review.json"
    endpoint_path = REPO_ROOT / "config" / "f4_1_2_s3_c5_endpoint_review.json"
    qemu_path = REPO_ROOT / "config" / "f4_1_3_s3_c5_qemu_review.json"
    errors: list[str] = []
    if (
        record.get("phase") != "F4"
        or record.get("historical_last_reviewed_substep") != "F4.1.3"
    ):
        errors.append("historical integrated F4 marker changed")
    if record.get("status") != "historical_superseded_by_r2":
        errors.append("R1 F4 evidence is not explicitly historical and superseded")
    if record.get("matrix_sha256") != sha256(MATRIX_PATH):
        errors.append("integrated F4 matrix hash changed")
    if not core_path.is_file() or not endpoint_path.is_file() or not qemu_path.is_file():
        errors.append("F4.1.1, F4.1.2 or F4.1.3 provider is missing")
        return errors
    core = load(core_path)
    endpoint = load(endpoint_path)
    qemu = load(qemu_path)
    expected_provider = [
        {
            "stage": "F4.1.1",
            "evidence_class": "HOST_SANITIZED_MODEL",
            "applies_to": ["S3_C5", "S3_RP"],
            "path": "config/f4_1_1_high_speed_core_review.json",
            "sha256": sha256(core_path),
            "status": "reviewed",
        },
        {
            "stage": "F4.1.2",
            "evidence_class": "EXACT_TARGET_BUILD",
            "applies_to": ["S3_C5"],
            "path": "config/f4_1_2_s3_c5_endpoint_review.json",
            "sha256": sha256(endpoint_path),
            "status": "reviewed",
        },
        {
            "stage": "F4.1.3",
            "evidence_class": "S3_QEMU_FAKE_BOUNDARY",
            "applies_to": ["S3_C5"],
            "path": "config/f4_1_3_s3_c5_qemu_review.json",
            "sha256": sha256(qemu_path),
            "status": "reviewed",
        },
    ]
    if record.get("providers") != expected_provider:
        errors.append("integrated F4 provider record changed")
    if record.get("accepted_claims") != (
        core.get("accepted_claims")
        + endpoint.get("accepted_claims")
        + qemu.get("accepted_claims")
    ):
        errors.append("integrated F4 accepted claims changed")
    if record.get("deferred_claims") != qemu.get("deferred_claims"):
        errors.append("integrated F4 deferred claims changed")
    if record.get("execution_counts") != {
        "host_sanitized_scenarios": 19,
        "exact_target_adapter_builds": 4,
        "s3_qemu_fake_runs": 2,
        "physical_transport_runs": 0,
    }:
        errors.append("integrated F4 execution counts changed")
    if record.get("superseded_physical_gate") != {
        "stage": "F4.1.4",
        "status": "not_run_superseded_by_r2",
        "physical_transport_runs": 0,
    }:
        errors.append("historical F4.1.4 non-execution boundary changed")
    if record.get("next") is not None:
        errors.append("superseded R1 F4 evidence may not name a next action")
    return errors


def print_errors(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-plan", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--snapshot", action="store_true")
    mode.add_argument("--check-snapshot", action="store_true")
    mode.add_argument("--run-available", action="store_true")
    mode.add_argument("--check-evidence", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    errors = validate_plan()
    if errors:
        return print_errors(errors)
    if args.check_plan:
        print(
            "Historical R1 F4.0.2 acceptance plan OK: 4 transports, 6 non-substitutable "
            "evidence classes, 37 scenarios, 0 PHY/QEMU runs"
        )
        return 0
    if args.dry_run:
        print(json.dumps(dry_run_plan(), indent=2))
        return 0
    if args.check_snapshot:
        errors = check_snapshot()
        if errors:
            return print_errors(errors)
        print("F4.0.2 acceptance snapshot OK: 2 static checks; all execution gates remain explicit")
        return 0
    if args.snapshot:
        return print_errors(
            ["R1 F4 is superseded by R2; its reviewed snapshot is immutable"]
        )
    if args.check_evidence:
        errors = check_historical_evidence()
        if errors:
            return print_errors(errors)
        print("Historical R1 F4 evidence OK: F4.1.1 core, F4.1.2 endpoints and F4.1.3 fake-SDIO QEMU reviewed; F4.1.4 was not run and R2 supersedes this lifecycle")
        return 0
    return print_errors(
        ["R1 F4 is superseded by R2; F4.1.1-F4.1.3 evidence is immutable"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
