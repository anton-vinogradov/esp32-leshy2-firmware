#!/usr/bin/env python3
"""Run and verify two canonical clean builds for every firmware artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from capture_target_build_review import capture as capture_target
from review_f2_4_builds import aggregate as aggregate_builds
from review_f2_4_preflight import local_environment


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = (REPO_ROOT / "build" / "targets").resolve()
MATRIX_PATH = REPO_ROOT / "config" / "build_matrix.json"
OUTPUT_PATH = REPO_ROOT / "config" / "f2_5_reproducibility_review.json"
TARGETS = ("s3", "c5", "rp", "pack", "safety")
CONFIGURATIONS = ("debug", "release")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def reset_build(target: str, configuration: str) -> None:
    path = (BUILD_ROOT / target / configuration).resolve()
    expected_parent = (BUILD_ROOT / target).resolve()
    if path.parent != expected_parent or target not in TARGETS or configuration not in CONFIGURATIONS:
        raise RuntimeError(f"refusing unsafe build reset: {path}")
    if path.exists():
        shutil.rmtree(path)


def run_action(target: str, configuration: str, action: str, environment: dict[str, str]) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools" / "build_targets.py"),
            action,
            "--target",
            target,
            "--config",
            configuration,
        ],
        cwd=REPO_ROOT,
        env=environment,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{target}:{configuration}:{action} failed\n{result.stdout}"
        )


def artifact_manifest(matrix: dict[str, object]) -> dict[str, dict[str, int | str]]:
    manifest: dict[str, dict[str, int | str]] = {}
    for target in matrix["targets"]:
        target_id = target["id"]
        for configuration in CONFIGURATIONS:
            root = BUILD_ROOT / target_id / configuration
            for relative in target["artifacts"]:
                path = root / relative
                if not path.is_file():
                    raise RuntimeError(f"missing reproducibility artifact: {path}")
                key = str(path.relative_to(REPO_ROOT))
                manifest[key] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    return dict(sorted(manifest.items()))


def distributable_path_scan(manifest: dict[str, dict[str, int | str]]) -> tuple[int, list[str]]:
    needle = str(REPO_ROOT).encode("utf-8")
    scanned = 0
    leaks: list[str] = []
    for relative in manifest:
        if not relative.endswith((".bin", ".uf2")):
            continue
        scanned += 1
        if needle in (REPO_ROOT / relative).read_bytes():
            leaks.append(relative)
    return scanned, leaks


def write_refreshed_build_evidence() -> None:
    for target in TARGETS:
        path = REPO_ROOT / "config" / f"f2_4_{target}_build_review.json"
        path.write_text(
            json.dumps(capture_target(target), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    integrated, errors = aggregate_builds()
    if errors:
        raise RuntimeError("\n".join(errors))
    (REPO_ROOT / "config" / "f2_4_build_review.json").write_text(
        json.dumps(integrated, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def run_review() -> dict[str, object]:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    environment = local_environment()
    passes: list[dict[str, dict[str, int | str]]] = []
    for pass_index in range(2):
        for target in TARGETS:
            for configuration in CONFIGURATIONS:
                reset_build(target, configuration)
                run_action(target, configuration, "configure", environment)
                run_action(target, configuration, "build", environment)
                run_action(target, configuration, "verify", environment)
        manifest = artifact_manifest(matrix)
        if len(manifest) != 52:
            raise RuntimeError(f"pass {pass_index + 1}: expected 52 artifacts")
        passes.append(manifest)

    mismatches = [
        path
        for path in passes[0]
        if passes[0][path] != passes[1].get(path)
    ]
    if mismatches:
        raise RuntimeError(
            "non-reproducible artifacts:\n" + "\n".join(mismatches)
        )
    scanned, path_leaks = distributable_path_scan(passes[1])
    if path_leaks:
        raise RuntimeError(
            "absolute workspace path leaked into distributable images:\n"
            + "\n".join(path_leaks)
        )

    write_refreshed_build_evidence()
    integrated_path = REPO_ROOT / "config" / "f2_4_build_review.json"
    return {
        "schema_version": 1,
        "stage": "F2.5",
        "status": "reviewed",
        "scope": "two clean canonical builds of every debug/release target artifact",
        "source_date_epoch": environment["SOURCE_DATE_EPOCH"],
        "passes": 2,
        "targets": 5,
        "configurations_per_pass": 10,
        "artifact_instances_per_pass": 52,
        "byte_identical_artifacts": 52,
        "distributable_images_scanned_for_absolute_workspace_path": scanned,
        "absolute_workspace_path_leaks": 0,
        "final_manifest": passes[1],
        "inputs": {
            "build_matrix": {
                "path": "config/build_matrix.json",
                "sha256": sha256(MATRIX_PATH),
            },
            "build_policy": {
                "path": "config/build_policy.json",
                "sha256": sha256(REPO_ROOT / "config" / "build_policy.json"),
            },
            "integrated_build_review": {
                "path": "config/f2_4_build_review.json",
                "sha256": sha256(integrated_path),
            },
        },
        "claims": {
            "canonical_path_clean_rebuild_is_byte_reproducible": True,
            "distributable_images_hide_absolute_workspace_path": True,
            "network_during_configure_or_build": False,
            "runtime_boot_proven": False,
            "cross_workspace_path_reproducibility_proven": False,
            "hardware_proven": False,
        },
        "next": "F3",
        "runner": "tools/review_f2_5_reproducibility.py",
    }


def check_review() -> list[str]:
    errors: list[str] = []
    if not OUTPUT_PATH.is_file():
        return ["missing F2.5 reproducibility evidence"]
    review = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    expected_scalars = {
        "stage": "F2.5",
        "status": "reviewed",
        "passes": 2,
        "targets": 5,
        "configurations_per_pass": 10,
        "artifact_instances_per_pass": 52,
        "byte_identical_artifacts": 52,
        "absolute_workspace_path_leaks": 0,
        "next": "F3",
    }
    for key, expected in expected_scalars.items():
        if review.get(key) != expected:
            errors.append(f"F2.5 {key} changed")
    if not str(review.get("source_date_epoch", "")).isdigit():
        errors.append("F2.5 SOURCE_DATE_EPOCH is invalid")
    manifest = review.get("final_manifest", {})
    if len(manifest) != 52:
        errors.append("F2.5 final manifest must contain 52 artifacts")
    for record in manifest.values():
        if len(record.get("sha256", "")) != 64 or record.get("bytes", 0) <= 0:
            errors.append("F2.5 final manifest record is invalid")
            break
    for record in review.get("inputs", {}).values():
        path = REPO_ROOT / record.get("path", "")
        if not path.is_file() or sha256(path) != record.get("sha256"):
            errors.append(f"F2.5 input is stale: {record.get('path')}")
    claims = review.get("claims", {})
    if claims.get("canonical_path_clean_rebuild_is_byte_reproducible") is not True:
        errors.append("F2.5 byte reproducibility claim is missing")
    if claims.get("runtime_boot_proven") is not False:
        errors.append("F2.5 may not claim runtime boot")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.run:
            result = run_review()
            OUTPUT_PATH.write_text(
                json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        else:
            errors = check_review()
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        "F2.5 reproducibility review OK: 2 clean passes, 5 targets, "
        "10 configurations/pass, 52/52 byte-identical artifacts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
