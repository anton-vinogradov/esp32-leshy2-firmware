#!/usr/bin/env python3
"""Review the F1-R2.1 six-domain portable update implementation."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_make(target: str) -> tuple[int, str]:
    result = subprocess.run(
        ["make", target], cwd=ROOT, check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    return result.returncode, result.stdout


def main() -> int:
    review = json.loads(
        (ROOT / "config/f1_r2_six_domain_update_review.json").read_text(encoding="utf-8")
    )
    policy = json.loads((ROOT / "config/update_policy.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    expected = ["pack", "safety", "c5", "rf_rp", "hub_rp", "s3"]
    if review.get("stage") != "F1-R2.1" or review.get("status") != "reviewed":
        errors.append("F1-R2.1 review is not closed")
    if review.get("domain_order") != expected:
        errors.append("reviewed domain order changed")
    if policy.get("pending_boot_order") != expected or policy.get("commit_order") != expected:
        errors.append("portable order no longer matches F0 policy")
    header = (ROOT / "common/include/leshy2/update_core.h").read_text(encoding="utf-8")
    for symbol in review.get("portable_symbols", []):
        if symbol not in header:
            errors.append(f"missing portable domain symbol: {symbol}")
    if "L2_UPDATE_DOMAIN_COUNT = 6" not in header:
        errors.append("portable domain count is not six")
    if "L2_UPDATE_GLOBAL_DEADLINE_MS = 16700" not in header:
        errors.append("portable TBYB upper bound changed")

    latest_system_scenarios = 0
    for target in ("host-test", "host-sanitize"):
        returncode, output = run_make(target)
        if returncode != 0:
            errors.append(f"{target} failed")
        if "host update core: 6 scenarios passed" not in output:
            errors.append(f"{target} missed six-target update marker")
        match = re.search(r"host six-domain model: (\d+) scenarios passed", output)
        if match is None or int(match.group(1)) < 7:
            errors.append(f"{target} lost the seven reviewed system scenarios")
        elif int(match.group(1)) > latest_system_scenarios:
            latest_system_scenarios = int(match.group(1))
    claims = review.get("claims", {})
    if not all(claims.get(name) is True for name in (
        "six_portable_domain_identities_implemented",
        "six_target_activation_order_implemented",
        "s3_last_implemented",
        "host_normal_and_sanitizer_runs_passed",
    )):
        errors.append("positive F1-R2.1 claim is incomplete")
    if any(claims.get(name) is not False for name in (
        "r2_target_builds_run",
        "target_or_physical_rollback_proven",
        "qualified_activation_budget_measured",
    )):
        errors.append("F1-R2.1 overstates target or physical evidence")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        f"F1-R2.1 review OK: 6 independent domains, 6 update and {latest_system_scenarios} system "
        "scenarios pass normal plus ASan/UBSan; 0 target/physical runs claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
