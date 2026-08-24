#!/usr/bin/env python3
"""Fail-closed validation of the exact Leshy2 build environment."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = REPO_ROOT / "environment" / "toolchains.lock.json"
PROGRESS_PATH = REPO_ROOT / "config" / "f2_4_preflight_progress.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _run(arguments: list[str], environment: dict[str, str]) -> tuple[int, str]:
    try:
        result = subprocess.run(
            arguments,
            cwd=REPO_ROOT,
            env=environment,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except OSError as error:
        return 127, str(error)
    return result.returncode, result.stdout.strip()


def _record(
    checks: list[dict], errors: list[str], check_id: str, expected: str, observed: str
) -> None:
    passed = expected in observed
    observed_lines = observed.splitlines()
    summary = next(
        (line for line in observed_lines if expected in line),
        observed_lines[0] if observed_lines else "",
    )
    checks.append(
        {
            "id": check_id,
            "status": "passed" if passed else "failed",
            "expected": expected,
            "observed": summary,
        }
    )
    if not passed:
        errors.append(f"{check_id}: expected {expected!r}, got {observed!r}")


def _command_check(
    checks: list[dict],
    errors: list[str],
    environment: dict[str, str],
    check_id: str,
    command: str,
    expected_output: str,
    expected_path_token: str = "",
) -> None:
    executable = shutil.which(command, path=environment.get("PATH"))
    if executable is None:
        errors.append(f"{check_id}: executable not found: {command}")
        checks.append(
            {
                "id": check_id,
                "status": "failed",
                "expected": expected_output,
                "observed": "executable not found",
            }
        )
        return
    if expected_path_token and expected_path_token not in executable:
        errors.append(
            f"{check_id}: executable path does not contain locked version "
            f"{expected_path_token!r}: {executable}"
        )
    returncode, output = _run([executable, "--version"], environment)
    if returncode != 0:
        errors.append(f"{check_id}: version command failed: {output}")
    _record(checks, errors, check_id, expected_output, output)


def _host_profile() -> str:
    machine = platform.machine().lower()
    if sys.platform == "darwin" and machine == "arm64":
        return "macos_arm64"
    if sys.platform.startswith("linux") and machine in {"x86_64", "amd64"}:
        return "linux_x86_64"
    return f"unsupported:{sys.platform}:{machine}"


def validate_exact_environment(
    target_ids: set[str], environment: dict[str, str] | None = None
) -> tuple[list[str], dict]:
    """Return errors and path-free evidence for the selected physical targets."""

    env = dict(os.environ if environment is None else environment)
    lock = _load(LOCK_PATH)
    progress = _load(PROGRESS_PATH)
    checks: list[dict] = []
    errors: list[str] = []
    host_profile = _host_profile()
    if host_profile not in lock["host_profiles"]:
        errors.append(f"unsupported build host: {host_profile}")

    expected_python = lock["host_profiles"].get(host_profile, {}).get("python", "")
    _record(checks, errors, "python-version", expected_python, platform.python_version())
    python_env = env.get("IDF_PYTHON_ENV_PATH", "")
    if not python_env:
        errors.append("IDF_PYTHON_ENV_PATH is unset")
    else:
        expected_prefix = str(Path(python_env).resolve())
        observed_prefix = str(Path(sys.prefix).resolve())
        _record(
            checks,
            errors,
            "python-environment",
            "active",
            "active" if expected_prefix == observed_prefix else "different environment",
        )
    returncode, pip_output = _run([sys.executable, "-m", "pip", "check"], env)
    if returncode != 0:
        errors.append(f"python-packages: pip check failed: {pip_output}")
    _record(checks, errors, "python-packages", "No broken requirements found", pip_output)

    for item in lock["local_locks"]:
        path = REPO_ROOT / item["path"]
        observed = _sha256(path) if path.is_file() else "missing"
        _record(checks, errors, f"lock:{item['id']}", item["sha256"], observed)

    source_env = {
        "esp-idf": "IDF_PATH",
        "pico-sdk": "PICO_SDK_PATH",
        "mspm0-sdk": "MSPM0_SDK_PATH",
    }
    needed_sources = set()
    if target_ids & {"s3", "c5"}:
        needed_sources.add("esp-idf")
    if "rp" in target_ids:
        needed_sources.add("pico-sdk")
    if target_ids & {"pack", "safety"}:
        needed_sources.add("mspm0-sdk")
    source_revisions = {item["id"]: item for item in lock["source_revisions"]}
    for source_id in sorted(needed_sources):
        variable = source_env[source_id]
        source_path = env.get(variable, "")
        expected_commit = source_revisions[source_id]["commit"]
        if not source_path or not Path(source_path).is_dir():
            errors.append(f"source:{source_id}: invalid {variable}")
            observed_commit = "missing"
        else:
            returncode, observed_commit = _run(
                ["git", "-C", source_path, "rev-parse", "HEAD"], env
            )
            if returncode != 0:
                errors.append(f"source:{source_id}: cannot read Git HEAD")
        _record(
            checks,
            errors,
            f"source:{source_id}",
            expected_commit,
            observed_commit,
        )

    versions = progress["substeps"]
    shared = versions["F2.4.0.3"]["versions"]
    _command_check(checks, errors, env, "tool:cmake", "cmake", shared["cmake"])
    _command_check(checks, errors, env, "tool:ninja", "ninja", shared["ninja"])

    if target_ids & {"s3", "c5"}:
        esp = versions["F2.4.0.2"]["versions"]
        _record(
            checks,
            errors,
            "esp-idf-environment-version",
            "6.0",
            env.get("ESP_IDF_VERSION", "unset"),
        )
        _record(
            checks,
            errors,
            "esp-component-manager-offline",
            "0",
            env.get("IDF_COMPONENT_MANAGER", "unset"),
        )
        for check_id, command, output_token, path_token in (
            ("tool:xtensa-esp-elf", "xtensa-esp32s3-elf-gcc", esp["xtensa-esp-elf"], esp["xtensa-esp-elf"]),
            ("tool:riscv32-esp-elf", "riscv32-esp-elf-gcc", esp["riscv32-esp-elf"], esp["riscv32-esp-elf"]),
            ("tool:xtensa-gdb", "xtensa-esp32s3-elf-gdb", f"GNU gdb (esp-gdb) {esp['xtensa-esp-elf-gdb']}", esp["xtensa-esp-elf-gdb"]),
            ("tool:riscv-gdb", "riscv32-esp-elf-gdb", f"GNU gdb (esp-gdb) {esp['riscv32-esp-elf-gdb']}", esp["riscv32-esp-elf-gdb"]),
            ("tool:esp32ulp", "esp32ulp-elf-as", "2.38", esp["esp32ulp-elf"]),
            ("tool:openocd", "openocd", "0.12.0", esp["openocd-esp32"]),
        ):
            _command_check(
                checks, errors, env, check_id, command, output_token, path_token
            )
        tools_root = Path(env.get("IDF_TOOLS_PATH", ""))
        rom_root = tools_root / "tools" / "esp-rom-elfs" / esp["esp-rom-elfs"]
        _record(
            checks,
            errors,
            "esp-rom-environment",
            "active",
            "active"
            if Path(env.get("ESP_ROM_ELF_DIR", "")).resolve() == rom_root.resolve()
            else "different directory",
        )
        for rom_name in ("esp32s3_rev0_rom.elf", "esp32c5_rev0_rom.elf"):
            observed = "present" if (rom_root / rom_name).is_file() else "missing"
            _record(checks, errors, f"rom:{rom_name}", "present", observed)

    if "rp" in target_ids:
        arm_root = Path(env.get("ARM_GNU_TOOLCHAIN_PATH", ""))
        command = arm_root / "bin" / "arm-none-eabi-gcc"
        returncode, output = _run([str(command), "--version"], env)
        if returncode != 0:
            errors.append(f"tool:arm-none-eabi: version command failed: {output}")
        _record(
            checks,
            errors,
            "tool:arm-none-eabi",
            "15.2.1 20251203",
            output,
        )

    if target_ids & {"pack", "safety"}:
        ti_root = Path(env.get("TI_ARM_CLANG_PATH", ""))
        sysconfig_root = Path(env.get("SYSCONFIG_PATH", ""))
        ti_versions = versions["F2.4.0.5"]["versions"]
        for check_id, command, expected in (
            ("tool:tiarmclang", ti_root / "bin" / "tiarmclang", ti_versions["tiarmclang"]),
            ("tool:tiarmobjcopy", ti_root / "bin" / "tiarmobjcopy", "TI LLVM version 18.1.8"),
            ("tool:sysconfig", sysconfig_root / "sysconfig_cli.sh", ti_versions["sysconfig"]),
        ):
            returncode, output = _run([str(command), "--version"], env)
            if returncode != 0:
                errors.append(f"{check_id}: version command failed: {output}")
            _record(checks, errors, check_id, expected, output)
        sdk_root = Path(env.get("MSPM0_SDK_PATH", ""))
        required_inputs = {
            "mspm0-startup": sdk_root / "source/ti/devices/msp/m0p/startup_system_files/ticlang/startup_mspm0c1105_c1106_ticlang.c",
            "mspm0-driverlib": sdk_root / "source/ti/driverlib/lib/ticlang/m0p/mspm0c1105_c1106/driverlib.a",
            "mspm0-product": sdk_root / ".metadata/product.json",
        }
        for check_id, path in required_inputs.items():
            _record(
                checks,
                errors,
                check_id,
                "present",
                "present" if path.is_file() else "missing",
            )

    return errors, {
        "host_profile": host_profile,
        "targets": sorted(target_ids),
        "checks": checks,
        "passed": sum(check["status"] == "passed" for check in checks),
        "failed": sum(check["status"] == "failed" for check in checks),
    }
