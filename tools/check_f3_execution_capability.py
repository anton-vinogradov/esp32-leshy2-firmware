#!/usr/bin/env python3
"""Fail-closed review of the F3 target execution capability matrix."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = REPO_ROOT / "config" / "f3_execution_capability_matrix.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qemu_registry_targets(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.AnnAssign):
            continue
        if not isinstance(node.target, ast.Name) or node.target.id != "QEMU_TARGETS":
            continue
        if not isinstance(node.value, ast.Dict):
            break
        return {
            key.value
            for key in node.value.keys
            if isinstance(key, ast.Constant) and isinstance(key.value, str)
        }
    raise RuntimeError("QEMU_TARGETS registry not found in locked ESP-IDF")


def main() -> int:
    errors: list[str] = []
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    if matrix.get("stage") != "F3.0.0" or matrix.get("status") != "reviewed":
        errors.append("F3.0.0 matrix is not reviewed")

    evidence = matrix["locked_source_evidence"]
    for record_name in ("esp_idf_qemu_registry", "esp_idf_tool_manifest"):
        record = evidence[record_name]
        path = REPO_ROOT / record["path"]
        if not path.is_file() or sha256(path) != record["sha256"]:
            errors.append(f"stale locked source evidence: {record_name}")
    pico = evidence["pico_host_platform"]
    for prefix in ("platform", "boundary"):
        path = REPO_ROOT / pico[f"{prefix}_path"]
        if not path.is_file() or sha256(path) != pico[f"{prefix}_sha256"]:
            errors.append(f"stale Pico host evidence: {prefix}")

    registry_path = REPO_ROOT / evidence["esp_idf_qemu_registry"]["path"]
    registry = qemu_registry_targets(registry_path)
    declared_registry = set(evidence["esp_idf_qemu_registry"]["targets"])
    if registry != declared_registry or registry != {"esp32", "esp32c3", "esp32s3"}:
        errors.append("locked ESP-IDF QEMU target registry changed")
    if "esp32c5" in registry:
        errors.append("C5 virtual-execution classification must be reviewed again")

    tools = json.loads(
        (REPO_ROOT / evidence["esp_idf_tool_manifest"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    qemu = next(tool for tool in tools["tools"] if tool["name"] == "qemu-xtensa")
    recommended = next(version for version in qemu["versions"] if version["status"] == "recommended")
    manifest = evidence["esp_idf_tool_manifest"]
    if qemu["supported_targets"] != ["esp32", "esp32s3"]:
        errors.append("qemu-xtensa supported targets changed")
    if recommended["name"] != manifest["qemu_xtensa_version"]:
        errors.append("recommended qemu-xtensa version changed")
    if recommended["macos-arm64"]["sha256"] != manifest["qemu_xtensa_macos_arm64_sha256"]:
        errors.append("qemu-xtensa macOS arm64 archive hash changed")

    pico_boundary = (REPO_ROOT / pico["boundary_path"]).read_text(encoding="utf-8")
    if "default=1 when PICO_PLATFORM is host" not in pico_boundary:
        errors.append("Pico host no-hardware boundary changed")

    targets = {target["id"]: target for target in matrix["targets"]}
    if set(targets) != {"s3", "c5", "rp", "pack", "safety"}:
        errors.append("F3 execution matrix must cover exactly five targets")
    exact = [
        target["id"]
        for target in matrix["targets"]
        if target["target_binary_execution"] == "official_vendor_qemu"
    ]
    if exact != ["s3"]:
        errors.append("only S3 has an accepted exact virtual target path")
    for target in matrix["targets"]:
        if not target["accepted_f3_claims"] or not target["forbidden_claims"]:
            errors.append(f"{target['id']} lacks an explicit evidence boundary")
        if not target["physical_gate"]:
            errors.append(f"{target['id']} lacks a physical evidence gate")

    counts = matrix["execution_counts"]
    if counts != {
        "target_binary_emulator_paths": 1,
        "portable_host_paths": 5,
        "target_emulator_runs": 0,
        "hardware_runs": 0,
    }:
        errors.append("F3.0.0 execution counts changed")
    if matrix.get("next") != "F3.0.1":
        errors.append("F3.0.0 next marker changed")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        "F3.0.0 execution capability review OK: 5 targets, "
        "1 exact vendor QEMU path, 4 explicit host/dev-board boundaries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
