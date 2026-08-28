#!/usr/bin/env python3
"""Retain the reviewed single-RP H2 export as historical R1 evidence.

The current R2 firmware authority is ``config/h0_r2_hardware_contract.json``.
This importer deliberately decorates the former five-domain H2 export as
historical on every write so a routine hardware hash refresh cannot silently
promote it back into an R2 hardware authority.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    REPO.parent
    / "esp32-leshy2"
    / "hardware/ecad/generated/H2-hwfw-contract.json"
)
BSP_OUTPUT = REPO / "config/hardware_bsp_contract.json"
INTEGRATION_OUTPUT = REPO / "config/hardware_integration_contract.json"

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


def render(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def validate(data: dict) -> None:
    if data.get("export_id") != "LESHY2-H2-HWFW-1":
        raise ValueError("unexpected hardware export identity")
    if (
        data.get("stage") != "H2.0.3"
        or data.get("status") != "reviewed_historical_r1_hwfw_export"
    ):
        raise ValueError(
            "firmware may retain only the reviewed historical R1 H2.0.3 export"
        )
    authority = data.get("authority", {})
    if (
        authority.get("generation") != "historical_single_rp_r1"
        or authority.get("current_r2_authority") is not False
    ):
        raise ValueError("historical H2 export must remain forbidden as R2 authority")
    integration = data.get("integration_contract", {})
    if integration.get("contract_id") != "LESHY2-HWFW-1":
        raise ValueError("unexpected integration-contract identity")
    if integration.get("review_status") != "h2_0_3_reviewed":
        raise ValueError("integration contract is not reviewed at H2.0.3")

    domains = data.get("bsp", {}).get("domains", [])
    if {row.get("domain") for row in domains} != {"S3", "C5", "RP", "PACK", "SAFETY"}:
        raise ValueError("BSP contract must expose all five firmware domains")
    if data["bsp"].get("temporary_pin_assignments_allowed") is not False:
        raise ValueError("temporary target pin assignments are forbidden")
    contacts = [
        (domain["instance"], pin["contact"])
        for domain in domains
        for pin in domain["pins"]
    ]
    if len(contacts) != len(set(contacts)) or len(contacts) != 125:
        raise ValueError("programmable-contact ledger is incomplete or duplicated")

    service = integration.get("physical_service", {})
    if (
        len(service.get("external_usb", [])),
        len(service.get("external_side_controls", [])),
        len(service.get("internal_fallback_headers", [])),
    ) != (3, 6, 3):
        raise ValueError("physical service boundary must remain 3 USB / 6 buttons / 3 internal DBG10")


def historical_outputs(data: dict) -> tuple[dict, dict]:
    """Return stable firmware copies with an explicit non-R2 authority marker."""

    bsp = copy.deepcopy(data)
    # Never trust an authority marker copied from the hardware-side evidence.
    # The firmware import has its own explicit, fail-closed lifecycle contract.
    bsp["authority"] = copy.deepcopy(HISTORICAL_BSP_AUTHORITY)
    integration = copy.deepcopy(bsp["integration_contract"])
    integration["authority"] = copy.deepcopy(HISTORICAL_INTEGRATION_AUTHORITY)
    bsp["integration_contract"] = copy.deepcopy(integration)
    return bsp, integration


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    source = args.source.resolve()
    data = json.loads(source.read_text(encoding="utf-8"))
    validate(data)
    bsp, integration = historical_outputs(data)
    expected = {
        BSP_OUTPUT: render(bsp),
        INTEGRATION_OUTPUT: render(integration),
    }
    if args.write:
        for path, content in expected.items():
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
        return 0

    stale = [
        path
        for path, content in expected.items()
        if not path.is_file() or path.read_text(encoding="utf-8") != content
    ]
    if stale:
        for path in stale:
            print(f"stale: {path.relative_to(REPO)}")
        return 1
    print(
        "ok: historical R1 HW/FW and BSP contracts match the reviewed "
        "single-RP hardware H2.0.3 export and remain forbidden as R2 authority"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
