#!/usr/bin/env python3
"""Validate cross-SDK language, diagnostic, optimization and link policy."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "config" / "build_policy.json"
MATRIX_PATH = REPO_ROOT / "config" / "build_matrix.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    policy = load(POLICY_PATH)
    matrix = load(MATRIX_PATH)
    errors: list[str] = []

    if policy.get("status") != "reviewed":
        errors.append("build policy is not reviewed")
    language = policy.get("language", {})
    if language.get("c") != "C17" or language.get("c_extensions") is not False:
        errors.append("portable C must be strict C17")
    if language.get("cxx") != "C++17" or language.get("cxx_extensions") is not False:
        errors.append("target C++ must be strict C++17")

    required_warnings = set(policy.get("warnings", {}).get("required", []))
    if not {"-Wall", "-Wextra", "-Werror", "-Wformat=2", "-Wshadow", "-Wundef"}.issubset(
        required_warnings
    ):
        errors.append("required warning categories were weakened")

    configs = policy.get("configurations", {})
    if configs.get("debug", {}).get("optimization") != "-Og":
        errors.append("debug must use -Og")
    if configs.get("debug", {}).get("debug_information") != "-g3":
        errors.append("debug must use -g3")
    if configs.get("release", {}).get("optimization") != "-Os":
        errors.append("release must use -Os")
    if configs.get("release", {}).get("debug_information") != "-g1":
        errors.append("release must retain -g1 diagnostics")
    if configs.get("release", {}).get("lto") is not False:
        errors.append("LTO cannot be enabled before F2.4 measurement")

    forbidden = set(policy.get("warnings", {}).get("forbidden", [])) | set(
        policy.get("code_generation", {}).get("forbidden", [])
    )
    flattened = json.dumps(policy, sort_keys=True)
    for flag in forbidden:
        if flattened.count(flag) != 1:
            errors.append(f"forbidden flag must appear only in its registry: {flag}")

    link = policy.get("link", {})
    if link.get("map_file") != "required" or link.get("undefined_symbols") != "error":
        errors.append("map and undefined-symbol link policy must fail closed")
    reproducibility = policy.get("reproducibility", {})
    if reproducibility.get("source_date_epoch") != "required":
        errors.append("SOURCE_DATE_EPOCH must be required")
    if reproducibility.get("absolute_source_paths_in_artifacts") is not False:
        errors.append("absolute source paths must be removed from artifacts")
    if reproducibility.get("network_during_configure_or_build") is not False:
        errors.append("target builds must not resolve network dependencies")

    if matrix.get("build_policy") != "config/build_policy.json":
        errors.append("build matrix does not reference the reviewed policy")
    if set(policy.get("families", {})) != {"esp_idf", "pico_sdk", "ti_mspm0_sdk"}:
        errors.append("policy must cover all three SDK families")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("build policy OK: C17/C++17, strict diagnostics, debug/release maps, 3 SDK families")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
