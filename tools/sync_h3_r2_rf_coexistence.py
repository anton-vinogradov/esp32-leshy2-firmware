#!/usr/bin/env python3
"""Import the reviewed H3-R2.5 RF/coexistence boundary into firmware."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "esp32-leshy2/hardware/verification/generated/H3-R2-rf-coexistence.json"
OUTPUT = ROOT / "config/h3_r2_rf_coexistence.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    summary = source.get("summary", {})
    checks = source.get("checks", {})
    microcoax = source.get("microcoax", {})
    expected_summary = {
        "checks": 71,
        "external_ports": 10,
        "front_ports": 5,
        "rear_ports": 5,
        "microcoaxes": 5,
        "active_signal_groups": 9,
        "quiet_contracts": 13,
        "nrf_role_modes": 4,
        "nrf_identity_permutations": 8,
        "analytical_findings_open": 0,
    }
    if (
        source.get("marker") != "H3-R2.5"
        or source.get("status") != "pass"
        or source.get("errors") != []
        or not checks
        or not all(value is True for value in checks.values())
        or any(summary.get(key) != value for key, value in expected_summary.items())
        or microcoax.get("status") != "pass"
        or microcoax.get("thirty_mm_paths") != 2
        or microcoax.get("sixty_mm_paths") != 3
        or float(microcoax.get("minimum_conservative_slack_mm", 0)) < 5.0
    ):
        raise ValueError("hardware H3-R2.5 RF/coexistence evidence is not closed")

    return {
        "schema_version": 1,
        "artifact": "FW-H3-R2.5-rf-coexistence-import",
        "status": "reviewed_hardware_contract_imported",
        "hardware_marker": source["marker"],
        "current_hardware_substep": "H4-R2.2",
        "source": {
            "path": "../esp32-leshy2/hardware/verification/generated/H3-R2-rf-coexistence.json",
            "sha256": sha256(SOURCE),
        },
        "port_topology": source["path_topology"],
        "microcoax": {
            "paths": microcoax["paths"],
            "thirty_mm_paths": microcoax["thirty_mm_paths"],
            "sixty_mm_paths": microcoax["sixty_mm_paths"],
            "minimum_conservative_slack_mm": microcoax["minimum_conservative_slack_mm"],
        },
        "quiet_matrix": source["quiet_matrix"],
        "nrf_concurrency": source["nrf_concurrency"],
        "runtime_invariants": {
            "top_level_radio_group": "admit exactly one active top-level signal group; unknown or stale ownership fails quiet",
            "nrf_parallelism": "within SG-N24, preserve independent ownership for nrf0/nrf1/nrf2 and all four reviewed role mixes",
            "rf_over_m1": "no main RF path may be synthesized over M1",
            "airband": "Airband is receive-only and reuses the selectable RX-FM/SW branch",
            "tx_evidence": "software permission never substitutes for the hardware TX-evidence chain",
        },
        "physical_residuals": source["physical_residuals"],
        "claims": {
            "runtime_radio_arbiter_implemented": False,
            "routed_rf_or_antenna_performance_measured": False,
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
    print("ok: reviewed H3-R2.5 RF/coexistence contract is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
