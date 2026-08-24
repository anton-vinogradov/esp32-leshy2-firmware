#!/usr/bin/env python3
"""Run and record the integrated F2.4.0.6 preflight without target execution."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from toolchain_preflight import REPO_ROOT, validate_exact_environment


OUTPUT = REPO_ROOT / "config" / "f2_4_preflight_review.json"
TARGETS = {"s3", "c5", "rp", "pack", "safety"}


def source_date_epoch() -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%ct"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    value = result.stdout.strip()
    if not value.isdigit():
        raise RuntimeError("git commit timestamp is not a valid SOURCE_DATE_EPOCH")
    return value


def local_environment() -> dict[str, str]:
    root = REPO_ROOT / ".toolchains"
    esp_tools = root / "esp-tools"
    ti_root = root / "tools/ti-cgt-armllvm-4.0.5.LTS/ti-cgt-armllvm_4.0.5.LTS"
    sysconfig_root = root / "tools/ti-sysconfig-1.28.0.4712"
    arm_root = root / "tools/arm-gnu-toolchain-15.2.rel1-darwin-arm64-arm-none-eabi"
    path_entries = (
        root / "python/idf6_py3.12_env/bin",
        esp_tools / "tools/cmake/4.0.3/CMake.app/Contents/bin",
        esp_tools / "tools/ninja/1.12.1",
        esp_tools / "tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin",
        esp_tools / "tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin",
        esp_tools / "tools/xtensa-esp-elf-gdb/17.1_20260402/xtensa-esp-elf-gdb/bin",
        esp_tools / "tools/riscv32-esp-elf-gdb/17.1_20260402/riscv32-esp-elf-gdb/bin",
        esp_tools / "tools/esp32ulp-elf/2.38_20240113/esp32ulp-elf/bin",
        esp_tools / "tools/openocd-esp32/v0.12.0-esp32-20260424/openocd-esp32/bin",
        arm_root / "bin",
        ti_root / "bin",
        sysconfig_root,
    )
    environment = dict(os.environ)
    environment.update(
        {
            "IDF_PATH": str(root / "src/esp-idf"),
            "IDF_TOOLS_PATH": str(esp_tools),
            "IDF_PYTHON_ENV_PATH": str(root / "python/idf6_py3.12_env"),
            "ESP_IDF_VERSION": "6.0",
            "IDF_COMPONENT_MANAGER": "0",
            "ESP_ROM_ELF_DIR": str(
                esp_tools / "tools/esp-rom-elfs/20241011"
            ),
            "PICO_SDK_PATH": str(root / "src/pico-sdk"),
            "ARM_GNU_TOOLCHAIN_PATH": str(arm_root),
            "PICOTOOL_FETCH_FROM_GIT_PATH": str(root / "src/picotool-2.3.0"),
            "MSPM0_SDK_PATH": str(root / "src/mspm0-sdk"),
            "TI_ARM_CLANG_PATH": str(ti_root),
            "SYSCONFIG_PATH": str(sysconfig_root),
            "SOURCE_DATE_EPOCH": source_date_epoch(),
            "PATH": os.pathsep.join(str(path) for path in path_entries)
            + os.pathsep
            + environment.get("PATH", ""),
        }
    )
    return environment


def integrated_review() -> dict:
    environment = local_environment()
    errors, evidence = validate_exact_environment(TARGETS, environment)
    dispatcher_results = []
    for configuration in ("debug", "release"):
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "tools/build_targets.py"),
                "preflight",
                "--target",
                "all",
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
        dispatcher_results.append(
            {
                "configuration": configuration,
                "status": "passed" if result.returncode == 0 else "failed",
                "summary": result.stdout.strip().splitlines()[-1]
                if result.stdout.strip()
                else "no output",
            }
        )
        if result.returncode != 0:
            errors.append(f"dispatcher:{configuration}: {result.stdout.strip()}")
    if errors:
        raise RuntimeError("\n".join(errors))
    return {
        "schema_version": 1,
        "stage": "F2.4.0.6",
        "status": "reviewed",
        "host_profile": evidence["host_profile"],
        "targets": sorted(TARGETS),
        "configurations": ["debug", "release"],
        "exact_environment": evidence,
        "dispatcher_preflight": dispatcher_results,
        "network_during_preflight": False,
        "target_execution": {
            "configure_runs": 0,
            "build_runs": 0,
            "emulator_runs": 0,
        },
        "next": "F2.4.1",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = integrated_review()
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    serialized = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        OUTPUT.write_text(serialized, encoding="utf-8")
    elif not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != serialized:
        print(f"ERROR: stale integrated evidence: {OUTPUT}", file=sys.stderr)
        return 1
    print(
        "F2.4.0.6 preflight review OK: "
        f"{result['exact_environment']['passed']} exact checks, 5 targets, "
        "debug/release, 0 target executions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
