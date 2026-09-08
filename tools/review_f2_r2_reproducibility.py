#!/usr/bin/env python3
"""Two genuine clean R2 passes at fixed paths, commit and epoch; no deletions.

All 60 declared artifacts are compared. Maps have one explicit, recorded build
publication step, never a comparison-only filter. Failure retains recovery data
and does not replace either canonical evidence record.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import build_f2_r2_targets as build
import normalize_r2_map_paths as maps


ROOT = build.REPO_ROOT
OUTPUT = ROOT / "config/f2_r2_reproducibility.json"
EXCLUDED_INPUTS = {
    "config/f2_r2_build_qualification.json", "config/f2_r2_reproducibility.json",
    "config/firmware_roadmap_state.json",
}
CLAIMS = {
    "two_clean_passes_same_input_commit": True,
    "all_60_artifacts_byte_identical": True,
    "all_60_artifacts_source_path_scan_passed": True,
    "raw_maps_retained_and_publication_verified": True,
    "cross_workspace_byte_equality_proven": False,
    "runtime_boot_proven": False,
    "emulator_execution_proven": False,
    "physical_hardware_proven": False,
}


class PublicationRollbackError(build.QualificationError):
    """An I/O failure also prevented recovery of a canonical evidence file."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise build.QualificationError(message)


def serialized(value: dict) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def source_snapshot(root: Path, commit: str) -> dict[str, str]:
    """Pin build code as well as contracts, permitting later docs-only commits."""
    require(bool(re.fullmatch(r"[0-9a-f]{40}", commit)), "invalid input commit")
    paths = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root).decode().split("\x00")
    selected = sorted(path for path in paths if path not in EXCLUDED_INPUTS and (
        path.startswith(("common/", "targets/", "generated/r2/", "environment/", "config/", "tools/"))
        or path == "Makefile"
    ))
    result = {}
    for relative in selected:
        path = root / relative
        require(path.is_file() and not path.is_symlink(), f"non-regular input: {relative}")
        data = path.read_bytes()
        pinned = subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=root, stderr=subprocess.PIPE)
        require(data == pinned, f"input differs from its pinned Git commit: {relative}")
        result[relative] = maps.digest(data)
    require(bool(result), "empty build input snapshot")
    return result


def validate_policy(matrix: dict, root: Path) -> None:
    policy = build.load_json(root / matrix["inputs"]["build_policy"]["path"])
    repro = policy.get("reproducibility", {})
    require(repro.get("absolute_source_paths_in_artifacts") is False, "absolute source path policy must not be weakened")
    step = repro.get("map_publication_step", {})
    require(step.get("runner") == "tools/review_f2_r2_reproducibility.py"
            and step.get("raw_sdk_maps_retained") is True
            and step.get("raw_to_published_sha256_and_replacement_counts_required") is True
            and step.get("unknown_absolute_roots_or_timestamps_may_be_stripped") is False
            and step.get("comparison_scope") == "all 60 declared artifacts, including debug and maps",
            "explicit all-artifact map publication policy is missing or weakened")


def real_path(base: Path, relative: str, *, directory: bool = False) -> Path:
    rel = Path(relative)
    require(bool(relative) and not rel.is_absolute() and ".." not in rel.parts, "unsafe recovery path")
    path = base / rel
    require(base.resolve() in path.resolve().parents, "recovery path escapes its root")
    for item in (path, *path.parents):
        if item == base:
            break
        require(not item.is_symlink(), f"aliased recovery path: {relative}")
    require(path.is_dir() if directory else path.is_file(), f"missing recovery {'directory' if directory else 'file'}: {relative}")
    return path


def move_build_roots(matrix: dict, destination: Path, root: Path) -> None:
    """Resolve all twelve targets before moving any; preserve instead of clean."""
    planned = []
    for job in matrix["jobs"]:
        path = build.job_build_root(matrix, job["target"], job["configuration"], root)
        for ancestor in (path, *path.parents):
            if ancestor == root:
                break
            require(not ancestor.is_symlink(), f"cannot recover aliased build root: {path}")
        require(not path.exists() or path.is_dir(), f"build root is not a directory: {path}")
        target = destination / path.relative_to(root)
        require(not target.exists() and not target.is_symlink(), "recovery target already exists")
        if path.exists():
            planned.append((path, target))
    for path, target in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(target))


def scan_artifact(path: Path, root: Path) -> None:
    findings = maps.source_path_findings(path.read_bytes(), root)
    require(not findings, f"absolute source path in {path.name}: {findings[:8]}")


