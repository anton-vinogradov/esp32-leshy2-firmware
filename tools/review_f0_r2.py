#!/usr/bin/env python3
"""Run the integrated F0-R2 contract closure review."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "config" / "f0_r2_review.json"
PROJECTION_PATH = ROOT / "config" / "h0_r2_hardware_contract.json"
SYNC_PATH = ROOT / "tools" / "sync_h0_r2_contract.py"


def fail(message: str, output: str = "") -> int:
    if output:
        sys.stdout.write(output)
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def load_sync_module():
    spec = importlib.util.spec_from_file_location("sync_h0_r2_contract", SYNC_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    review = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    projection = json.loads(PROJECTION_PATH.read_text(encoding="utf-8"))
    if load_sync_module().build() != projection:
        return fail("H0-R2 projection is stale")
    if review.get("stage") != "F0-R2" or review.get("status") != "reviewed":
        return fail("F0-R2 review artifact is not closed as reviewed")
    if review.get("hardware_source_sha256") != projection.get("hardware_source_sha256"):
        return fail("F0-R2 review is not bound to the current hardware source")

    expected_artifacts = [
        ("F0-R2.0", "config/h0_r2_hardware_contract.json", "tests/test_h0_r2_contract.py"),
        ("F0-R2.1", "config/f0_r2_target_identity_contract.json", "tools/check_f0_r2_target_identities.py"),
        ("F0-R2.2", "config/f0_r2_memory_rollback_contract.json", "tools/check_f0_r2_memory_rollback.py"),
        ("F0-R2.3", "config/update_policy.json", "tools/check_f0_r2_update_policy.py"),
        ("F0-R2.4", "config/f0_r2_execution_gate_matrix.json", "tools/check_f0_r2_execution_gates.py"),
    ]
    actual_artifacts = [
        (row.get("stage"), row.get("path"), row.get("checker"))
        for row in review.get("artifacts", [])
    ]
    if actual_artifacts != expected_artifacts:
        return fail("F0-R2 artifact chain changed")
    if any(not (ROOT / path).is_file() or not (ROOT / checker).is_file() for _, path, checker in expected_artifacts):
        return fail("F0-R2 artifact or checker is missing")

    checks = [
        ("tools/check_r2_h2_sync_gate.py", "R2/H2 sync gate CLOSED"),
        ("tools/check_f0_r2_target_identities.py", "6 application images"),
        ("tools/check_f0_r2_memory_rollback.py", "6 independent dual-slot domains"),
        ("tools/check_f0_r2_update_policy.py", "6 staged/pending/commit targets"),
        ("tools/check_f0_r2_execution_gates.py", "1 exact emulator"),
    ]
    for script, expected in checks:
        result = subprocess.run(
            ["python3", script], cwd=ROOT, check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        if result.returncode != 0 or expected not in result.stdout:
            return fail(f"closure prerequisite failed: {script}", result.stdout)

    expected_evidence = {
        "hardware_domains": 6,
        "hub_centered_transports": 5,
        "application_image_identities": 6,
        "protected_controller_boot_images": 2,
        "independent_dual_slot_domains": 6,
        "staged_pending_commit_targets": 6,
        "execution_evidence_layers": 5,
        "exact_vendor_emulator_targets": 1,
        "exact_selected_module_or_mcu_devboards": 4,
        "explicit_surrogate_devboards": 2,
        "r2_target_builds_run": 0,
        "r2_devboard_runs": 0,
        "r2_leshy2_hil_runs": 0,
    }
    if review.get("evidence") != expected_evidence:
        return fail("F0-R2 integrated evidence counts changed")
    claims = review.get("claims", {})
    for true_claim in (
        "hardware_projection_current_and_hash_bound",
        "target_memory_update_and_execution_contracts_coherent",
        "r1_topology_is_historical_only",
        "f0_r2_reviewed",
    ):
        if claims.get(true_claim) is not True:
            return fail(f"missing closure claim: {true_claim}")
    for false_claim in (
        "r2_projects_or_binaries_implemented",
        "physical_target_or_transport_execution_proven",
        "qualified_update_timing_proven",
        "production_signature_verifier_fit_proven",
    ):
        if claims.get(false_claim) is not False:
            return fail(f"closure overstates evidence: {false_claim}")
    for report in review.get("reports", []):
        if not (ROOT / report).is_file():
            return fail(f"closure report missing: {report}")

    print(
        "F0-R2 closure review OK: 6 domains, 6 images, 6 rollback owners, "
        "5 evidence layers; 0 R2 builds/dev-board/HIL runs claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
