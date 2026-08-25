#!/usr/bin/env python3
"""Validate the exact, fail-closed F3.0.1 runtime recipe contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = REPO_ROOT / "config" / "f3_runtime_plan.json"
CAPABILITY_PATH = REPO_ROOT / "config" / "f3_execution_capability_matrix.json"
TOOLS_PATH = REPO_ROOT / ".toolchains" / "src" / "esp-idf" / "tools" / "tools.json"
QEMU_ROOT = (
    REPO_ROOT
    / ".toolchains"
    / "esp-tools"
    / "tools"
    / "qemu-xtensa"
    / "esp_develop_9.2.2_20250817"
    / "qemu"
    / "bin"
    / "qemu-system-xtensa"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-installed", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    capability = json.loads(CAPABILITY_PATH.read_text(encoding="utf-8"))
    tools = json.loads(TOOLS_PATH.read_text(encoding="utf-8"))

    if plan.get("stage") != "F3.0.1" or plan.get("status") != "reviewed":
        errors.append("F3.0.1 plan is not reviewed")
    policy = plan.get("policy", {})
    for key in (
        "target_boot_requires_target_binary",
        "success_requires_all_ordered_markers",
        "timeout_is_failure",
        "forbidden_marker_is_failure",
        "runner_error_is_failure",
        "raw_wall_clock_timing_is_not_committed",
        "no_emulator_run_claimed",
        "no_hardware_run_claimed",
    ):
        if policy.get(key) is not True:
            errors.append(f"fail-closed policy is missing: {key}")

    exact_targets = [
        target["id"]
        for target in capability["targets"]
        if target["target_binary_execution"] == "official_vendor_qemu"
    ]
    if exact_targets != ["s3"]:
        errors.append("runtime recipes must follow the reviewed capability matrix")

    qemu = next(tool for tool in tools["tools"] if tool["name"] == "qemu-xtensa")
    recommended = next(item for item in qemu["versions"] if item["status"] == "recommended")
    declared = plan["qemu"]
    if declared["version"] != recommended["name"]:
        errors.append("QEMU version is not the locked ESP-IDF recommendation")
    host_keys = {"linux_x86_64": "linux-amd64", "macos_arm64": "macos-arm64"}
    for host, manifest_key in host_keys.items():
        archive = declared["archives"][host]
        manifest = recommended[manifest_key]
        if archive["url"] != manifest["url"] or archive["sha256"] != manifest["sha256"]:
            errors.append(f"{host}: QEMU archive diverges from locked ESP-IDF")

    recipes = plan.get("recipes", {})
    if set(recipes) != {"s3_debug", "s3_release"}:
        errors.append("F3.0.1 must define S3 debug and release recipes")
    for configuration in ("debug", "release"):
        recipe = recipes.get(f"s3_{configuration}", {})
        if recipe.get("target") != "s3" or recipe.get("configuration") != configuration:
            errors.append(f"invalid S3 {configuration} recipe identity")
        if recipe.get("build_command") != [
            "{locked_python}",
            "tools/run_locked_target.py",
            "build",
            "--target",
            "s3",
            "--config",
            configuration,
        ]:
            errors.append(f"S3 {configuration} locked build command changed")
        if recipe.get("target_elf") != f"build/targets/s3/{configuration}/leshy2_s3.elf":
            errors.append(f"invalid S3 {configuration} target ELF")
        command = recipe.get("run_command", [])
        for token in ("{locked_python}", "{idf_path}/tools/idf.py", "qemu"):
            if token not in command:
                errors.append(f"S3 {configuration} run command misses {token}")
        qemu_args = next(
            (token for token in command if token.startswith("--qemu-extra-args=")), ""
        )
        if not qemu_args.startswith("--qemu-extra-args=-no-reboot -m 8M -d guest_errors,unimp -D "):
            errors.append(f"S3 {configuration} may reboot after a fault")
        if f"build/targets/s3/{configuration}/qemu_debug.log" not in qemu_args:
            errors.append(f"S3 {configuration} diagnostic log path changed")
        expected_flash = f"{{repo}}/build/targets/s3/{configuration}/qemu_f3_flash.bin"
        if "--flash-file" not in command or expected_flash not in command:
            errors.append(f"S3 {configuration} deterministic flash fixture is missing")

    observation = plan.get("observation", {})
    if observation.get("timeout_seconds") != 30:
        errors.append("runtime timeout must remain exactly 30 seconds")
    markers = observation.get("ordered_success_markers", [])
    if markers != [
        "ESP-ROM:esp32s3-",
        "boot: ESP-IDF v6.0.2",
        "esp_psram: Found 8MB PSRAM device",
        "esp_psram: SPI SRAM memory test OK",
        "main_task: Calling app_main()",
        "leshy2_s3: skeleton ready:",
    ]:
        errors.append("ordered boot markers changed")
    app_main = (REPO_ROOT / "targets" / "s3" / "main" / "app_main.c").read_text(
        encoding="utf-8"
    )
    if "skeleton ready:" not in app_main:
        errors.append("product boot marker is absent from S3 target source")
    if not observation.get("forbidden_markers"):
        errors.append("forbidden failure markers are empty")

    contract = plan.get("result_contract", {})
    if len(contract.get("required_fields", [])) != 18:
        errors.append("result record schema is incomplete")
    if "physical_board" not in contract.get("deferred_claims", []):
        errors.append("physical board evidence must remain deferred")
    fixture = plan.get("flash_fixture", {})
    if fixture.get("patch_offset") != 0xF000:
        errors.append("S3 otadata fixture offset changed")
    if fixture.get("entry", {}).get("ota_state_name") != "ESP_OTA_IMG_VALID":
        errors.append("S3 otadata fixture is not pre-confirmed")
    if set(fixture.get("claims_excluded", [])) != {
        "first_boot_otadata_write",
        "ota_state_flash_mutation",
        "rollback_transition",
    }:
        errors.append("S3 QEMU flash-write exclusions changed")
    if set(fixture.get("known_qemu_diagnostics", [])) != {
        "M25P80: Read id (command 0x90/0xAB) is not supported by device",
        "M25P80: Unknown cmd 5a",
        "M25P80: Unknown cmd 7a",
        "Invalid read at addr 0x10200C",
    }:
        errors.append("S3 known QEMU diagnostics changed")
    if plan.get("execution_counts") != {
        "defined_recipes": 2,
        "target_emulator_runs": 0,
        "hardware_runs": 0,
    }:
        errors.append("F3.0.1 may not claim an execution")
    if plan.get("next") != "F3.0.2":
        errors.append("F3.0.1 next marker changed")

    local_supported = platform.system() == "Darwin" and platform.machine() == "arm64"
    if args.require_installed and not QEMU_ROOT.is_file():
        errors.append(f"exact QEMU is not installed: {QEMU_ROOT}")
    if QEMU_ROOT.is_file() and local_supported:
        expected_hash = declared["archives"]["macos_arm64"]["executable_sha256"]
        if sha256(QEMU_ROOT) != expected_hash:
            errors.append("installed QEMU executable hash changed")
        result = subprocess.run(
            [str(QEMU_ROOT), "--version"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode != 0:
            errors.append("installed QEMU cannot start; check host runtime libraries")
        elif result.stdout.splitlines()[0] != declared["version_line"]:
            errors.append("installed QEMU version line changed")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    installed = "installed and exact" if QEMU_ROOT.is_file() and local_supported else "optional locally"
    print(
        "F3.0.1 runtime plan OK: 2 S3 recipes, 6 ordered markers, "
        f"30-second fail-closed timeout; QEMU {installed}; 0 runs claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
