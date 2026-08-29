#!/usr/bin/env python3
"""Keep R2 firmware fail-closed against the historical single-RP H2 export."""

from __future__ import annotations

import hashlib
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
    "live_signals": 24,
    "main_power": 14,
    "aon_power": 2,
    "returns": 24,
    "no_connect_reserve": 16,
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


def expected_domain_contracts(h0: dict) -> list[dict]:
    """Return the exact six-domain identity and published pin boundary."""
    return h0.get("domain_contracts", [])


def canonical_domain_contracts(rows: object) -> list[dict] | None:
    """Normalize only the security-relevant fields of an H2 domain export."""

    if not isinstance(rows, list):
        return None
    contracts = []
    for row in rows:
        if not isinstance(row, dict):
            return None
        domain_id = normalized_domain_id(row)
        contract = {"id": domain_id, "mpn": row.get("mpn")}
        if domain_id in {"s3", "c5", "rf_rp", "hub_rp", "pack", "safety"}:
            contract["pin_map"] = row.get("pin_map")
        contracts.append(contract)
    return contracts


def canonical_contract_sha256(h0: dict) -> str:
    payload = json.dumps(
        h0, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def expected_reconciliation(h0: dict) -> dict:
    return {
        "source_contract": "config/h0_r2_hardware_contract.json",
        "hardware_contract_sha256": canonical_contract_sha256(h0),
        "hardware_marker": h0.get("hardware_marker"),
        "hardware_sources": h0.get("hardware_sources"),
        "domain_ids": DOMAIN_IDS,
        "domain_contracts": expected_domain_contracts(h0),
        "rp_domains": RP_DOMAINS,
        "hub_pin_map": h0.get("hub_pin_map"),
        "rear_pin_map": h0.get("rear_pin_map"),
        "c5_sdio_service_mux": h0.get("c5_sdio_service_mux"),
        "interboard": expected_m1(h0),
        "pre_h2_gates": [],
        "physical_h1": h0.get("physical_h1"),
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

    expected_domains = expected_domain_contracts(h0)
    if canonical_domain_contracts(bsp.get("bsp", {}).get("domains")) != expected_domains:
        return False
    if canonical_domain_contracts(integration.get("controllers")) != expected_domains:
        return False
    if h0.get("pre_h2_gates") != []:
        return False
    physical_h1 = h0.get("physical_h1", {})
    if (
        physical_h1.get("status") != "reviewed"
        or physical_h1.get("current_h1_blockers") != []
        or physical_h1.get("pre_r2_h2_gates") != []
    ):
        return False

    reconciliation = bsp.get("r2_reconciliation", {})
    if reconciliation != expected_reconciliation(h0):
        return False
    if integration.get("r2_reconciliation") != reconciliation:
        return False
    return bsp.get("integration_contract") == integration


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
        "all_domain_mpns_source": "config/h0_r2_hardware_contract.json#/domains",
        "rp_domains": RP_DOMAINS,
        "rp_mpn": RP_MPN,
        "interboard_source": "config/h0_r2_hardware_contract.json#/interboard",
        "interboard_positions": 80,
        "interboard_counts": M1_COUNTS,
        "exact_rp_pin_map_required_here": True,
        "working_pin_map_source": "config/h0_r2_hardware_contract.json#/hub_pin_map and #/rear_pin_map",
        "working_pin_map_marker": "H1-R2.31",
        "six_domain_pin_maps_source": "config/h0_r2_hardware_contract.json#/domain_contracts",
        "integration_controllers_required_exact": True,
        "c5_mux_source": "config/h0_r2_hardware_contract.json#/c5_sdio_service_mux",
        "hardware_source_hashes": "config/h0_r2_hardware_contract.json#/hardware_sources",
        "unresolved_pre_h2_gates_required": 0,
        "physical_h1_source": "config/h0_r2_hardware_contract.json#/physical_h1",
        "physical_h1_status_required": "reviewed",
        "physical_h1_blockers_required": 0,
        "physical_pre_r2_h2_gates_required": 0,
    }
    if requirements != expected_requirements:
        errors.append("R2/H2 export requirements lost the imported exact working boundary")

    if len(h0.get("hub_pin_map", [])) != 48 or len(h0.get("rear_pin_map", [])) != 48:
        errors.append("current pre-H2 authority must contain both exact 48-GPIO RP maps")
    if h0.get("hardware_marker") != "H1-R2.31":
        errors.append("current pre-H2 authority is not H1-R2.31")
    c5 = h0.get("c5_sdio_service_mux", {})
    if c5.get("performance", {}).get("bus_width_bits") != 4:
        errors.append("current pre-H2 authority lost C5 4-bit SDIO")
    hardware_sources = h0.get("hardware_sources", {})
    if not hardware_sources or any(not row.get("path") or not row.get("sha256")
                                   for row in hardware_sources.values()):
        errors.append("current pre-H2 authority lost its exact hardware source hashes")
    physical_h1 = h0.get("physical_h1", {})
    if physical_h1.get("pin_authority_marker") != h0.get("hardware_marker"):
        errors.append("physical H1 lost its exact pin-authority marker")
    if physical_h1.get("marker") != "H1-R2.36":
        errors.append("physical H1 projection is not the current H1-R2.36 design")
    if "pre_r2_h2_gates" not in physical_h1:
        errors.append("physical H1 projection lost its pre-R2/H2 factory gates")

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
        if gate.get("status") != "blocked_pending_six_domain_h2_export_and_open_factory_gates":
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
        "exact_dual_rp_working_map_imported": True,
        "c5_quad_sdio_mux_contract_imported": True,
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
        print(
            "R2/H2 sync gate OPEN: exact domains, dual-RP maps, C5 mux/source hashes and "
            "H0 M1 exported with reviewed physical H1 and zero unresolved pre-H2 gates"
        )
    else:
        print(
            "R2/H2 sync gate CLOSED as required: historical five-domain single-RP H2 import "
            "cannot authorize R2; exact H1-R2.31 working pins remain pre-H2 only"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
