#!/usr/bin/env python3
"""Import the reviewed H3-R2 phase boundary and owned residual register."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HW = ROOT.parent / "esp32-leshy2"
ACCEPTANCE = HW / "hardware/verification/generated/H3-R2-acceptance-package.json"
CROSSCHECK = HW / "hardware/verification/generated/H3-R2-crosscheck.json"
RESIDUALS = HW / "hardware/verification/generated/H3-R2-physical-residuals.json"
OUTPUT = ROOT / "config/h3_r2_acceptance.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    acceptance = load(ACCEPTANCE)
    crosscheck = load(CROSSCHECK)
    residuals = load(RESIDUALS)
    registry = residuals.get("registry", [])
    obligations = crosscheck.get("firmware_obligations", [])
    if (
        acceptance.get("marker") != "H3-R2.7"
        or acceptance.get("status") != "reviewed"
        or acceptance.get("result", {}).get("open_analytical_findings") != 0
        or acceptance.get("result", {}).get("next_marker") != "H4-R2.0.1"
        or crosscheck.get("summary", {}).get("current_artifacts") != 20
        or crosscheck.get("summary", {}).get("hash_mismatches") != 0
        or crosscheck.get("summary", {}).get("open_analytical_findings") != 0
        or not crosscheck.get("checks")
        or not all(crosscheck["checks"].values())
        or len(registry) != 51
        or residuals.get("summary", {}).get("unassigned") != 0
        or not all(row.get("status") == "physical_evidence_required" for row in registry)
        or len(obligations) != 1
        or obligations[0].get("owner") != "F5/F6"
    ):
        raise ValueError("hardware H3-R2.7 acceptance evidence is not closed")

    return {
        "schema_version": 1,
        "artifact": "FW-H3-R2.7-acceptance-import",
        "status": "reviewed_hardware_phase_imported",
        "hardware_marker": "H3-R2.7",
        "current_hardware_substep": "H4-R2.0.1",
        "sources": {
            "acceptance": {"path": "../esp32-leshy2/hardware/verification/generated/H3-R2-acceptance-package.json", "sha256": sha256(ACCEPTANCE)},
            "crosscheck": {"path": "../esp32-leshy2/hardware/verification/generated/H3-R2-crosscheck.json", "sha256": sha256(CROSSCHECK)},
            "physical_residuals": {"path": "../esp32-leshy2/hardware/verification/generated/H3-R2-physical-residuals.json", "sha256": sha256(RESIDUALS)},
        },
        "reviewed_boundary": {
            "current_artifacts": crosscheck["summary"]["current_artifacts"],
            "recorded_source_hashes_checked": crosscheck["summary"]["recorded_source_hashes_checked"],
            "hash_mismatches": 0,
            "open_analytical_findings": 0,
            "physical_residuals": len(registry),
            "physical_residuals_by_stage": residuals["summary"]["by_closure_stage"],
        },
        "firmware_obligations": obligations,
        "firmware_invariants": {
            "h4_join": "H4-R2 consumes current R2 evidence only; retained R1 F3/F4 execution evidence is regression evidence, not current-topology proof",
            "i8080": "F5/F6 must instantiate and exercise the locked 20-MHz, 8-bit, CS=-1, rising-edge-capture display contract",
            "physical_residuals": "firmware may collect evidence but cannot mark an H5/H6/H8 residual complete without its required physical artifact",
            "release": "H3 completion does not authorize purchase, PCB placement/routing, fabrication or a final-product claim",
        },
        "claims": {
            "h3_r2_analytical_scope_imported": True,
            "h4_r2_join_complete": False,
            "i8080_target_implementation_proven": False,
            "physical_residuals_complete": False,
            "purchasing_or_fabrication_authorized": False,
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
    print("ok: reviewed H3-R2.7 phase boundary is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
