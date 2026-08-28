#!/usr/bin/env python3
"""Run the complete F2.1 boundary review without claiming target execution."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = REPO_ROOT / "config" / "f2_1_review.json"

CHECKS = (
    (
        ("python3", "tools/verify_environment_lock.py"),
        "environment lock OK: 26 archives",
    ),
    (
        ("python3", "tools/build_targets.py", "verify-matrix"),
        "build matrix OK: 5 targets, 2 configurations",
    ),
    (
        ("python3", "tools/check_source_layout.py"),
        "source layout OK: 12 portable files",
    ),
    (
        ("python3", "tools/check_build_policy.py"),
        "build policy OK: C17/C++17",
    ),
    (
        ("python3", "tools/import_hardware_contract.py", "--check"),
        "firmware HW/FW and BSP contracts match",
    ),
    (
        ("make", "host-test"),
        "host six-domain model: 10 scenarios passed",
    ),
)


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    review = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    if review.get("stage") != "F2.1.2" or review.get("status") != "reviewed":
        return fail("F2.1.2 review artifact is not reviewed")

    evidence = review.get("evidence", {})
    expected_evidence = {
        "portable_files": 8,
        "host_scenarios": 24,
        "target_identities": 5,
        "sdk_families": 3,
        "hardware_programmable_contacts": 125,
    }
    if evidence != expected_evidence:
        return fail("F2.1 evidence counts changed")

    claims = review.get("claims", {})
    for unexecuted in (
        "target_projects_created",
        "target_builds_run",
        "target_emulators_run",
    ):
        if claims.get(unexecuted) is not False:
            return fail(f"F2.1 cannot claim {unexecuted}")

    output: list[str] = []
    for command, expected in CHECKS:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        output.append(result.stdout)
        if result.returncode != 0:
            sys.stdout.write("".join(output))
            return fail(f"check failed: {' '.join(command)}")
        if expected not in result.stdout:
            sys.stdout.write("".join(output))
            return fail(f"check did not report expected evidence: {' '.join(command)}")

    print(
        "F2.1 integrated review OK: 8-file reviewed baseline, 12 current "
        "portable files after the owned F4 extension, 24 baseline host scenarios, "
        "5 targets, 3 SDK families; no F2 target project/build/emulator claim"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