def publish_job_maps(matrix: dict, target: dict, configuration: str, root: Path,
                     recovery: Path, pass_number: int, epoch: str) -> list[dict]:
    rows = []
    job_root = build.job_build_root(matrix, target["id"], configuration, root)
    for artifact in target["artifacts"]:
        if artifact["kind"] not in {"map", "boot_map"}:
            continue
        path = build.artifact_path(artifact["path"], job_root)
        relative = str(path.relative_to(root))
        raw_relative = f"raw-maps/pass-{pass_number}/{relative}"
        row = {"artifact": relative, "prepublication_map": raw_relative}
        if target["id"] in {"pack", "safety"}:
            sdk_relative = f"sdk-maps/pass-{pass_number}/{target['id']}/{configuration}/{path.name}"
            sdk = real_path(recovery, sdk_relative).read_bytes()
            require(maps.ti_epoch_bytes(sdk, epoch) == path.read_bytes(), "TI epoch publication changed unknown map bytes")
            row.update({"sdk_raw_map": sdk_relative, "sdk_raw_sha256": maps.digest(sdk), "ti_header_replacements": 1})
        row.update(maps.publish_map(path, recovery / raw_relative, root))
        rows.append(row)
    return rows


def run_pass(matrix_path: Path, matrix: dict, environment: dict, commit: str,
             root: Path, recovery: Path, number: int) -> dict:
    build.require_pristine_build_roots(matrix, root)
    build.preflight(matrix, build.TARGET_IDS, environment, root)
    jobs, commands, publications = [], [], []
    for target in matrix["targets"]:
        for configuration in build.CONFIGURATIONS:
            job_environment = dict(environment)
            raw = recovery / f"sdk-maps/pass-{number}/{target['id']}/{configuration}"
            raw.mkdir(parents=True, exist_ok=False)
            job_environment["LESHY2_R2_RAW_MAP_RECOVERY"] = str(raw)
            for action in ("configure", "build"):
                argv = build.render_command(matrix, target, action, configuration, job_environment, root)
                build.execute(argv, job_environment, root)
                commands.append({"target": target["id"], "configuration": configuration,
                                 "action": action, "argv": list(target["commands"][action]), "status": "passed"})
            publications.extend(publish_job_maps(matrix, target, configuration, root, recovery, number, environment["SOURCE_DATE_EPOCH"]))
            job = build.verify_job(matrix, target, configuration, root)
            for artifact in job["artifacts"]:
                scan_artifact(root / artifact["path"], root)
            jobs.append(job)
    qualification = build.qualification_evidence(matrix_path, matrix, jobs, commands, environment, commit, root)
    record = {"number": number, "qualification": qualification, "map_publications": publications}
    build.atomic_write(recovery / f"pass-{number}.json", serialized(qualification))
    return record


def artifact_rows(qualification: dict) -> list[dict]:
    return [artifact for job in qualification["jobs"] for artifact in job["artifacts"]]


def compare_passes(first: dict, second: dict, first_root: Path, second_root: Path) -> list[dict]:
    left, right = artifact_rows(first), artifact_rows(second)
    require(len(left) == len(right) == 60, "comparison requires all 60 declared artifacts in each pass")
    require([a["path"] for a in left] == [a["path"] for a in right], "artifact comparison inventories differ")
    compared = []
    for a, b in zip(left, right):
        relative = a["path"]
        one = real_path(first_root, relative).read_bytes()
        two = real_path(second_root, relative).read_bytes()
        require(len(one) == a["bytes"] and maps.digest(one) == a["sha256"], f"retained first-pass artifact changed: {relative}")
        require(len(two) == b["bytes"] and maps.digest(two) == b["sha256"], f"second-pass artifact changed: {relative}")
        require(a == b and one == two, f"two clean passes are not byte identical: {relative}")
        compared.append({"path": relative, "bytes": len(two), "sha256": maps.digest(two), "byte_equal": True})
    return compared


