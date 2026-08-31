#!/usr/bin/env python3
"""Import the reviewed global H4-R2 joined pre-layout gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HW_ROOT = ROOT.parent / "esp32-leshy2"
SOURCE = HW_ROOT / "hardware/verification/generated/H4-R2-acceptance-package.json"
OUTPUT = ROOT / "config/h4_r2_acceptance.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = source.get("result", {})
    if (
        source.get("marker") != "H4-R2.3"
        or source.get("status") != "reviewed"
        or not source.get("checks")
        or not all(source["checks"].values())
        or (result.get("joined_inputs"), result.get("compute_domains"), result.get("h2_controller_rows"), result.get("generated_bsp_rows"), result.get("m1_contacts"), result.get("qualified_target_configurations")) != (24, 6, 173, 173, 80, 12)
        or result.get("cross_domain_contradictions_remaining") != 0
        or result.get("open_analytical_findings") != 0
        or source.get("next", {}).get("marker") != "H5.0.3-R1"
    ):
        raise ValueError("hardware H4-R2 global acceptance is not reviewed")
    return {
        "schema_version": 1,
        "artifact": "FW-H4-R2-acceptance-import",
        "status": "reviewed_hardware_gate_imported",
        "hardware_marker": "H4-R2.3",
        "current_hardware_stage": "H5",
        "current_hardware_substep": "H5.0.3-R1",
        "source": {
            "path": "../esp32-leshy2/hardware/verification/generated/H4-R2-acceptance-package.json",
            "sha256": sha256(SOURCE),
        },
        "reviewed_result": result,
        "handoff": source["handoff"],
        "claims": {
            "joined_prelayout_gate_reviewed": True,
            "current_hardware_and_firmware_contracts_agree": True,
            "virtual_prelayout_blocker_open": False,
            "runtime_boot_proven": False,
            "physical_hardware_proven": False,
            "routing_proven": False,
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
    print("ok: global H4-R2 acceptance is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
