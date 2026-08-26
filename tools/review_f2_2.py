#!/usr/bin/env python3
"""Run the complete F2.2 project-boundary review without executing SDKs."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = REPO_ROOT / "config" / "f2_2_review.json"
PROJECTS_PATH = REPO_ROOT / "config" / "target_projects.json"
MATRIX_PATH = REPO_ROOT / "config" / "build_matrix.json"
TARGETS = ("s3", "c5", "rp", "pack", "safety")
CONFIGURATIONS = ("debug", "release")
ACTIONS = ("configure", "build")


def fail(message: str, output: str = "") -> int:
    if output:
        sys.stdout.write(output)
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def run(command: tuple[str, ...], expected: str) -> tuple[bool, str]:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.returncode == 0 and expected in result.stdout, result.stdout


def main() -> int:
    review = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    projects = json.loads(PROJECTS_PATH.read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))

    if review.get("stage") != "F2.2.5" or review.get("status") != "reviewed":
        return fail("F2.2.5 review artifact is not reviewed")
    if projects.get("stage") != "F2.2" or projects.get("status") != "reviewed":
        return fail("target-project registry is not closed as reviewed")
    if projects.get("integrated_review") != {
        "substep": "F2.2.5",
        "status": "reviewed",
        "artifact": "config/f2_2_review.json",
        "runner": "tools/review_f2_2.py",
    }:
        return fail("target-project registry does not bind the F2.2.5 review")

    expected_evidence = {
        "target_projects": 5,
        "project_files": 37,
        "configurations": 2,
        "named_build_artifacts": 26,
        "rendered_configure_and_build_plans": 20,
        "target_pins_consumed": 0,
    }
    if review.get("evidence") != expected_evidence:
        return fail("F2.2 evidence counts changed")

    claims = review.get("claims", {})
    if claims.get("all_target_project_structures_reviewed") is not True:
        return fail("F2.2 does not claim all project structures reviewed")
    if claims.get("target_projects_created") is not True:
        return fail("F2.2 does not claim the five project structures")
    for unexecuted in (
        "target_configure_run",
        "target_builds_run",
        "target_emulators_run",
        "target_pins_consumed_before_f2_3",
    ):
        if claims.get(unexecuted) is not False:
            return fail(f"F2.2 cannot claim {unexecuted}")

    registry_projects = projects.get("projects", {})
    matrix_projects = {target["id"]: target for target in matrix.get("targets", [])}
    if tuple(sorted(registry_projects)) != tuple(sorted(TARGETS)):
        return fail("target-project registry does not contain exactly five domains")
    if tuple(sorted(matrix_projects)) != tuple(sorted(TARGETS)):
        return fail("build matrix does not contain exactly five domains")

    project_files = 0
    artifact_count = 0
    for target_id in TARGETS:
        project = registry_projects[target_id]
        target = matrix_projects[target_id]
        if project.get("status") != "reviewed_structure":
            return fail(f"{target_id}: project structure is not reviewed")
        if project.get("family") != target.get("family"):
            return fail(f"{target_id}: SDK family differs between registry and matrix")
        if project.get("sdk_target") != target.get("sdk_target"):
            return fail(f"{target_id}: SDK target differs between registry and matrix")
        if Path(target["project_dir"]).name != target_id:
            return fail(f"{target_id}: build-matrix project directory is inconsistent")
        for false_claim in ("pins_consumed", "configure_run", "build_run"):
            if project.get(false_claim) is not False:
                return fail(f"{target_id}: F2.2 requires {false_claim}=false")
        project_files += len(project.get("files", []))
        artifact_count += len(target.get("artifacts", []))

    if project_files != expected_evidence["project_files"]:
        return fail(f"project-file count changed: {project_files}")
    if artifact_count != expected_evidence["named_build_artifacts"]:
        return fail(f"named-artifact count changed: {artifact_count}")

    prerequisite_checks = (
        (("python3", "tools/review_f2_1.py"), "F2.1 integrated review OK"),
        (
            ("python3", "tools/check_target_projects.py"),
            "S3/C5/RP/Pack/Safety structures reviewed",
        ),
        (
            ("python3", "tools/build_targets.py", "verify-matrix"),
            "build matrix OK: 5 targets, 2 configurations",
        ),
    )
    for command, expected in prerequisite_checks:
        ok, output = run(command, expected)
        if not ok:
            return fail(f"check failed: {' '.join(command)}", output)

    rendered_plans = 0
    for configuration in CONFIGURATIONS:
        for action in ACTIONS:
            command = (
                "python3",
                "tools/build_targets.py",
                action,
                "--target",
                "all",
                "--config",
                configuration,
                "--dry-run",
            )
            ok, output = run(command, f"safety:{configuration}:{action}")
            if not ok:
                return fail(f"command-plan rendering failed: {' '.join(command)}", output)
            for target_id in TARGETS:
                if f"{target_id}:{configuration}:{action}" not in output:
                    return fail(
                        f"missing command plan for {target_id}:{configuration}:{action}",
                        output,
                    )
                rendered_plans += 1

    if rendered_plans != expected_evidence["rendered_configure_and_build_plans"]:
        return fail(f"rendered command-plan count changed: {rendered_plans}")

    print(
        "F2.2 integrated review OK: 5 project structures, 37 files, "
        "26 named artifacts and 20 configure/build plans; "
        "0 pins and 0 SDK executions claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
