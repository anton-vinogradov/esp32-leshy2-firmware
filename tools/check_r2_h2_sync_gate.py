#!/usr/bin/env python3
"""Keep R2 firmware fail-closed against the historical single-RP H2 export."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "config" / "r2_h2_sync_gate.json"
H0_PATH = ROOT / "config" / "h0_r2_hardware_contract.json"
BSP_PATH = ROOT / "config" / "hardware_bsp_contract.json"
INTEGRATION_PATH = ROOT / "config" / "hardware_integration_contract.json"

DOMAIN_IDS = ["s3", "c5", "rf_rp", "hub_rp", "pack", "safety"]
RP_DOMAINS = ["rf_rp", "hub_rp"]
RP_MPN = "SC1512-A4"
HISTORICAL_BSP_AUTHORITY = {
    "baseline": "R1",
    "lifecycle": "historical_single_rp_import",
    "allowed_as_r2_authority": False,
    "superseded_by": "config/h0_r2_hardware_contract.json",
    "r2_sync_gate": "config/r2_h2_sync_gate.json",
}
HISTORICAL_INTEGRATION_AUTHORITY = {
    "baseline": "R1",
    "lifecycle": "historical_single_rp_integration_contract",
    "allowed_as_r2_authority": False,
    "superseded_by": "config/h0_r2_hardware_contract.json",
    "r2_sync_gate": "config/r2_h2_sync_gate.json",
}
M1_COUNTS = {
    "live_signals": 25,
    "main_power": 14,
    "aon_power": 2,
    "returns": 25,
    "no_connect_reserve": 14,
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_domain_id(row: dict) -> str:
    raw = row.get("id") or row.get("domain") or row.get("instance") or ""
    normalized = str(raw).strip().lower()
    aliases = {
        "rp": "rp",
        "pack_admission": "pack",
        "safety_controller": "safety",
    }
    return aliases.get(normalized, normalized)


def expected_m1(h0: dict) -> dict:
    interboard = h0.get("interboard", {})
    return {
        "connector": interboard.get("connector"),
        "current_budget": interboard.get("current_budget"),
        "pin_map": interboard.get("pin_map"),
    }


def export_ready_for_r2(h0: dict, bsp: dict, integration: dict) -> bool:
    """Require explicit six-domain reconciliation; never infer RP pin order."""

    authority = bsp.get("authority", {})
    integration_authority = integration.get("authority", {})
    if authority.get("baseline") != "R2" or authority.get("allowed_as_r2_authority") is not True:
        return False
    if (
        integration_authority.get("baseline") != "R2"
        or integration_authority.get("allowed_as_r2_authority") is not True
    ):
        return False

    bsp_domains = bsp.get("bsp", {}).get("domains", [])
    integration_domains = integration.get("controllers", [])
    if [normalized_domain_id(row) for row in bsp_domains] != DOMAIN_IDS:
        return False
    if [normalized_domain_id(row) for row in integration_domains] != DOMAIN_IDS:
        return False
    rp_rows = [row for row in bsp_domains if normalized_domain_id(row) in RP_DOMAINS]
    if len(rp_rows) != 2 or any(row.get("mpn") != RP_MPN for row in rp_rows):
        return False

    reconciliation = bsp.get("r2_reconciliation", {})
    if reconciliation.get("source_contract") != "config/h0_r2_hardware_contract.json":
        return False
    if reconciliation.get("hardware_source_sha256") != h0.get("hardware_source_sha256"):
        return False
    if reconciliation.get("domain_ids") != DOMAIN_IDS:
        return False
    if reconciliation.get("rp_domains") != RP_DOMAINS:
        return False
    return reconciliation.get("interboard") == expected_m1(h0)


def check(gate: dict, h0: dict, bsp: dict, integration: dict) -> list[str]:
    errors: list[str] = []
    if gate.get("schema_version") != 1 or gate.get("id") != "FW-R2-H2-AUTHORITY-GATE":
        errors.append("R2/H2 authority gate identity changed")

    domains = h0.get("domains", [])
    if [row.get("id") for row in domains] != DOMAIN_IDS:
        errors.append("active H0-R2 projection must contain the exact six domains")
    rp_rows = [row for row in domains if row.get("id") in RP_DOMAINS]
    if len(rp_rows) != 2 or any(row.get("mpn") != RP_MPN for row in rp_rows):
        errors.append("active H0-R2 projection must contain two SC1512-A4 RP domains")

    interboard = h0.get("interboard", {})
    if len(interboard.get("pin_map", [])) != 80:
        errors.append("active H0-R2 M1 must contain exactly 80 contacts")
    if interboard.get("current_budget") != {"positions": 80, **M1_COUNTS}:
        errors.append("active H0-R2 M1 accounting changed")

    requirements = gate.get("required_h2_export", {})
    expected_requirements = {
        "domain_ids": DOMAIN_IDS,
        "rp_domains": RP_DOMAINS,
        "rp_mpn": RP_MPN,
        "interboard_source": "config/h0_r2_hardware_contract.json#/interboard",
        "interboard_positions": 80,
        "interboard_counts": M1_COUNTS,
        "exact_rp_pin_map_required_here": False,
    }
    if requirements != expected_requirements:
        errors.append("R2/H2 export requirements changed or invented exact RP pins")

    current_ready = export_ready_for_r2(h0, bsp, integration)
    if bsp.get("integration_contract") != integration:
        errors.append("BSP and standalone integration-contract copies diverged")
    claimed_sync = gate.get("r2_h2_synchronized")
    if claimed_sync is not current_ready:
        errors.append("R2/H2 synchronization claim does not match the candidate H2 export")

    if current_ready:
        if gate.get("status") != "reviewed_six_domain_h2_export":
            errors.append("ready six-domain H2 export is not marked reviewed")
    else:
        if gate.get("status") != "blocked_pending_six_domain_h2_export":
            errors.append("missing R2 H2 export must keep the gate blocked")
        if bsp.get("authority") != HISTORICAL_BSP_AUTHORITY:
            errors.append("single-RP BSP import is not explicitly historical and non-authoritative")
        if integration.get("authority") != HISTORICAL_INTEGRATION_AUTHORITY:
            errors.append("single-RP integration import is not explicitly historical and non-authoritative")

    expected_claims = {
        "h0_r2_projection_is_current_firmware_authority": True,
        "historical_single_rp_import_can_authorize_r2": False,
        "six_domain_h2_export_available": current_ready,
        "r2_h2_ecad_and_firmware_synchronized": current_ready,
        "exact_rp_pin_order_invented": False,
        "qualification_or_execution_evidence_created": False,
    }
    if gate.get("claims") != expected_claims:
        errors.append("R2/H2 authority claims changed or overstate evidence")
    return errors


def main() -> int:
    gate = load(GATE_PATH)
    h0 = load(H0_PATH)
    bsp = load(BSP_PATH)
    integration = load(INTEGRATION_PATH)
    errors = check(gate, h0, bsp, integration)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if gate["r2_h2_synchronized"]:
        print("R2/H2 sync gate OPEN: six domains, two SC1512-A4 RP domains and exact H0 M1 exported")
    else:
        print(
            "R2/H2 sync gate CLOSED as required: historical five-domain single-RP H2 import "
            "cannot authorize R2; exact RP pin order remains uninvented"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
