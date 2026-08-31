#!/usr/bin/env python3
"""Import the reviewed H4-R2.0.2/H4-R2.1 contract reconciliation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HW_ROOT = ROOT.parent / "esp32-leshy2"
RECONCILIATION = HW_ROOT / "hardware/verification/generated/H4-R2-contract-reconciliation.json"
JOINED = HW_ROOT / "hardware/verification/generated/H4-R2-joined-crosscheck.json"
OUTPUT = ROOT / "config/h4_r2_contract_reconciliation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    reconciliation = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
    joined = json.loads(JOINED.read_text(encoding="utf-8"))
    summary = reconciliation.get("summary", {})
    if (
        reconciliation.get("marker") != "H4-R2.0.2"
        or reconciliation.get("status") != "reviewed_with_corrections_required"
        or not reconciliation.get("checks")
        or not all(reconciliation["checks"].values())
        or summary.get("hardware_pin_rows") != 173
        or summary.get("generated_bsp_pin_rows") != 135
        or summary.get("missing_generated_bsp_rows") != 38
        or [row.get("domain") for row in reconciliation.get("corrections_required", [])] != ["c5", "pack", "safety"]
        or joined.get("marker") != "H4-R2.1"
        or joined.get("status") != "reviewed_corrections_required"
        or joined.get("summary", {}).get("unowned_contradictions") != 0
        or joined.get("next", {}).get("marker") != "H4-R2.2"
    ):
        raise ValueError("hardware H4-R2 contract reconciliation is not reviewed")
    return {
        "schema_version": 1,
        "artifact": "FW-H4-R2-contract-reconciliation-import",
        "status": "reviewed_hardware_contract_imported",
        "hardware_markers": ["H4-R2.0.2", "H4-R2.1"],
        "current_hardware_substep": "H4-R2.2",
        "sources": {
            "reconciliation": {"path": "../esp32-leshy2/hardware/verification/generated/H4-R2-contract-reconciliation.json", "sha256": sha256(RECONCILIATION)},
            "joined_crosscheck": {"path": "../esp32-leshy2/hardware/verification/generated/H4-R2-joined-crosscheck.json", "sha256": sha256(JOINED)},
        },
        "reviewed_boundary": {
            "domains": 6,
            "hardware_pin_rows": 173,
            "generated_bsp_pin_rows": 135,
            "missing_generated_bsp_rows": 38,
            "correction_domains": ["c5", "pack", "safety"],
            "unowned_contradictions": 0,
            "retained_firmware_obligations": 1,
            "physical_residuals_carried": 51,
        },
        "claims": {
            "hardware_firmware_contract_reconciliation_reviewed": True,
            "generated_bsp_complete": False,
            "joined_h4_complete": False,
            "i8080_target_implementation_proven": False,
            "physical_residuals_complete": False,
            "purchase_layout_or_fabrication_authorized": False,
        },
        "next": {"marker": "H4-R2.2", "action": "regenerate complete exact C5, Pack and Safety BSP maps and target guards"},
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
    print("ok: H4-R2.0.2/H4-R2.1 reconciliation is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
