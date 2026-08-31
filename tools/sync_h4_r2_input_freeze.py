#!/usr/bin/env python3
"""Import the reviewed H4-R2.0.1 cross-repository input freeze."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "esp32-leshy2/hardware/verification/generated/H4-R2-input-freeze.json"
OUTPUT = ROOT / "config/h4_r2_input_freeze.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    summary = source.get("summary", {})
    if (
        source.get("marker") != "H4-R2.0.1"
        or source.get("status") != "reviewed"
        or source.get("errors") != []
        or not source.get("checks")
        or not all(source["checks"].values())
        or summary.get("total_inputs") != 24
        or summary.get("cross_repository_h3_hash_mismatches") != 0
        or summary.get("physical_residuals_carried") != 51
        or summary.get("firmware_obligations_carried") != 1
        or source.get("next", {}).get("marker") != "H4-R2.0.2"
    ):
        raise ValueError("hardware H4-R2.0.1 input freeze is not reviewed")
    return {
        "schema_version": 1,
        "artifact": "FW-H4-R2.0.1-input-freeze-import",
        "status": "reviewed_hardware_contract_imported",
        "hardware_marker": "H4-R2.0.1",
        "current_hardware_substep": "H4-R2.0.2",
        "source": {
            "path": "../esp32-leshy2/hardware/verification/generated/H4-R2-input-freeze.json",
            "sha256": sha256(SOURCE),
        },
        "frozen_boundary": {
            "hardware_inputs": summary["hardware_inputs"],
            "firmware_inputs": summary["firmware_inputs"],
            "total_inputs": summary["total_inputs"],
            "cross_repository_h3_hashes_checked": summary["cross_repository_h3_hashes_checked"],
            "cross_repository_h3_hash_mismatches": 0,
            "physical_residuals_carried": 51,
            "firmware_obligations_carried": 1,
        },
        "next_contract": {
            "marker": "H4-R2.0.2",
            "purpose": "reconcile every hardware-visible firmware contract and retained implementation obligation",
        },
        "claims": {
            "joined_inputs_frozen": True,
            "joined_contract_reconciliation_complete": False,
            "physical_evidence_complete": False,
            "purchase_layout_or_fabrication_authorized": False,
        },
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
    print("ok: reviewed H4-R2.0.1 input freeze is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
