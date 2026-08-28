#!/usr/bin/env python3
"""Shell-free F2-R2 target dispatcher and fail-closed artifact verifier.

All target commands, paths and gates come from f2_r2_build_matrix.json.  This
module prepares the F2-R2.4 qualification surface; it does not treat a dry run,
preflight or partial target build as reviewed execution evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from review_f2_4_preflight import local_environment  # noqa: E402
from toolchain_preflight import validate_exact_environment  # noqa: E402


DEFAULT_MATRIX = REPO_ROOT / "config" / "f2_r2_build_matrix.json"
DEFAULT_EVIDENCE = REPO_ROOT / "config" / "f2_r2_build_qualification.json"
TARGET_IDS = ("s3", "c5", "rf_rp", "hub_rp", "pack", "safety")
CONFIGURATIONS = ("debug", "release")
ENV_TOKEN = re.compile(r"\{env:([A-Z0-9_]+)\}")
FORBIDDEN_EXECUTABLES = {"bash", "dash", "fish", "sh", "zsh"}
FORBIDDEN_ARGUMENTS = {"-c", "&&", "||", "|", ";"}


class QualificationError(RuntimeError):
    """A fail-closed matrix, environment, command or artifact failure."""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_matrix(matrix: dict, repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    if matrix.get("stage") != "F2-R2.1" or matrix.get("status") != "reviewed_matrix":
        errors.append("matrix must retain the reviewed F2-R2.1 identity")
    if matrix.get("build_root") != "build/r2/targets/{target}/{configuration}":
        errors.append("matrix build root must be the isolated R2 target root")
    if list(matrix.get("configurations", {})) != list(CONFIGURATIONS):
        errors.append("matrix must contain debug and release in canonical order")

    locked = matrix.get("locked_environment", {})
    if locked.get("command_form") != "argv_only_no_shell":
        errors.append("matrix command form must remain shell-free argv")
    if locked.get("network_during_configure_or_build") is not False:
        errors.append("network must remain disabled during configure/build")
    expected_environment = {
        "IDF_COMPONENT_MANAGER": "0",
        "FETCHCONTENT_FULLY_DISCONNECTED": "ON",
        "SOURCE_DATE_EPOCH": "{git_commit_timestamp}",
        "LC_ALL": "C",
        "TZ": "UTC",
    }
    if locked.get("environment") != expected_environment:
        errors.append("locked deterministic environment changed")

    for record in [
        *matrix.get("inputs", {}).values(),
        *matrix.get("size_gate_sources", {}).values(),
    ]:
        relative = record.get("path", "")
        path = repo_root / relative
        if not relative or not path.is_file():
            errors.append(f"missing locked input: {relative}")
        elif sha256(path) != record.get("sha256"):
            errors.append(f"stale locked input: {relative}")

    targets = matrix.get("targets", [])
    if [target.get("id") for target in targets] != list(TARGET_IDS):
        errors.append("matrix must contain the exact six R2 targets")
    expected_jobs = [
        {
            "target": target_id,
            "configuration": configuration,
            "build_dir": f"build/r2/targets/{target_id}/{configuration}",
        }
        for target_id in TARGET_IDS
        for configuration in CONFIGURATIONS
    ]
    if matrix.get("jobs") != expected_jobs:
        errors.append("matrix must contain the exact 6x2 Cartesian job set")

    artifact_count = 0
    map_count = 0
    size_gate_count = 0
    for target in targets:
        target_id = target.get("id", "?")
        project_dir = target.get("project_dir", "")
        if not project_dir.startswith("targets/"):
            errors.append(f"{target_id}: project root escapes targets/")
        commands = target.get("commands", {})
        if set(commands) != {"configure", "build", "clean"}:
            errors.append(f"{target_id}: configure/build/clean argv set is incomplete")
        for action, command in commands.items():
            if not isinstance(command, list) or not command:
                errors.append(f"{target_id}: {action} is not a non-empty argv array")
                continue
            if not all(isinstance(argument, str) and argument for argument in command):
                errors.append(f"{target_id}: {action} contains an invalid argv item")
                continue
            executable = Path(command[0]).name
            if executable in FORBIDDEN_EXECUTABLES:
                errors.append(f"{target_id}: {action} crosses a shell boundary")
            if any(argument in FORBIDDEN_ARGUMENTS for argument in command):
                errors.append(f"{target_id}: {action} contains a shell operator")
            if any("\n" in argument or "\x00" in argument for argument in command):
                errors.append(f"{target_id}: {action} contains a control character")

        artifacts = target.get("artifacts", [])
        artifact_paths = [record.get("path") for record in artifacts]
        if not artifact_paths or len(artifact_paths) != len(set(artifact_paths)):
            errors.append(f"{target_id}: artifact paths are empty or duplicated")
        if not all(path and path.startswith("{build}/") for path in artifact_paths):
            errors.append(f"{target_id}: artifact path escapes the job build root")
        maps = [
            record for record in artifacts if record.get("kind") in {"map", "boot_map"}
        ]
        if not maps:
            errors.append(f"{target_id}: no map artifact is declared")
        artifact_count += len(artifacts) * len(CONFIGURATIONS)
        map_count += len(maps) * len(CONFIGURATIONS)

        for gate in target.get("size_gates", []):
            if gate.get("artifact") not in artifact_paths:
                errors.append(f"{target_id}: size gate does not name a declared artifact")
            warning = gate.get("warning_bytes")
            maximum = gate.get("maximum_bytes")
            if not isinstance(warning, int) or not isinstance(maximum, int):
                errors.append(f"{target_id}: size gate is not integral")
            elif not 0 < warning <= maximum:
                errors.append(f"{target_id}: size gate warning/maximum is invalid")
        size_gate_count += len(target.get("size_gates", [])) * len(CONFIGURATIONS)

    evidence = matrix.get("evidence", {})
    expected_evidence = {
        "target_count": 6,
        "configuration_count": 12,
        "artifact_paths_per_complete_pass": artifact_count,
        "map_paths_per_complete_pass": map_count,
        "size_gates_per_complete_pass": size_gate_count,
        "r2_target_projects_created": 0,
        "r2_configures_run": 0,
        "r2_builds_run": 0,
        "r2_emulator_runs": 0,
        "r2_devboard_runs": 0,
        "r2_physical_runs": 0,
    }
    if evidence != expected_evidence:
        errors.append("reviewed F2-R2.1 zero-execution evidence changed")
    return errors


def matrix_targets(matrix: dict) -> dict[str, dict]:
    return {target["id"]: target for target in matrix["targets"]}


def selected_ids(requested: str) -> tuple[str, ...]:
    return TARGET_IDS if requested == "all" else (requested,)


def selected_configurations(requested: str) -> tuple[str, ...]:
    return CONFIGURATIONS if requested == "all" else (requested,)


def job_build_root(
    matrix: dict,
    target_id: str,
    configuration: str,
    repo_root: Path = REPO_ROOT,
) -> Path:
    relative = matrix["build_root"].format(
        target=target_id, configuration=configuration
    )
    path = repo_root / relative
    expected_parent = (repo_root / "build" / "r2" / "targets").resolve()
    resolved_parent = path.parent.resolve()
    if expected_parent not in (resolved_parent, *resolved_parent.parents):
        raise QualificationError(f"unsafe build root: {path}")
    return path


def render_argument(argument: str, values: dict[str, str], environment: dict[str, str]) -> str:
    def replace_environment(match: re.Match[str]) -> str:
        name = match.group(1)
        value = environment.get(name)
        if not value:
            raise QualificationError(f"required environment is unset: {name}")
        return value

    return ENV_TOKEN.sub(replace_environment, argument).format_map(values)


def render_command(
    matrix: dict,
    target: dict,
    action: str,
    configuration: str,
    environment: dict[str, str],
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    build = job_build_root(matrix, target["id"], configuration, repo_root)
    cmake_type = matrix["configurations"][configuration]["cmake_build_type"]
    python = Path(environment["IDF_PYTHON_ENV_PATH"]) / "bin" / "python"
    values = {
        "repo": str(repo_root),
        "build": str(build),
        "configuration": configuration,
        "cmake_build_type": cmake_type,
        "python": str(python),
    }
    return [
        render_argument(argument, values, environment)
        for argument in target["commands"][action]
    ]


def preflight(
    matrix: dict,
    target_ids: tuple[str, ...],
    environment: dict[str, str],
    repo_root: Path = REPO_ROOT,
) -> dict:
    physical_ids = {
        "rp" if target_id in {"rf_rp", "hub_rp"} else target_id
        for target_id in target_ids
    }
    errors, exact = validate_exact_environment(physical_ids, environment)
    targets = matrix_targets(matrix)
    for target_id in target_ids:
        target = targets[target_id]
        project = repo_root / target["project_dir"]
        if not project.is_dir() or project.is_symlink():
            errors.append(f"{target_id}: project root is missing or aliased: {project}")
        for name in target.get("required_environment", []):
            value = environment.get(name, "")
            if not value or not Path(value).exists():
                errors.append(f"{target_id}: invalid required environment: {name}")
        command = render_command(
            matrix, target, "configure", "debug", environment, repo_root
        )
        executable = command[0]
        if os.sep in executable:
            found = Path(executable).is_file()
        else:
            found = shutil.which(executable, path=environment.get("PATH")) is not None
        if not found:
            errors.append(f"{target_id}: configure executable is missing: {executable}")
    if errors:
        raise QualificationError("\n".join(errors))
    return exact


def artifact_path(
    template: str,
    build: Path,
) -> Path:
    rendered = Path(template.format(build=str(build)))
    build_resolved = build.resolve()
    parent = rendered.parent.resolve()
    if build_resolved not in (parent, *parent.parents):
        raise QualificationError(f"artifact escapes build root: {rendered}")
    return rendered


def verify_job(
    matrix: dict,
    target: dict,
    configuration: str,
    repo_root: Path = REPO_ROOT,
) -> dict:
    build = job_build_root(matrix, target["id"], configuration, repo_root)
    records: list[dict] = []
    by_template: dict[str, dict] = {}
    for artifact in target["artifacts"]:
        path = artifact_path(artifact["path"], build)
        if not path.is_file() or path.is_symlink():
            raise QualificationError(f"missing or aliased artifact: {path}")
        size = path.stat().st_size
        if size <= 0:
            raise QualificationError(f"empty artifact: {path}")
        record = {
            "kind": artifact["kind"],
            "path": str(path.relative_to(repo_root)),
            "bytes": size,
            "sha256": sha256(path),
        }
        records.append(record)
        by_template[artifact["path"]] = record

    gate_records: list[dict] = []
    warnings: list[str] = []
    for gate in target.get("size_gates", []):
        record = by_template[gate["artifact"]]
        size = record["bytes"]
        maximum = gate["maximum_bytes"]
        warning = gate["warning_bytes"]
        if size > maximum:
            raise QualificationError(
                f"{target['id']}:{configuration}: {record['path']} is {size} bytes; "
                f"maximum is {maximum}"
            )
        status = "warning" if size > warning else "passed"
        if status == "warning":
            warnings.append(record["path"])
        gate_records.append(
            {
                "artifact": record["path"],
                "bytes": size,
                "warning_bytes": warning,
                "maximum_bytes": maximum,
                "status": status,
                "source": gate["source"],
            }
        )
    return {
        "target": target["id"],
        "configuration": configuration,
        "artifacts": records,
        "size_gates": gate_records,
        "warnings": warnings,
    }


def execute(
    command: list[str],
    environment: dict[str, str],
    repo_root: Path = REPO_ROOT,
) -> None:
    try:
        subprocess.run(
            command,
            cwd=repo_root,
            env=environment,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise QualificationError(f"command failed: {json.dumps(command)}: {error}") from error


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as temporary:
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_name = temporary.name
        os.replace(temporary_name, path)
    finally:
        if temporary_name and Path(temporary_name).exists():
            Path(temporary_name).unlink()


def clean_repository_commit(repo_root: Path = REPO_ROOT) -> str:
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=repo_root,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise QualificationError(f"cannot inspect repository status: {error}") from error
    if status.stdout.strip():
        raise QualificationError(
            "qualification evidence requires a clean repository commit"
        )
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise QualificationError(f"cannot resolve repository commit: {error}") from error
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise QualificationError("cannot resolve the qualification Git commit")
    return revision


def require_pristine_build_roots(matrix: dict, repo_root: Path = REPO_ROOT) -> None:
    occupied: list[str] = []
    for target_id in TARGET_IDS:
        for configuration in CONFIGURATIONS:
            path = job_build_root(matrix, target_id, configuration, repo_root)
            if path.is_symlink() or (path.is_dir() and any(path.iterdir())):
                occupied.append(str(path.relative_to(repo_root)))
            elif path.exists() and not path.is_dir():
                occupied.append(str(path.relative_to(repo_root)))
    if occupied:
        raise QualificationError(
            "qualification requires empty R2 build roots: " + ", ".join(occupied)
        )


def qualification_evidence(
    matrix_path: Path,
    matrix: dict,
    jobs: list[dict],
    commands: list[dict],
    environment: dict[str, str],
    repo_commit: str,
    repo_root: Path = REPO_ROOT,
) -> dict:
    artifacts = sum(len(job["artifacts"]) for job in jobs)
    maps = sum(
        artifact["kind"] in {"map", "boot_map"}
        for job in jobs
        for artifact in job["artifacts"]
    )
    size_gates = sum(len(job["size_gates"]) for job in jobs)
    policy = matrix["inputs"]["build_policy"]
    return {
        "schema_version": 1,
        "stage": "F2-R2.4",
        "status": "reviewed_target_build_qualification",
        "inputs": {
            "matrix": {
                "path": str(matrix_path.relative_to(repo_root)),
                "sha256": sha256(matrix_path),
            },
            "build_policy": policy,
        },
        "repo_commit": repo_commit,
        "source_date_epoch": environment["SOURCE_DATE_EPOCH"],
        "jobs": jobs,
        "commands": commands,
        "totals": {
            "targets": 6,
            "configurations": 12,
            "configure_runs": 12,
            "build_runs": 12,
            "artifact_verify_runs": 12,
            "artifacts": artifacts,
            "maps": maps,
            "size_gates": size_gates,
            "emulator_runs": 0,
            "devboard_runs": 0,
            "physical_runs": 0,
        },
        "claims": {
            "all_target_compilation_and_link_passed": True,
            "all_declared_artifacts_present": True,
            "all_image_size_gates_passed": True,
            "network_during_configure_or_build": False,
            "runtime_boot_proven": False,
            "byte_reproducibility_proven": False,
            "emulator_execution_proven": False,
            "physical_hardware_proven": False,
        },
        "runner": "tools/build_f2_r2_targets.py",
        "next": "F2-R2.5",
    }


def check_evidence(
    evidence_path: Path,
    matrix_path: Path,
    matrix: dict,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    if not evidence_path.is_file():
        return [f"qualification evidence is absent: {evidence_path}"]
    evidence = load_json(evidence_path)
    errors: list[str] = []
    if evidence.get("stage") != "F2-R2.4" or evidence.get("status") != "reviewed_target_build_qualification":
        errors.append("qualification stage/status changed")
    inputs = evidence.get("inputs", {})
    if inputs.get("matrix") != {
        "path": str(matrix_path.relative_to(repo_root)),
        "sha256": sha256(matrix_path),
    }:
        errors.append("qualification matrix input is stale")
    if inputs.get("build_policy") != matrix["inputs"]["build_policy"]:
        errors.append("qualification build-policy input is stale")
    if not re.fullmatch(r"[0-9a-f]{40}", str(evidence.get("repo_commit", ""))):
        errors.append("qualification Git commit is missing")
    if not str(evidence.get("source_date_epoch", "")).isdigit():
        errors.append("qualification SOURCE_DATE_EPOCH is invalid")
    expected_jobs = [
        (target_id, configuration)
        for target_id in TARGET_IDS
        for configuration in CONFIGURATIONS
    ]
    actual_jobs = [
        (job.get("target"), job.get("configuration"))
        for job in evidence.get("jobs", [])
    ]
    if actual_jobs != expected_jobs:
        errors.append("qualification does not contain the exact 6x2 job set")
    target_map = matrix_targets(matrix)
    for job in evidence.get("jobs", []):
        target_id = job.get("target")
        configuration = job.get("configuration")
        if target_id not in target_map or configuration not in CONFIGURATIONS:
            continue
        target = target_map[target_id]
        build = job_build_root(matrix, target_id, configuration, repo_root)
        expected_artifacts = [
            {
                "kind": artifact["kind"],
                "path": str(
                    artifact_path(artifact["path"], build).relative_to(repo_root)
                ),
            }
            for artifact in target["artifacts"]
        ]
        actual_artifacts = job.get("artifacts", [])
        if [
            {"kind": artifact.get("kind"), "path": artifact.get("path")}
            for artifact in actual_artifacts
        ] != expected_artifacts:
            errors.append(f"{target_id}:{configuration}: artifact inventory changed")
        for artifact in actual_artifacts:
            if artifact.get("bytes", 0) <= 0 or not re.fullmatch(
                r"[0-9a-f]{64}", str(artifact.get("sha256", ""))
            ):
                errors.append(
                    f"{target_id}:{configuration}: invalid artifact evidence"
                )
                break
        artifact_sizes = {
            artifact.get("path"): artifact.get("bytes")
            for artifact in actual_artifacts
        }
        actual_gates = job.get("size_gates", [])
        if len(actual_gates) != len(target.get("size_gates", [])):
            errors.append(f"{target_id}:{configuration}: size-gate count changed")
        for actual, expected in zip(actual_gates, target.get("size_gates", [])):
            expected_path = str(
                artifact_path(expected["artifact"], build).relative_to(repo_root)
            )
            if (
                actual.get("artifact") != expected_path
                or actual.get("warning_bytes") != expected["warning_bytes"]
                or actual.get("maximum_bytes") != expected["maximum_bytes"]
                or actual.get("source") != expected["source"]
                or actual.get("status") not in {"passed", "warning"}
                or not isinstance(actual.get("bytes"), int)
                or actual.get("bytes") != artifact_sizes.get(expected_path)
                or actual.get("bytes", expected["maximum_bytes"] + 1)
                > expected["maximum_bytes"]
                or actual.get("status")
                != (
                    "warning"
                    if actual.get("bytes", 0) > expected["warning_bytes"]
                    else "passed"
                )
            ):
                errors.append(f"{target_id}:{configuration}: invalid size-gate evidence")
                break
        expected_warnings = [
            gate.get("artifact")
            for gate in actual_gates
            if gate.get("status") == "warning"
        ]
        if job.get("warnings") != expected_warnings:
            errors.append(f"{target_id}:{configuration}: warning inventory changed")
    expected_totals = {
        "targets": 6,
        "configurations": 12,
        "configure_runs": 12,
        "build_runs": 12,
        "artifact_verify_runs": 12,
        "artifacts": matrix["evidence"]["artifact_paths_per_complete_pass"],
        "maps": matrix["evidence"]["map_paths_per_complete_pass"],
        "size_gates": matrix["evidence"]["size_gates_per_complete_pass"],
        "emulator_runs": 0,
        "devboard_runs": 0,
        "physical_runs": 0,
    }
    if evidence.get("totals") != expected_totals:
        errors.append("qualification totals are incomplete or changed")
    expected_commands = evidence_command_rows(
        matrix,
        TARGET_IDS,
        CONFIGURATIONS,
        ("configure", "build"),
    )
    actual_commands = evidence.get("commands", [])
    if len(actual_commands) != 24:
        errors.append("qualification must record exactly 12 configure and 12 build argv calls")
    elif [
        {
            "target": row.get("target"),
            "configuration": row.get("configuration"),
            "action": row.get("action"),
            "argv": row.get("argv"),
        }
        for row in actual_commands
    ] != expected_commands or any(row.get("status") != "passed" for row in actual_commands):
        errors.append("qualification command evidence differs from the matrix")
    claims = evidence.get("claims", {})
    for name in (
        "all_target_compilation_and_link_passed",
        "all_declared_artifacts_present",
        "all_image_size_gates_passed",
    ):
        if claims.get(name) is not True:
            errors.append(f"missing required qualification claim: {name}")
    for name in (
        "runtime_boot_proven",
        "byte_reproducibility_proven",
        "emulator_execution_proven",
        "physical_hardware_proven",
    ):
        if claims.get(name) is not False:
            errors.append(f"premature qualification claim: {name}")
    if claims.get("network_during_configure_or_build") is not False:
        errors.append("qualification offline claim changed")
    return errors


def command_rows(
    matrix: dict,
    targets: tuple[str, ...],
    configurations: tuple[str, ...],
    actions: tuple[str, ...],
    environment: dict[str, str],
    repo_root: Path = REPO_ROOT,
) -> list[dict]:
    target_map = matrix_targets(matrix)
    return [
        {
            "target": target_id,
            "configuration": configuration,
            "action": action,
            "argv": render_command(
                matrix,
                target_map[target_id],
                action,
                configuration,
                environment,
                repo_root,
            ),
        }
        for target_id in targets
        for configuration in configurations
        for action in actions
    ]


def evidence_command_rows(
    matrix: dict,
    targets: tuple[str, ...],
    configurations: tuple[str, ...],
    actions: tuple[str, ...],
) -> list[dict]:
    """Return portable matrix argv templates for a completed execution record."""

    target_map = matrix_targets(matrix)
    return [
        {
            "target": target_id,
            "configuration": configuration,
            "action": action,
            "argv": list(target_map[target_id]["commands"][action]),
        }
        for target_id in targets
        for configuration in configurations
        for action in actions
    ]


def fail(errors: list[str] | str) -> int:
    rows = [errors] if isinstance(errors, str) else errors
    for error in rows:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=(
            "verify-matrix",
            "list",
            "preflight",
            "configure",
            "build",
            "clean",
            "artifacts",
            "verify",
            "qualify",
            "verify-evidence",
        ),
    )
    parser.add_argument("--target", choices=("all", *TARGET_IDS), default="all")
    parser.add_argument(
        "--config", choices=("all", *CONFIGURATIONS), default="all"
    )
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args()

    matrix_path = DEFAULT_MATRIX.resolve()
    try:
        matrix = load_json(matrix_path)
    except (OSError, json.JSONDecodeError) as error:
        return fail(f"cannot load matrix: {error}")
    errors = validate_matrix(matrix)
    if errors:
        return fail(errors)

    targets = selected_ids(args.target)
    configurations = selected_configurations(args.config)
    if args.action == "verify-matrix":
        print("F2-R2 matrix executable contract OK: 6 targets x 2 configurations; 0 executions")
        return 0
    if args.action == "list":
        target_map = matrix_targets(matrix)
        for target_id in targets:
            target = target_map[target_id]
            print(f"{target_id}\t{target['family']}\t{target['sdk_target']}")
        return 0

    environment = local_environment()
    source_date_epoch = environment["SOURCE_DATE_EPOCH"]
    environment.update(matrix["locked_environment"]["environment"])
    environment["SOURCE_DATE_EPOCH"] = source_date_epoch
    target_map = matrix_targets(matrix)
    try:
        if args.action == "preflight":
            exact = preflight(matrix, targets, environment)
            print(
                f"F2-R2 preflight OK: {len(targets)} target(s), "
                f"{exact['passed']} exact checks; 0 target executions"
            )
            return 0
        if args.action == "artifacts":
            for target_id in targets:
                target = target_map[target_id]
                for configuration in configurations:
                    build = job_build_root(matrix, target_id, configuration)
                    for artifact in target["artifacts"]:
                        print(artifact_path(artifact["path"], build))
            return 0
        if args.action == "verify":
            jobs = [
                verify_job(matrix, target_map[target_id], configuration)
                for target_id in targets
                for configuration in configurations
            ]
            print(
                f"F2-R2 artifacts OK: {len(jobs)} job(s), "
                f"{sum(len(job['artifacts']) for job in jobs)} artifacts; "
                "no execution claim written"
            )
            return 0
        if args.action == "verify-evidence":
            evidence_errors = check_evidence(
                args.evidence.resolve(), matrix_path, matrix
            )
            if evidence_errors:
                return fail(evidence_errors)
            print("F2-R2.4 qualification evidence OK: 12 jobs, 60 artifacts, 16 maps")
            return 0
        if args.action == "qualify":
            if targets != TARGET_IDS or configurations != CONFIGURATIONS:
                raise QualificationError(
                    "qualification evidence requires --target all --config all"
                )
            rows = command_rows(
                matrix,
                targets,
                configurations,
                ("configure", "build"),
                environment,
            )
            if args.dry_run:
                if not args.summary_only:
                    print(json.dumps(rows, indent=2, ensure_ascii=False))
                print("F2-R2 qualification dry run: 24 argv commands; 0 executions; 0 evidence writes")
                return 0
            if not args.write_evidence:
                raise QualificationError(
                    "full qualification requires --write-evidence; partial claims are forbidden"
                )
            if args.evidence.resolve() != DEFAULT_EVIDENCE.resolve():
                raise QualificationError(
                    "qualification evidence may be written only to the canonical path"
                )
            repo_commit = clean_repository_commit()
            require_pristine_build_roots(matrix)
            preflight(matrix, targets, environment)
            executed: list[dict] = []
            jobs: list[dict] = []
            for target_id in targets:
                target = target_map[target_id]
                for configuration in configurations:
                    for action in ("configure", "build"):
                        command = render_command(
                            matrix, target, action, configuration, environment
                        )
                        execute(command, environment)
                        executed.append(
                            {
                                "target": target_id,
                                "configuration": configuration,
                                "action": action,
                                "argv": list(target["commands"][action]),
                                "status": "passed",
                            }
                        )
                    jobs.append(verify_job(matrix, target, configuration))
            evidence = qualification_evidence(
                matrix_path, matrix, jobs, executed, environment, repo_commit
            )
            serialized = json.dumps(evidence, indent=2, ensure_ascii=False) + "\n"
            atomic_write(args.evidence.resolve(), serialized)
            print("F2-R2.4 qualification recorded atomically: 12 jobs, 60 artifacts, 16 maps")
            return 0

        rows = command_rows(
            matrix,
            targets,
            configurations,
            (args.action,),
            environment,
        )
        if args.dry_run:
            if not args.summary_only:
                print(json.dumps(rows, indent=2, ensure_ascii=False))
            print(f"F2-R2 {args.action} dry run: {len(rows)} argv commands; 0 executions")
            return 0
        preflight(matrix, targets, environment)
        for row in rows:
            execute(row["argv"], environment)
        print(f"F2-R2 {args.action} complete: {len(rows)} command(s); no evidence claim written")
        return 0
    except QualificationError as error:
        return fail(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
