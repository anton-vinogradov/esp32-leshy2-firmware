#!/usr/bin/env python3
"""Import the reviewed H4-R2.2 BSP correction closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HW_ROOT = ROOT.parent / "esp32-leshy2"
SOURCE = HW_ROOT / "hardware/verification/generated/H4-R2-correction-closure.json"
OUTPUT = ROOT / "config/h4_r2_correction_closure.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    summary = source.get("summary", {})
    if (
        source.get("marker") != "H4-R2.2"
        or source.get("status") != "reviewed"
        or not source.get("checks")
        or not all(source["checks"].values())
        or (summary.get("h2_controller_rows"), summary.get("generated_bsp_rows"), summary.get("restored_rows")) != (173, 173, 38)
        or summary.get("remaining_contradictions") != 0
        or (summary.get("qualified_configurations"), summary.get("verified_artifacts"), summary.get("verified_maps"), summary.get("passed_size_gates")) != (12, 60, 16, 16)
        or source.get("next", {}).get("marker") != "H4-R2.3"
    ):
        raise ValueError("hardware H4-R2.2 correction closure is not reviewed")
    return {
        "schema_version": 1,
        "artifact": "FW-H4-R2-correction-closure-import",
        "status": "reviewed_hardware_correction_imported",
        "hardware_marker": "H4-R2.2",
        "current_hardware_substep": "H4-R2.3",
        "source": {
            "path": "../esp32-leshy2/hardware/verification/generated/H4-R2-correction-closure.json",
            "sha256": sha256(SOURCE),
        },
        "reviewed_boundary": {
            "domains": 6,
            "h2_controller_rows": 173,
            "generated_bsp_rows": 173,
            "restored_rows": 38,
            "remaining_contradictions": 0,
            "qualified_configurations": 12,
            "verified_artifacts": 60,
            "verified_maps": 16,
            "passed_size_gates": 16,
            "retained_firmware_obligations": 1,
            "physical_residuals_carried": 51,
        },
        "claims": {
            "all_six_generated_bsp_maps_exact": True,
            "all_targets_fail_closed_on_mapping_and_count": True,
            "all_target_compilation_and_link_passed": True,
            "runtime_boot_proven": False,
            "i8080_target_implementation_proven": False,
            "physical_residuals_complete": False,
            "purchase_layout_or_fabrication_authorized": False,
        },
        "next": source["next"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
        print(f"stale: {OUTPUT.relative_to(ROOT)}")
        return 1
    print("ok: H4-R2.2 BSP correction closure is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
