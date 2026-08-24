#!/usr/bin/env python3
"""Canonical shell-free command dispatcher for all Leshy2 firmware targets."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from toolchain_preflight import validate_exact_environment


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = REPO_ROOT / "config" / "build_matrix.json"
ENV_TOKEN = re.compile(r"\{env:([A-Z0-9_]+)\}")
TARGET_IDS = {"s3", "c5", "rp", "pack", "safety"}
FAMILIES = {"esp_idf", "pico_sdk", "ti_mspm0_sdk"}


def load_matrix(path: Path) -> dict:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def validate_matrix(matrix: dict) -> list[str]:
    errors: list[str] = []
    targets = matrix.get("targets", [])
    ids = [target.get("id") for target in targets]
    if set(ids) != TARGET_IDS or len(ids) != len(TARGET_IDS):
        errors.append(f"target set must be {sorted(TARGET_IDS)}, got {ids}")
    if matrix.get("status") != "reviewed":
        errors.append("matrix status must be reviewed")
    policy = matrix.get("policy", {})
    if policy.get("shell_execution") is not False:
        errors.append("shell execution must be disabled")
    if policy.get("network_during_configure_or_build") is not False:
        errors.append("configure/build network access must be disabled")

    for target in targets:
        target_id = target.get("id", "?")
        if target.get("family") not in FAMILIES:
            errors.append(f"{target_id}: unknown family")
        if not target.get("project_dir", "").startswith("targets/"):
            errors.append(f"{target_id}: project directory must stay under targets/")
        commands = target.get("commands", {})
        for action in ("configure", "build", "clean"):
            command = commands.get(action)
            if not isinstance(command, list) or not command:
                errors.append(f"{target_id}: missing {action} command")
            elif not all(isinstance(item, str) and item for item in command):
                errors.append(f"{target_id}: invalid {action} argument")
        artifacts = target.get("artifacts", [])
        if not artifacts or len(artifacts) != len(set(artifacts)):
            errors.append(f"{target_id}: artifacts must be non-empty and unique")
        if target.get("size_gate", {}).get("image") not in artifacts:
            errors.append(f"{target_id}: size-gate image is not a declared artifact")

    return errors


def select_targets(matrix: dict, requested: str) -> list[dict]:
    if requested == "all":
        return matrix["targets"]
    return [target for target in matrix["targets"] if target["id"] == requested]


def context(target: dict, configuration: str) -> dict[str, str]:
    build = REPO_ROOT / "build" / "targets" / target["id"] / configuration
    cmake_type = "Debug" if configuration == "debug" else "Release"
    return {
        "repo": str(REPO_ROOT),
        "build": str(build),
        "config": configuration,
        "cmake_build_type": cmake_type,
        "python": sys.executable,
    }


def render(argument: str, values: dict[str, str], strict_env: bool) -> str:
    def replace_env(match: re.Match[str]) -> str:
        name = match.group(1)
        value = os.environ.get(name)
        if value is None:
            if strict_env:
                raise KeyError(name)
            return f"${name}"
        return value

    rendered = ENV_TOKEN.sub(replace_env, argument)
    return rendered.format_map(values)


def rendered_command(
    target: dict, action: str, configuration: str, strict_env: bool
) -> list[str]:
    values = context(target, configuration)
    return [
        render(argument, values, strict_env)
        for argument in target["commands"][action]
    ]


def preflight(target: dict, configuration: str) -> list[str]:
    errors: list[str] = []
    if sys.version_info[:2] != (3, 12):
        errors.append(
            f"{target['id']}: target orchestration requires Python 3.12, "
            f"got {sys.version_info.major}.{sys.version_info.minor}"
        )
    project = REPO_ROOT / target["project_dir"]
    if not project.is_dir():
        errors.append(f"{target['id']}: project not created yet: {project}")
    for name in target["required_environment"]:
        value = os.environ.get(name)
        if not value:
            errors.append(f"{target['id']}: required environment is unset: {name}")
        elif not Path(value).exists():
            errors.append(f"{target['id']}: {name} path does not exist: {value}")
    try:
        command = rendered_command(target, "configure", configuration, strict_env=True)
    except KeyError:
        command = []
    if command and "/" not in command[0] and shutil.which(command[0]) is None:
        errors.append(f"{target['id']}: executable not found: {command[0]}")
    return errors


def print_command(target: dict, action: str, configuration: str) -> None:
    command = rendered_command(target, action, configuration, strict_env=False)
    print(f"{target['id']}:{configuration}:{action}")
    print(json.dumps(command, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=(
            "list",
            "verify-matrix",
            "preflight",
            "configure",
            "build",
            "clean",
            "verify",
            "artifacts",
        ),
    )
    parser.add_argument("--target", choices=("all", *sorted(TARGET_IDS)), default="all")
    parser.add_argument("--config", choices=("debug", "release"), default="debug")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    args = parser.parse_args()

    matrix = load_matrix(args.matrix)
    errors = validate_matrix(matrix)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.action == "verify-matrix":
        print(f"build matrix OK: {len(matrix['targets'])} targets, 2 configurations")
        return 0

    targets = select_targets(matrix, args.target)
    if args.action == "list":
        for target in targets:
            print(f"{target['id']}\t{target['family']}\t{target['sdk_target']}")
        return 0
    if args.action == "artifacts":
        for target in targets:
            build = Path(context(target, args.config)["build"])
            for artifact in target["artifacts"]:
                print(build / artifact)
        return 0
    if args.action == "preflight":
        exact_failures, exact_evidence = validate_exact_environment(
            {target["id"] for target in targets}
        )
        failures = exact_failures + [
            error for target in targets for error in preflight(target, args.config)
        ]
        if failures:
            for failure in failures:
                print(f"ERROR: {failure}", file=sys.stderr)
            return 1
        print(
            f"preflight OK: {len(targets)} target(s), {args.config}; "
            f"{exact_evidence['passed']} exact environment checks"
        )
        return 0

    if args.action == "verify":
        missing: list[Path] = []
        for target in targets:
            build = Path(context(target, args.config)["build"])
            for artifact in target["artifacts"]:
                path = build / artifact
                if not path.is_file():
                    missing.append(path)
            image = build / target["size_gate"]["image"]
            if image.is_file():
                subprocess.run(
                    [
                        sys.executable,
                        str(REPO_ROOT / "tools" / "check_image_size.py"),
                        "--target",
                        target["size_gate"]["target"],
                        "--image",
                        str(image),
                    ],
                    check=True,
                )
        if missing:
            for path in missing:
                print(f"ERROR: missing artifact: {path}", file=sys.stderr)
            return 1
        return 0

    if not args.dry_run:
        exact_failures, _ = validate_exact_environment(
            {target["id"] for target in targets}
        )
        if exact_failures:
            for failure in exact_failures:
                print(f"ERROR: {failure}", file=sys.stderr)
            return 1

    for target in targets:
        if not args.dry_run:
            failures = preflight(target, args.config)
            if failures:
                for failure in failures:
                    print(f"ERROR: {failure}", file=sys.stderr)
                return 1
        command = rendered_command(
            target, args.action, args.config, strict_env=not args.dry_run
        )
        if args.dry_run:
            print_command(target, args.action, args.config)
        else:
            subprocess.run(command, cwd=REPO_ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
