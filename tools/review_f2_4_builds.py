#!/usr/bin/env python3
"""Aggregate and validate all five F2.4 target-build evidence artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "config" / "f2_4_build_review.json"
EXPECTED = {
    "s3": ("F2.4.1", "esp32s3", "esp_idf", 5),
    "c5": ("F2.4.2", "esp32c5", "esp_idf", 5),
    "rp": ("F2.4.3", "rp2350-arm-s", "pico_sdk", 4),
    "pack": ("F2.4.4", "MSPM0C1106", "ti_mspm0_sdk", 6),
    "safety": ("F2.4.5", "MSPM0C1106", "ti_mspm0_sdk", 6),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def fail(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


def aggregate() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    targets: list[dict[str, object]] = []
    total_artifacts = 0
    total_maps = 0
    total_gates = 0
    watched_margins: list[dict[str, object]] = []

    for target_id, (stage, sdk_target, family, per_config) in EXPECTED.items():
        relative = Path("config") / f"f2_4_{target_id}_build_review.json"
        path = REPO_ROOT / relative
        if not path.is_file():
            errors.append(f"missing evidence: {relative}")
            continue
        review = json.loads(path.read_text(encoding="utf-8"))
        for key, expected in (
            ("stage", stage),
            ("status", "reviewed"),
            ("target", target_id),
            ("sdk_target", sdk_target),
            ("family", family),
        ):
            if review.get(key) != expected:
                errors.append(
                    f"{target_id}: {key} is {review.get(key)!r}, expected {expected!r}"
                )

        configurations = review.get("configurations", {})
        if set(configurations) != {"debug", "release"}:
            errors.append(f"{target_id}: debug/release evidence is incomplete")
            continue

        image_bytes: dict[str, int] = {}
        target_artifacts = 0
        target_maps = 0
        for configuration in ("debug", "release"):
            row = configurations[configuration]
            artifacts = row.get("artifacts", [])
            if row.get("status") != "passed":
                errors.append(f"{target_id}:{configuration}: status is not passed")
            if len(artifacts) != per_config:
                errors.append(
                    f"{target_id}:{configuration}: {len(artifacts)} artifacts, "
                    f"expected {per_config}"
                )
            paths = [item.get("path", "") for item in artifacts]
            if len(paths) != len(set(paths)):
                errors.append(f"{target_id}:{configuration}: duplicate artifact path")
            expected_prefix = f"build/targets/{target_id}/{configuration}/"
            for item in artifacts:
                artifact_path = item.get("path", "")
                if not artifact_path.startswith(expected_prefix) or Path(artifact_path).is_absolute():
                    errors.append(
                        f"{target_id}:{configuration}: invalid artifact path {artifact_path!r}"
                    )
                if not isinstance(item.get("bytes"), int) or item["bytes"] <= 0:
                    errors.append(f"{artifact_path}: invalid byte count")
                digest = item.get("sha256", "")
                if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
                    errors.append(f"{artifact_path}: invalid SHA-256")

            gate = row.get("image_gate", {})
            if gate.get("result") not in {"ok", "warning"}:
                errors.append(f"{target_id}:{configuration}: image gate did not pass")
            size = gate.get("size_bytes")
            maximum = gate.get("maximum_image_bytes")
            if not isinstance(size, int) or not isinstance(maximum, int) or size > maximum:
                errors.append(f"{target_id}:{configuration}: image exceeds its gate")
            if gate.get("image") not in paths:
                errors.append(f"{target_id}:{configuration}: gated image is not an artifact")
            image_bytes[configuration] = size

            margin = row.get("bootloader_margin")
            if margin is not None:
                free = margin.get("free_bytes")
                if not isinstance(free, int) or free < 0:
                    errors.append(f"{target_id}:{configuration}: invalid bootloader margin")
                if margin.get("result") == "watch":
                    watched_margins.append(
                        {
                            "target": target_id,
                            "configuration": configuration,
                            "free_bytes": free,
                        }
                    )

            target_artifacts += len(artifacts)
            target_maps += sum(item.get("path", "").endswith(".map") for item in artifacts)
            total_gates += 1

        execution = review.get("execution", {})
        for key in ("configure_runs", "build_runs", "artifact_verify_runs"):
            if execution.get(key) != 2:
                errors.append(f"{target_id}: {key} must equal 2")
        for key in ("emulator_runs", "hardware_runs"):
            if execution.get(key) != 0:
                errors.append(f"{target_id}: {key} must remain zero")
        if execution.get("network_during_configure_or_build") is not False:
            errors.append(f"{target_id}: offline build claim changed")

        claims = review.get("claims", {})
        for key in (
            "target_compilation_and_link_passed",
            "all_declared_artifacts_present",
            "image_size_gate_passed",
        ):
            if claims.get(key) is not True:
                errors.append(f"{target_id}: required claim {key} is not true")
        for key in ("runtime_boot_proven", "byte_reproducibility_proven"):
            if claims.get(key) is not False:
                errors.append(f"{target_id}: premature claim {key}")

        targets.append(
            {
                "target": target_id,
                "stage": stage,
                "evidence": str(relative),
                "evidence_sha256": sha256(path),
                "configurations": ["debug", "release"],
                "artifact_instances": target_artifacts,
                "map_files": target_maps,
                "image_bytes": image_bytes,
            }
        )
        total_artifacts += target_artifacts
        total_maps += target_maps

    expected_totals = {
        "targets": 5,
        "configurations": 10,
        "artifact_instances": 52,
        "map_files": 14,
        "image_size_gates": 10,
        "configure_runs": 10,
        "build_runs": 10,
        "artifact_verify_runs": 10,
        "emulator_runs": 0,
        "hardware_runs": 0,
    }
    observed_totals = {
        "targets": len(targets),
        "configurations": len(targets) * 2,
        "artifact_instances": total_artifacts,
        "map_files": total_maps,
        "image_size_gates": total_gates,
        "configure_runs": len(targets) * 2,
        "build_runs": len(targets) * 2,
        "artifact_verify_runs": len(targets) * 2,
        "emulator_runs": 0,
        "hardware_runs": 0,
    }
    if observed_totals != expected_totals:
        errors.append(f"integrated totals changed: {observed_totals!r}")

    result = {
        "schema_version": 1,
        "stage": "F2.4.6",
        "status": "reviewed",
        "scope": "integrated debug/release target-build, artifact, map and image-size review",
        "targets": targets,
        "totals": observed_totals,
        "watched_margins": watched_margins,
        "claims": {
            "all_target_compilation_and_link_passed": True,
            "all_declared_artifacts_present": True,
            "all_image_size_gates_passed": True,
            "network_during_configure_or_build": False,
            "runtime_boot_proven": False,
            "byte_reproducibility_proven": False,
        },
        "next": "F2.5",
        "runner": "tools/review_f2_4_builds.py",
    }
    return result, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result, errors = aggregate()
    if errors:
        return fail(errors)
    serialized = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        OUTPUT_PATH.write_text(serialized, encoding="utf-8")
    elif not OUTPUT_PATH.is_file() or OUTPUT_PATH.read_text(encoding="utf-8") != serialized:
        return fail([f"stale integrated evidence: {OUTPUT_PATH.relative_to(REPO_ROOT)}"])

    totals = result["totals"]
    print(
        "F2.4.6 integrated build review OK: "
        f"{totals['targets']} targets, {totals['configurations']} configurations, "
        f"{totals['artifact_instances']} artifacts, {totals['map_files']} maps, "
        f"{totals['image_size_gates']} image gates"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