def publish_records(root: Path, qualification: dict, record: dict) -> None:
    """Publish the checked pair, restoring both prior files on any write error."""
    payloads = {
        root / "config/f2_r2_build_qualification.json": serialized(qualification),
        root / "config/f2_r2_reproducibility.json": serialized(record),
    }
    previous = {}
    for path in payloads:
        require(not path.is_symlink(), "canonical evidence must not be a symlink")
        previous[path] = path.read_text(encoding="utf-8") if path.exists() else None
    try:
        for path, content in payloads.items():
            build.atomic_write(path, content)
    except Exception as error:
        rollback_errors = []
        for path, content in previous.items():
            try:
                if content is None:
                    # Only a newly created canonical file in this exact pair.
                    if path.exists():
                        path.unlink()
                else:
                    build.atomic_write(path, content)
            except Exception as rollback_error:
                rollback_errors.append(f"{path.name}: {rollback_error}")
        if rollback_errors:
            raise PublicationRollbackError(
                "canonical publication failed and rollback is incomplete; restore preserved previous records: "
                + "; ".join(rollback_errors)
            ) from error
        raise build.QualificationError("canonical publication failed; both previous records restored") from error


def check_record(record: dict, matrix_path: Path, matrix: dict, root: Path = ROOT) -> list[str]:
    """Re-read both builds, raw map preimages, inputs, Git commit and epoch."""
    try:
        require(record.get("schema_version") == 1 and record.get("stage") == "F2-R2.5"
                and record.get("status") == "two_clean_passes_verified", "reproducibility stage/status changed")
        require(record.get("claims") == CLAIMS, "reproducibility claims changed")
        validate_policy(matrix, root)
        errors = build.validate_matrix(matrix, root)
        require(not errors, "; ".join(errors))
        name = record.get("recovery_directory", "")
        require(bool(re.fullmatch(r"fw-r2-repro-[A-Za-z0-9_-]+", name)), "unsafe recovery directory name")
        recovery = real_path(root.parent / "work", name, directory=True)
        require(record.get("checkout_root_sha256") == maps.digest(str(root.resolve()).encode()), "record belongs to a different checkout path")
        commit = record.get("repo_commit", "")
        require(record.get("build_inputs") == source_snapshot(root, commit), "build source snapshot changed")
        passes = record.get("passes", [])
        require([p.get("number") for p in passes] == [1, 2], "exactly two complete ordered passes are required")
        for number, row in enumerate(passes, 1):
            qualification = row["qualification"]
            require(qualification.get("repo_commit") == commit and qualification.get("source_date_epoch") == record.get("source_date_epoch"), "pass commit/epoch differs")
            manifest = real_path(recovery, f"pass-{number}.json")
            require(build.load_json(manifest) == qualification, "retained pass manifest changed")
            artifact_root = recovery / "pass-1-builds" if number == 1 else root
            errors = build.check_evidence(manifest, matrix_path, matrix, root, artifact_root=artifact_root)
            require(not errors, "; ".join(errors))
            artifacts = artifact_rows(qualification)
            for artifact in artifacts:
                scan_artifact(real_path(artifact_root, artifact["path"]), root)
            expected_maps = [a["path"] for a in artifacts if a["kind"] in {"map", "boot_map"}]
            publications = row.get("map_publications", [])
            require([p.get("artifact") for p in publications] == expected_maps and len(expected_maps) == 16, "all 16 map publications must be proved")
            for publication in publications:
                relative = publication["artifact"]
                require(publication.get("prepublication_map") == f"raw-maps/pass-{number}/{relative}", "raw map identity changed")
                raw = real_path(recovery, publication["prepublication_map"]).read_bytes()
                published = real_path(artifact_root, relative).read_bytes()
                errors = maps.publication_errors(publication, raw, published, str(root.resolve()).encode())
                require(not errors, "; ".join(errors))
                pieces = Path(relative).parts
                target, configuration = pieces[3:5]
                if target in {"pack", "safety"}:
                    sdk_relative = f"sdk-maps/pass-{number}/{target}/{configuration}/{Path(relative).name}"
                    require(publication.get("sdk_raw_map") == sdk_relative and publication.get("ti_header_replacements") == 1, "TI SDK raw map identity changed")
                    sdk = real_path(recovery, sdk_relative).read_bytes()
                    require(maps.digest(sdk) == publication.get("sdk_raw_sha256") and maps.ti_epoch_bytes(sdk, record["source_date_epoch"]) == raw, "TI SDK raw map/header proof differs")
        comparisons = compare_passes(passes[0]["qualification"], passes[1]["qualification"], recovery / "pass-1-builds", root)
        require(record.get("comparisons") == comparisons, "all-artifact comparison evidence changed")
        return []
    except (build.QualificationError, OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        return [str(error)]


def run(matrix_path: Path = build.DEFAULT_MATRIX, root: Path = ROOT) -> dict:
    matrix = build.load_json(matrix_path)
    errors = build.validate_matrix(matrix, root)
    require(not errors, "; ".join(errors))
    validate_policy(matrix, root)
    commit = build.clean_repository_commit(root)
    inputs = source_snapshot(root, commit)
    epoch = subprocess.check_output(["git", "show", "-s", "--format=%ct", commit], cwd=root, text=True).strip()
    environment = build.local_environment()
    environment.update(matrix["locked_environment"]["environment"])
    environment["SOURCE_DATE_EPOCH"] = epoch
    build.preflight(matrix, build.TARGET_IDS, environment, root)
    work = root.parent / "work"
    work.mkdir(exist_ok=True)
    require(not work.is_symlink(), "recovery parent must not be a symlink")
    recovery = Path(tempfile.mkdtemp(prefix="fw-r2-repro-", dir=work))
    print(f"Recovery directory (retained on success or failure): {recovery}", flush=True)
    for name in ("f2_r2_build_qualification.json", "f2_r2_reproducibility.json"):
        source = root / "config" / name
        if source.is_file():
            shutil.copy2(source, recovery / f"previous-{name}")
    passes = []
    try:
        move_build_roots(matrix, recovery / "baseline-builds", root)
        for number in (1, 2):
            require(build.clean_repository_commit(root) == commit, "Git input commit changed before pass")
            require(source_snapshot(root, commit) == inputs, "build inputs changed before pass")
            print(f"Starting clean R2 pass {number}/2: 12 jobs, 60 artifacts", flush=True)
            passes.append(run_pass(matrix_path, matrix, environment, commit, root, recovery, number))
            require(build.clean_repository_commit(root) == commit, "repository changed during pass")
            require(source_snapshot(root, commit) == inputs, "build inputs changed during pass")
            if number == 1:
                move_build_roots(matrix, recovery / "pass-1-builds", root)
        comparisons = compare_passes(passes[0]["qualification"], passes[1]["qualification"], recovery / "pass-1-builds", root)
        record = {
            "schema_version": 1, "stage": "F2-R2.5", "status": "two_clean_passes_verified",
            "repo_commit": commit, "source_date_epoch": epoch,
            "checkout_root_sha256": maps.digest(str(root.resolve()).encode()),
            "recovery_directory": recovery.name, "build_inputs": inputs,
            "passes": passes, "comparisons": comparisons, "claims": CLAIMS,
        }
        errors = check_record(record, matrix_path, matrix, root)
        require(not errors, "; ".join(errors))
        build.atomic_write(recovery / "verified-result.json", serialized(record))
        # Nothing canonical is published until BOTH passes and every guard pass.
        require(build.clean_repository_commit(root) == commit, "repository changed before publication")
        publish_records(root, passes[1]["qualification"], record)
        return record
    except Exception as error:
        status = "publication_inconsistent_requires_recovery" if isinstance(error, PublicationRollbackError) else "failed_not_published"
        build.atomic_write(recovery / "failure.json", serialized({"status": status, "reason": str(error), "completed_passes": len(passes)}))
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plan", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--run", action="store_true")
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args()
    try:
        matrix = build.load_json(build.DEFAULT_MATRIX)
        errors = build.validate_matrix(matrix)
        require(not errors, "; ".join(errors))
        validate_policy(matrix, ROOT)
        if args.plan:
            require(not args.write_evidence, "--plan never writes evidence")
            print("F2-R2.5 plan: 2 pristine passes x 12 jobs; compare all 60 artifacts including 16 maps; fixed clean commit/epoch; recover old directories; no target executions or evidence writes")
        elif args.check:
            require(not args.write_evidence, "--check never writes evidence")
            require(OUTPUT.is_file(), "R2 reproducibility evidence is absent; no completed two-pass claim")
            errors = check_record(build.load_json(OUTPUT), build.DEFAULT_MATRIX, matrix)
            require(not errors, "; ".join(errors))
            print("F2-R2.5 evidence verified: two clean passes, all 60 artifacts byte identical and source-path checked, 32 map publication proofs")
        else:
            require(args.write_evidence, "--run requires --write-evidence; partial publication is forbidden")
            run()
            print("F2-R2.5 recorded: 24 genuine clean builds, 60 byte-identical artifact pairs; runtime/HIL remains unproven")
        return 0
    except (build.QualificationError, OSError, ValueError, subprocess.CalledProcessError) as error:
        return build.fail(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
