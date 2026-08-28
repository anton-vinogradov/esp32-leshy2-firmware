#!/usr/bin/env python3
"""Validate the exact six-target F2-R2.1 build matrix without running it."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "config" / "f2_r2_build_matrix.json"
TARGET_IDS = ["s3", "c5", "rf_rp", "hub_rp", "pack", "safety"]
CONFIGURATIONS = ["debug", "release"]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    matrix = load("config/f2_r2_build_matrix.json")
    errors: list[str] = []
    if matrix.get("stage") != "F2-R2.1" or matrix.get("status") != "reviewed_matrix":
        errors.append("F2-R2.1 matrix is not reviewed")

    for source in [*matrix.get("inputs", {}).values(), *matrix.get("size_gate_sources", {}).values()]:
        path = ROOT / source.get("path", "")
        if not path.is_file():
            errors.append(f"missing locked input: {source.get('path')}")
            continue
        if digest(path) != source.get("sha256"):
            errors.append(f"stale locked input: {source.get('path')}")

    identities = load("config/f0_r2_target_identity_contract.json")
    identity_rows = identities.get("targets", [])
    if [row.get("id") for row in identity_rows] != TARGET_IDS:
        errors.append("reviewed target identity order changed")
    identity_by_id = {row["id"]: row for row in identity_rows}
    targets = matrix.get("targets", [])
    if [row.get("id") for row in targets] != TARGET_IDS:
        errors.append("matrix does not contain the exact six target identities")
    target_by_id = {row.get("id"): row for row in targets}
    for target_id in TARGET_IDS:
        actual = target_by_id.get(target_id, {})
        expected = identity_by_id.get(target_id, {})
        for key in ("family", "sdk_target", "project_dir", "project_name"):
            if actual.get(key) != expected.get(key):
                errors.append(f"{target_id}: {key} differs from the identity contract")

    if list(matrix.get("configurations", {})) != CONFIGURATIONS:
        errors.append("debug/release configuration order changed")
    expected_jobs = [
        {
            "target": target,
            "configuration": configuration,
            "build_dir": f"build/r2/targets/{target}/{configuration}",
        }
        for target, configuration in itertools.product(TARGET_IDS, CONFIGURATIONS)
    ]
    if matrix.get("jobs") != expected_jobs:
        errors.append("matrix is not the exact 6x2 Cartesian build set")

    forbidden_argv = {"sh", "bash", "zsh", "-c", "&&", "||", "|"}
    artifact_count = 0
    map_count = 0
    size_gate_count = 0
    for target_id in TARGET_IDS:
        target = target_by_id.get(target_id, {})
        commands = target.get("commands", {})
        if set(commands) != {"configure", "build", "clean"}:
            errors.append(f"{target_id}: configure/build/clean command set is incomplete")
        for name, argv in commands.items():
            if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) for arg in argv):
                errors.append(f"{target_id}: {name} is not a non-empty argv array")
                continue
            if any(arg in forbidden_argv for arg in argv):
                errors.append(f"{target_id}: {name} uses a shell boundary")
        artifacts = target.get("artifacts", [])
        paths = [row.get("path") for row in artifacts]
        if len(paths) != len(set(paths)) or not all(path and path.startswith("{build}/") for path in paths):
            errors.append(f"{target_id}: artifact paths are missing, duplicated or outside the build root")
        if not any(row.get("kind") in {"map", "boot_map"} for row in artifacts):
            errors.append(f"{target_id}: no map artifact is declared")
        artifact_count += len(artifacts) * len(CONFIGURATIONS)
        map_count += sum(row.get("kind") in {"map", "boot_map"} for row in artifacts) * len(CONFIGURATIONS)
        size_gate_count += len(target.get("size_gates", [])) * len(CONFIGURATIONS)
        gate = target.get("execution_gate", {})
        if gate.get("target_build") != "not_run_until_F2-R2.4":
            errors.append(f"{target_id}: target execution gate is not fail-closed")
        if gate.get("development_board") is None or "not_run" not in gate.get("development_board", ""):
            errors.append(f"{target_id}: development-board execution is not explicit")
        if gate.get("leshy2_hil") != "not_run":
            errors.append(f"{target_id}: HIL execution is not explicit")

    memory = {row["id"]: row for row in load(
        "config/f0_r2_memory_rollback_contract.json"
    )["targets"]}
    for target_id in TARGET_IDS:
        target = target_by_id.get(target_id, {})
        identity = identity_by_id[target_id]
        gates = target.get("size_gates", [])
        app_path = f"{{build}}/{identity['application_image']}.bin"
        app = next((row for row in gates if row.get("artifact") == app_path), None)
        if app is None or app.get("maximum_bytes") != memory[target_id]["maximum_image_bytes"]:
            errors.append(f"{target_id}: application size gate differs from rollback geometry")
        if target_id in {"pack", "safety"}:
            boot_path = f"{{build}}/{identity['boot_image']}.bin"
            boot = next((row for row in gates if row.get("artifact") == boot_path), None)
            if boot is None or boot.get("maximum_bytes") != 16384:
                errors.append(f"{target_id}: protected boot size gate is missing")

    lock = load("environment/toolchains.lock.json")
    source_locks = {row["id"]: row for row in lock.get("source_revisions", [])}
    archive_locks = {row["id"]: row for row in lock.get("archives", [])}
    families = matrix.get("toolchain_families", {})
    expected_sources = {
        "esp_idf": ("esp-idf", "v6.0.2", "7101770dc6db2667b3c477cc31365dd1acd6db4e"),
        "pico_sdk": ("pico-sdk", "2.3.0", "98a542c1a62fb549ffb5d66a3e5892b06276b670"),
        "ti_mspm0_sdk": ("mspm0-sdk", "2.11.00.07", "20807db79aa17b49f87ab8ec87f6b6d63ee2cb32"),
    }
    for family_id, (lock_id, version, commit) in expected_sources.items():
        family = families.get(family_id, {})
        if (family.get("source_lock_id"), family.get("version"), family.get("commit")) != (lock_id, version, commit):
            errors.append(f"{family_id}: production SDK identity changed")
        source = source_locks.get(lock_id, {})
        if source.get("version") != version or source.get("commit") != commit:
            errors.append(f"{family_id}: source revision is not backed by the toolchain lock")

    archive_ids: list[str] = []
    archive_ids.extend(families.get("esp_idf", {}).get("target_compilers", {}).get("s3", {}).get("archive_lock_ids", []))
    archive_ids.extend(families.get("esp_idf", {}).get("target_compilers", {}).get("c5", {}).get("archive_lock_ids", []))
    archive_ids.extend(families.get("pico_sdk", {}).get("compiler", {}).get("archive_lock_ids", []))
    ti = families.get("ti_mspm0_sdk", {})
    archive_ids.extend(ti.get("compiler", {}).get("archive_lock_ids", []))
    archive_ids.extend(ti.get("sysconfig", {}).get("archive_lock_ids", []))
    archive_ids.extend(ti.get("sdk_archive_lock_ids", []))
    for lock_id in archive_ids:
        record = archive_locks.get(lock_id, {})
        if len(record.get("sha256", "")) != 64:
            errors.append(f"missing SHA-256 archive lock: {lock_id}")

    expected_archives = {
        "esp-xtensa-gcc-linux_x86_64": ("xtensa-esp-elf", "esp-15.2.0_20251204", "linux_x86_64"),
        "esp-xtensa-gcc-macos_arm64": ("xtensa-esp-elf", "esp-15.2.0_20251204", "macos_arm64"),
        "esp-riscv-gcc-linux_x86_64": ("riscv32-esp-elf", "esp-15.2.0_20251204", "linux_x86_64"),
        "esp-riscv-gcc-macos_arm64": ("riscv32-esp-elf", "esp-15.2.0_20251204", "macos_arm64"),
        "arm-gnu-linux_x86_64": ("arm-none-eabi", "15.2.Rel1", "linux_x86_64"),
        "arm-gnu-macos_arm64": ("arm-none-eabi", "15.2.Rel1", "macos_arm64"),
        "ti-arm-clang-linux_x86_64": ("ti-arm-clang", "4.0.5.LTS", "linux_x86_64"),
        "ti-arm-clang-macos_arm64": ("ti-arm-clang", "4.0.5.LTS", "macos_arm64"),
        "ti-sysconfig-linux_x86_64": ("sysconfig", "1.28.0.4712", "linux_x86_64"),
        "ti-sysconfig-macos_arm64": ("sysconfig", "1.28.0.4712", "macos_arm64"),
        "ti-mspm0-sdk-linux_x86_64": ("mspm0-sdk", "2.11.00.07", "linux_x86_64"),
        "ti-mspm0-sdk-macos_arm64": ("mspm0-sdk", "2.11.00.07", "macos_arm64"),
    }
    for lock_id, expected in expected_archives.items():
        record = archive_locks.get(lock_id, {})
        if (record.get("tool"), record.get("version"), record.get("host")) != expected:
            errors.append(f"archive identity changed: {lock_id}")

    expected_versions = {
        "s3": ("xtensa-esp-elf", "esp-15.2.0_20251204"),
        "c5": ("riscv32-esp-elf", "esp-15.2.0_20251204"),
    }
    for target_id, expected in expected_versions.items():
        compiler = families.get("esp_idf", {}).get("target_compilers", {}).get(target_id, {})
        if (compiler.get("name"), compiler.get("version")) != expected:
            errors.append(f"{target_id}: compiler identity changed")
    if (families.get("pico_sdk", {}).get("compiler", {}).get("name"), families.get("pico_sdk", {}).get("compiler", {}).get("version")) != ("arm-none-eabi", "15.2.Rel1"):
        errors.append("RP compiler identity changed")
    if ti.get("compiler", {}).get("version") != "4.0.5.LTS" or ti.get("sysconfig", {}).get("version") != "1.28.0.4712":
        errors.append("TI compiler or SysConfig identity changed")

    locked = matrix.get("locked_environment", {})
    if matrix.get("host_profiles") != ["linux_x86_64", "macos_arm64"]:
        errors.append("canonical host profiles changed")
    if locked.get("network_during_configure_or_build") is not False:
        errors.append("network is not disabled during configure/build")
    if locked.get("floating_versions_allowed") is not False:
        errors.append("floating toolchain versions are allowed")
    if locked.get("environment", {}).get("IDF_COMPONENT_MANAGER") != "0":
        errors.append("ESP Component Manager is not disabled")
    if locked.get("environment", {}).get("FETCHCONTENT_FULLY_DISCONNECTED") != "ON":
        errors.append("Pico FetchContent is not offline")
    if locked.get("command_form") != "argv_only_no_shell":
        errors.append("command form is not shell-free argv")
    local_locks = {row["id"]: row for row in lock.get("local_locks", [])}
    python_lock = local_locks.get("esp-idf-python-lock", {})
    python_path = ROOT / locked.get("python_lock", "")
    if not python_path.is_file() or digest(python_path) != python_lock.get("sha256"):
        errors.append("hash-locked Python environment drifted")
    if locked.get("python_install_flags") != python_lock.get("install_flags"):
        errors.append("hash-required Python install flags changed")

    execution = {row["id"]: row for row in load(
        "config/f0_r2_execution_gate_matrix.json"
    ).get("targets", [])}
    for target_id in TARGET_IDS:
        planned = target_by_id[target_id]["execution_gate"]["official_emulator"]
        available = execution[target_id]["official_emulator"]["available"]
        if available != (not planned.startswith("unsupported_")):
            errors.append(f"{target_id}: official emulator support gate changed")

    evidence = matrix.get("evidence", {})
    expected_counts = {
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
    if evidence != expected_counts:
        errors.append("F2-R2.1 evidence counts changed")
    if matrix.get("next") != "F2-R2.2":
        errors.append("F2-R2.1 next marker changed")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "F2-R2.1 build matrix OK: 6 targets x 2 configurations, 60 artifact "
        "paths, 16 maps, 16 size gates; 0 projects/builds/executions claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
