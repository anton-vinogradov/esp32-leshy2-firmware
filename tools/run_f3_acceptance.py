#!/usr/bin/env python3
"""Fail-closed F3 plan validation and exact ESP32-S3 QEMU execution."""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import os
import platform
import selectors
import signal
import struct
import subprocess
import sys
import time
import traceback
from pathlib import Path

from capture_target_build_review import input_manifest
from review_f2_4_preflight import local_environment


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = REPO_ROOT / "config" / "f3_acceptance_matrix.json"
CAPABILITY_PATH = REPO_ROOT / "config" / "f3_execution_capability_matrix.json"
PLAN_PATH = REPO_ROOT / "config" / "f3_runtime_plan.json"
SCENARIO_PLAN_PATH = REPO_ROOT / "config" / "f3_2_scenario_plan.json"
LOCKED_PYTHON = REPO_ROOT / ".toolchains" / "python" / "idf6_py3.12_env" / "bin" / "python"
IDF_PATH = REPO_ROOT / ".toolchains" / "src" / "esp-idf"
QEMU_PATH = (
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


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execution_contract(stage: str) -> tuple[dict, dict, list[str], list[str]]:
    runtime_plan = load(PLAN_PATH)
    if stage == "F3.1":
        return (
            runtime_plan,
            runtime_plan["observation"],
            runtime_plan["result_contract"]["accepted_claims"],
            runtime_plan["result_contract"]["deferred_claims"],
        )
    if stage == "F3.2":
        scenario_plan = load(SCENARIO_PLAN_PATH)
        return (
            runtime_plan,
            scenario_plan["observation"],
            scenario_plan["result_contract"]["accepted_claims"],
            scenario_plan["result_contract"]["deferred_claims"],
        )
    raise ValueError(f"unsupported execution stage: {stage}")


def validate_plan() -> list[str]:
    errors: list[str] = []
    matrix = load(MATRIX_PATH)
    capability = load(CAPABILITY_PATH)
    plan = load(PLAN_PATH)
    scenario_plan = load(SCENARIO_PLAN_PATH)
    if matrix.get("stage") != "F3.0.2" or matrix.get("status") != "reviewed":
        errors.append("F3.0.2 acceptance matrix is not reviewed")
    if matrix.get("next") != "F3.1":
        errors.append("F3.0.2 next marker changed")
    if matrix.get("execution_counts") != {
        "target_emulator_runs": 0,
        "hardware_runs": 0,
    }:
        errors.append("F3.0.2 may not claim an execution")
    targets = {target["id"]: target for target in matrix.get("targets", [])}
    capability_targets = {target["id"]: target for target in capability["targets"]}
    if set(targets) != {"s3", "c5", "rp", "pack", "safety"}:
        errors.append("acceptance matrix must cover exactly five targets")
    for target_id, target in targets.items():
        exact = capability_targets[target_id]["target_binary_execution"] == "official_vendor_qemu"
        if target.get("target_boot_claim_allowed_after_pass") is not exact:
            errors.append(f"{target_id}: target-boot claim diverges from capability matrix")
        if not target.get("physical_gate") or not target.get("automated_evidence"):
            errors.append(f"{target_id}: evidence or physical gate is missing")
    if targets.get("s3", {}).get("f3_execution_class") != "exact_target_qemu":
        errors.append("S3 exact QEMU path is missing")
    for target_id in ("c5", "rp", "pack", "safety"):
        if "static" not in targets.get(target_id, {}).get("f3_execution_class", ""):
            errors.append(f"{target_id}: non-emulated path is mislabeled")
    if set(plan.get("recipes", {})) != {"s3_debug", "s3_release"}:
        errors.append("acceptance runner requires both reviewed S3 recipes")
    runner = matrix.get("runner", {})
    if runner.get("path") != "tools/run_f3_acceptance.py":
        errors.append("acceptance runner path changed")
    for command_name in (
        "plan_check",
        "s3_run",
        "s3_evidence_check",
        "s3_scenario_run",
        "f3_2_review",
    ):
        if not runner.get(command_name):
            errors.append(f"acceptance runner command is missing: {command_name}")
    if (
        scenario_plan.get("stage") != "F3.2"
        or scenario_plan.get("status") != "reviewed_plan"
    ):
        errors.append("F3.2 scenario plan is not reviewed")
    scenarios = scenario_plan.get("target_scenarios", [])
    if [scenario.get("id") for scenario in scenarios] != [
        "self_test_pass",
        "retained_first_fault_ram_model",
        "failed_update_ram_rollback_model",
    ]:
        errors.append("F3.2 target scenario set changed")
    scenario_markers = [scenario.get("marker") for scenario in scenarios]
    observed_contract = scenario_plan.get("observation", {}).get(
        "ordered_success_markers", []
    )
    if len(observed_contract) != 9 or any(
        marker not in observed_contract for marker in scenario_markers
    ):
        errors.append("F3.2 ordered marker contract is incomplete")
    if (
        scenario_plan.get("host_evidence", {})
        .get("scenario_counts", {})
        .get("total")
        != 24
    ):
        errors.append("F3.2 portable host scenario count changed")
    return errors


def expand(tokens: list[str]) -> list[str]:
    replacements = {
        "{locked_python}": str(LOCKED_PYTHON),
        "{idf_path}": str(IDF_PATH),
        "{repo}": str(REPO_ROOT),
    }
    expanded: list[str] = []
    for token in tokens:
        for placeholder, value in replacements.items():
            token = token.replace(placeholder, value)
        expanded.append(token)
    return expanded


def f3_environment() -> dict[str, str]:
    environment = local_environment()
    environment["PATH"] = str(QEMU_PATH.parent) + os.pathsep + environment["PATH"]
    return environment


def terminate_group(process: subprocess.Popen[bytes]) -> None:
    process_group = process.pid
    try:
        os.killpg(process_group, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process_group, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        return
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        pass


def prepare_s3_flash(recipe: dict, environment: dict[str, str]) -> tuple[Path, dict]:
    build = REPO_ROOT / recipe["build_directory"]
    flash = build / "qemu_f3_flash.bin"
    command = [
        str(LOCKED_PYTHON),
        "-m",
        "esptool",
        "--chip=esp32s3",
        "merge-bin",
        f"--output={flash}",
        "--pad-to-size=16MB",
        "@flash_args",
    ]
    result = subprocess.run(
        command,
        cwd=build,
        env=environment,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        raise RuntimeError("QEMU flash merge failed:\n" + result.stdout)
    fixture = load(PLAN_PATH)["flash_fixture"]
    offset = fixture["patch_offset"]
    image = bytearray(flash.read_bytes())
    if len(image) != 16 * 1024 * 1024:
        raise RuntimeError("QEMU flash fixture is not exactly 16 MiB")
    if image[offset : offset + 0x2000] != b"\xff" * 0x2000:
        raise RuntimeError("QEMU otadata input is not the reviewed blank initial state")
    ota_seq = fixture["entry"]["ota_seq"]
    ota_state = fixture["entry"]["ota_state"]
    ota_seq_bytes = struct.pack("<I", ota_seq)
    crc = binascii.crc32(ota_seq_bytes, 0xFFFFFFFF) & 0xFFFFFFFF
    entry = struct.pack("<I20sII", ota_seq, b"\xff" * 20, ota_state, crc)
    image[offset : offset + len(entry)] = entry
    flash.write_bytes(image)
    return flash, {
        "offset": offset,
        "ota_seq": ota_seq,
        "ota_state": ota_state,
        "ota_state_name": fixture["entry"]["ota_state_name"],
        "crc32_le": f"0x{crc:08x}",
        "excluded_claims": fixture["claims_excluded"],
    }


def execute_s3(configuration: str, stage: str) -> tuple[dict, str]:
    plan, observation, accepted_claims, deferred_claims = execution_contract(stage)
    recipe = plan["recipes"][f"s3_{configuration}"]
    environment = f3_environment()
    build_result = subprocess.run(
        expand(recipe["build_command"]),
        cwd=REPO_ROOT,
        env=environment,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if build_result.returncode != 0:
        raise RuntimeError("target build failed:\n" + build_result.stdout)
    prerequisite = subprocess.run(
        expand(recipe["verify_command"]),
        cwd=REPO_ROOT,
        env=environment,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if prerequisite.returncode != 0:
        raise RuntimeError("target artifact verification failed:\n" + prerequisite.stdout)
    qemu_check = subprocess.run(
        [sys.executable, "tools/check_f3_runtime_plan.py", "--require-installed"],
        cwd=REPO_ROOT,
        env=environment,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if qemu_check.returncode != 0:
        raise RuntimeError("QEMU preflight failed:\n" + qemu_check.stdout)

    flash, ota_fixture = prepare_s3_flash(recipe, environment)
    build = REPO_ROOT / recipe["build_directory"]
    diagnostic_log = build / "qemu_debug.log"
    diagnostic_log.unlink(missing_ok=True)
    (build / "qemu_efuse.bin").unlink(missing_ok=True)

    command = expand(recipe["run_command"])
    process = subprocess.Popen(
        command,
        cwd=REPO_ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    if process.stdout is None:
        terminate_group(process)
        raise RuntimeError("QEMU output pipe was not created")
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    timeout = observation["timeout_seconds"]
    deadline = time.monotonic() + timeout
    chunks = bytearray()
    markers = observation["ordered_success_markers"]
    forbidden = plan["observation"]["forbidden_markers"]
    marker_index = 0
    search_start = 0
    failure_marker: str | None = None
    timed_out = False
    termination = "runner_error"
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                termination = "timeout"
                break
            events = selector.select(timeout=min(remaining, 0.25))
            for key, _ in events:
                chunk = os.read(key.fd, 4096)
                if chunk:
                    chunks.extend(chunk)
            text = chunks.decode("utf-8", errors="replace")
            for candidate in forbidden:
                if candidate in text:
                    failure_marker = candidate
                    termination = "forbidden_marker"
                    break
            if failure_marker:
                break
            while marker_index < len(markers):
                position = text.find(markers[marker_index], search_start)
                if position < 0:
                    break
                search_start = position + len(markers[marker_index])
                marker_index += 1
            if marker_index == len(markers):
                termination = "ordered_markers_complete"
                break
            if process.poll() is not None:
                termination = "early_exit"
                break
    finally:
        selector.close()
        terminate_group(process)
        try:
            tail, _ = process.communicate(timeout=1)
            chunks.extend(tail)
        except subprocess.TimeoutExpired:
            pass

    transcript = chunks.decode("utf-8", errors="replace")
    diagnostic_log = REPO_ROOT / recipe["build_directory"] / "qemu_debug.log"
    diagnostic_text = ""
    if diagnostic_log.is_file():
        diagnostic_text = diagnostic_log.read_text(
            encoding="utf-8", errors="replace"
        )
        transcript += "\n--- qemu diagnostics ---\n" + diagnostic_text
        if failure_marker is None:
            failure_marker = next(
                (candidate for candidate in forbidden if candidate in diagnostic_text),
                None,
            )
            if failure_marker is not None:
                termination = "forbidden_marker"
    status = (
        "reviewed"
        if not timed_out and failure_marker is None and marker_index == len(markers)
        else "failed"
    )
    build = REPO_ROOT / recipe["build_directory"]
    elf = REPO_ROOT / recipe["target_elf"]
    version = subprocess.run(
        [str(QEMU_PATH), "--version"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.splitlines()[0]
    record = {
        "schema_version": 1,
        "stage": stage,
        "status": status,
        "target": "s3",
        "configuration": configuration,
        "target_elf_sha256": sha256(elf),
        "project_input_manifest_sha256": input_manifest("s3")["manifest_sha256"],
        "qemu_version": version,
        "qemu_executable_sha256": sha256(QEMU_PATH),
        "ordered_markers": [
            {"marker": marker, "observed": index < marker_index}
            for index, marker in enumerate(markers)
        ],
        "forbidden_markers_observed": [] if failure_marker is None else [failure_marker],
        "timed_out": timed_out,
        "termination": termination,
        "accepted_claims": accepted_claims if status == "reviewed" else [],
        "deferred_claims": deferred_claims,
        "qemu_flash_sha256": sha256(flash),
        "qemu_efuse_sha256": sha256(build / "qemu_efuse.bin")
        if (build / "qemu_efuse.bin").is_file()
        else None,
        "ota_fixture": ota_fixture,
        "qemu_diagnostics": {
            "known_patterns_observed": [
                pattern
                for pattern in plan["flash_fixture"]["known_qemu_diagnostics"]
                if pattern in diagnostic_text
            ],
            "unexpected_lines": [
                line
                for line in diagnostic_text.splitlines()
                if line
                and line != "Adding SPI flash device"
                and not any(
                    pattern in line
                    for pattern in plan["flash_fixture"]["known_qemu_diagnostics"]
                )
            ],
            "claims_expanded": False,
        },
    }
    return record, transcript


def evidence_path(configuration: str, stage: str) -> Path:
    stage_token = stage.lower().replace(".", "_")
    suffix = "runtime_review" if stage == "F3.1" else "scenario_review"
    return REPO_ROOT / "config" / f"{stage_token}_s3_{configuration}_{suffix}.json"


def check_evidence(configuration: str, stage: str) -> list[str]:
    errors: list[str] = []
    path = evidence_path(configuration, stage)
    if not path.is_file():
        return [f"runtime evidence does not exist: {path.relative_to(REPO_ROOT)}"]
    record = load(path)
    plan, observation, accepted_claims, deferred_claims = execution_contract(stage)
    if record.get("stage") != stage or record.get("status") != "reviewed":
        errors.append(f"S3 {configuration} runtime evidence is not reviewed")
    if record.get("target") != "s3" or record.get("configuration") != configuration:
        errors.append(f"S3 {configuration} runtime evidence identity changed")
    if record.get("timed_out") is not False:
        errors.append(f"S3 {configuration} runtime timed out")
    if record.get("termination") != "ordered_markers_complete":
        errors.append(f"S3 {configuration} did not reach every ordered marker")
    if record.get("forbidden_markers_observed") != []:
        errors.append(f"S3 {configuration} observed a forbidden marker")
    if not all(item.get("observed") for item in record.get("ordered_markers", [])):
        errors.append(f"S3 {configuration} has missing boot markers")
    if [item.get("marker") for item in record.get("ordered_markers", [])] != observation["ordered_success_markers"]:
        errors.append(f"S3 {configuration} boot marker contract changed")
    if record.get("accepted_claims") != accepted_claims:
        errors.append(f"S3 {configuration} accepted claims changed")
    if record.get("deferred_claims") != deferred_claims:
        errors.append(f"S3 {configuration} deferred claims changed")
    if stage == "F3.2" and record.get(
        "project_input_manifest_sha256"
    ) != input_manifest("s3")["manifest_sha256"]:
        errors.append(f"S3 {configuration} project inputs changed after runtime review")
    if QEMU_PATH.is_file() and record.get("qemu_executable_sha256") != sha256(QEMU_PATH):
        errors.append(f"S3 {configuration} QEMU executable changed after runtime review")
    fixture = record.get("ota_fixture", {})
    if fixture.get("excluded_claims") != plan["flash_fixture"]["claims_excluded"]:
        errors.append(f"S3 {configuration} otadata exclusion changed")
    diagnostics = record.get("qemu_diagnostics", {})
    if diagnostics.get("unexpected_lines") != [] or diagnostics.get("claims_expanded") is not False:
        errors.append(f"S3 {configuration} has unreviewed QEMU diagnostics")
    for field in ("qemu_flash_sha256", "qemu_efuse_sha256"):
        if not isinstance(record.get(field), str) or len(record[field]) != 64:
            errors.append(f"S3 {configuration} evidence has invalid {field}")
    for field in load(PLAN_PATH)["result_contract"]["required_fields"]:
        if field not in record:
            errors.append(f"S3 {configuration} evidence misses {field}")
    return errors


def f3_2_review_path() -> Path:
    return REPO_ROOT / "config" / "f3_2_runtime_review.json"


def create_f3_2_review() -> dict:
    scenario_plan = load(SCENARIO_PLAN_PATH)
    target_rows: list[dict] = []
    for configuration in ("debug", "release"):
        errors = check_evidence(configuration, "F3.2")
        if errors:
            raise RuntimeError("\n".join(errors))
        path = evidence_path(configuration, "F3.2")
        target_rows.append(
            {
                "configuration": configuration,
                "path": str(path.relative_to(REPO_ROOT)),
                "sha256": sha256(path),
            }
        )

    host = subprocess.run(
        ["make", "host-sanitize"],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if host.returncode != 0:
        raise RuntimeError("F3.2 host sanitizer run failed:\n" + host.stdout)
    host_contract = scenario_plan["host_evidence"]
    missing = [
        marker for marker in host_contract["required_markers"] if marker not in host.stdout
    ]
    if missing:
        raise RuntimeError("F3.2 host markers missing: " + ", ".join(missing))

    return {
        "schema_version": 1,
        "stage": "F3.2",
        "status": "reviewed",
        "target": "s3",
        "target_emulator_evidence": target_rows,
        "host_sanitizer_evidence": {
            "command": host_contract["command"],
            "sanitizers": ["address", "undefined"],
            "scenario_counts": host_contract["scenario_counts"],
            "markers": [
                {"marker": marker, "observed": True}
                for marker in host_contract["required_markers"]
            ],
        },
        "accepted_claims": scenario_plan["result_contract"]["accepted_claims"]
        + ["portable_host_fault_suite_sanitizer_clean"],
        "deferred_claims": scenario_plan["result_contract"]["deferred_claims"],
        "execution_counts": {
            "s3_target_emulator_runs": 2,
            "host_sanitizer_scenarios": host_contract["scenario_counts"]["total"],
            "hardware_runs": 0,
        },
        "next": scenario_plan["next"],
        "runner": "tools/run_f3_acceptance.py",
    }


def check_f3_2_review() -> list[str]:
    path = f3_2_review_path()
    if not path.is_file():
        return ["F3.2 integrated runtime evidence does not exist"]
    record = load(path)
    scenario_plan = load(SCENARIO_PLAN_PATH)
    errors: list[str] = []
    if record.get("stage") != "F3.2" or record.get("status") != "reviewed":
        errors.append("F3.2 integrated runtime evidence is not reviewed")
    expected_rows = []
    for configuration in ("debug", "release"):
        errors.extend(check_evidence(configuration, "F3.2"))
        evidence = evidence_path(configuration, "F3.2")
        if evidence.is_file():
            expected_rows.append(
                {
                    "configuration": configuration,
                    "path": str(evidence.relative_to(REPO_ROOT)),
                    "sha256": sha256(evidence),
                }
            )
    if record.get("target_emulator_evidence") != expected_rows:
        errors.append("F3.2 target evidence hashes changed")
    host = record.get("host_sanitizer_evidence", {})
    if host.get("sanitizers") != ["address", "undefined"]:
        errors.append("F3.2 sanitizer set changed")
    if host.get("scenario_counts") != scenario_plan["host_evidence"]["scenario_counts"]:
        errors.append("F3.2 host scenario counts changed")
    expected_host_markers = [
        {"marker": marker, "observed": True}
        for marker in scenario_plan["host_evidence"]["required_markers"]
    ]
    if host.get("markers") != expected_host_markers:
        errors.append("F3.2 host evidence markers changed")
    if record.get("execution_counts") != {
        "s3_target_emulator_runs": 2,
        "host_sanitizer_scenarios": 24,
        "hardware_runs": 0,
    }:
        errors.append("F3.2 execution counts changed")
    expected_claims = scenario_plan["result_contract"]["accepted_claims"] + [
        "portable_host_fault_suite_sanitizer_clean"
    ]
    if record.get("accepted_claims") != expected_claims:
        errors.append("F3.2 accepted claims changed")
    if (
        record.get("deferred_claims")
        != scenario_plan["result_contract"]["deferred_claims"]
    ):
        errors.append("F3.2 deferred claims changed")
    if record.get("next") != "F3.3":
        errors.append("F3.2 next marker changed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-plan", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--run-s3", action="store_true")
    mode.add_argument("--check-s3-evidence", action="store_true")
    mode.add_argument("--run-s3-f3-2", action="store_true")
    mode.add_argument("--check-f3-2-evidence", action="store_true")
    mode.add_argument("--review-f3-2", action="store_true")
    mode.add_argument("--check-f3-2-review", action="store_true")
    parser.add_argument("--config", choices=("debug", "release"), default="debug")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    errors = validate_plan()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.check_plan:
        print("F3.0.2 acceptance plan OK: 5 targets, 1 exact QEMU path, 4 honest physical gates, 0 runs claimed")
        return 0
    if args.dry_run:
        recipe = load(PLAN_PATH)["recipes"][f"s3_{args.config}"]
        print(" ".join(expand(recipe["run_command"])))
        return 0
    if args.check_s3_evidence:
        errors = check_evidence(args.config, "F3.1")
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"F3.1 S3 {args.config} runtime evidence OK")
        return 0
    if args.check_f3_2_evidence:
        errors = check_evidence(args.config, "F3.2")
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"F3.2 S3 {args.config} scenario evidence OK")
        return 0
    if args.check_f3_2_review:
        errors = check_f3_2_review()
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("F3.2 integrated runtime review OK: 2 S3 runs and 24 sanitized host scenarios")
        return 0
    if args.review_f3_2:
        if not args.write:
            print("ERROR: F3.2 review execution requires --write evidence", file=sys.stderr)
            return 1
        try:
            record = create_f3_2_review()
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
        f3_2_review_path().write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print("F3.2 integrated runtime review OK: 2 S3 runs and 24 sanitized host scenarios")
        return 0
    if not args.write:
        print("ERROR: target execution requires --write evidence", file=sys.stderr)
        return 1
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        print("ERROR: this reviewed local run requires macOS arm64", file=sys.stderr)
        return 1
    try:
        stage = "F3.2" if args.run_s3_f3_2 else "F3.1"
        record, transcript = execute_s3(args.config, stage)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        traceback.print_exc()
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if record["status"] != "reviewed":
        print(transcript[-6000:], file=sys.stderr)
        print(
            f"ERROR: {record['stage']} S3 {args.config} QEMU run failed: "
            f"{record['termination']}",
            file=sys.stderr,
        )
        return 1
    evidence_path(args.config, record["stage"]).write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"{record['stage']} S3 {args.config} QEMU run OK: "
        f"{len(record['ordered_markers'])} ordered markers"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
