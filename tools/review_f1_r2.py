#!/usr/bin/env python3
"""Run the integrated F1-R2 portable-core closure review."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    review = json.loads((ROOT / "config/f1_r2_review.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    if review.get("stage") != "F1-R2" or review.get("status") != "reviewed":
        errors.append("F1-R2 closure is not reviewed")
    expected = [
        ("F1-R2.0", "config/f1_r2_portable_rebaseline.json", "tools/check_f1_r2_rebaseline.py"),
        ("F1-R2.1", "config/f1_r2_six_domain_update_review.json", "tools/review_f1_r2_six_domain_update.py"),
        ("F1-R2.2", "config/f1_r2_receiver_review.json", "tools/review_f1_r2_receiver.py"),
        ("F1-R2.3", "config/f1_r2_integrated_fault_review.json", "tools/review_f1_r2_integrated_faults.py"),
    ]
    actual = [(row.get("stage"), row.get("path"), row.get("checker")) for row in review.get("artifacts", [])]
    if actual != expected:
        errors.append("F1-R2 artifact chain changed")
    for _, path, checker in expected:
        if not (ROOT / path).is_file() or not (ROOT / checker).is_file():
            errors.append(f"missing artifact or checker: {path}")
            continue
        result = subprocess.run(
            ["python3", checker], cwd=ROOT, check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        if result.returncode != 0:
            errors.append(f"closure prerequisite failed: {checker}\n{result.stdout}")

    evidence = review.get("evidence", {})
    expected_counts = {
        "portable_files": 12,
        "domain_identities": 6,
        "update_scenarios": 6,
        "receiver_states": 5,
        "receiver_scenarios": 6,
        "integrated_system_scenarios": 10,
        "f1_scenarios_per_configuration": 34,
        "normal_scenario_executions": 34,
        "asan_ubsan_scenario_executions": 34,
        "total_f1_scenario_executions": 68,
        "r2_target_builds": 0,
        "target_or_emulator_runs": 0,
        "physical_or_rf_runs": 0,
    }
    if evidence != expected_counts:
        errors.append("F1-R2 integrated evidence counts changed")
    claims = review.get("claims", {})
    for name in (
        "portable_f1_r2_reviewed",
        "six_domain_update_and_fault_model_reviewed",
        "hub_airband_receive_only_model_reviewed",
        "strict_c17_normal_and_sanitizer_clean",
    ):
        if claims.get(name) is not True:
            errors.append(f"missing closure claim: {name}")
    for name in (
        "target_projects_or_builds_proven",
        "target_instruction_or_peripheral_execution_proven",
        "physical_transport_watchdog_rf_or_rollback_proven",
    ):
        if claims.get(name) is not False:
            errors.append(f"F1-R2 closure overstates: {name}")
    for report in review.get("reports", []):
        if not (ROOT / report).is_file():
            errors.append(f"missing F1 report: {report}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "F1-R2 closure review OK: 6 domains, 5 receiver states, 34 scenarios "
        "and 68 normal+sanitizer executions; 0 target/physical runs claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
