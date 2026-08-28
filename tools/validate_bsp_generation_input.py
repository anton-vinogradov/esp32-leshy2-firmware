#!/usr/bin/env python3
"""Validate the reviewed H2 contract as deterministic BSP-generator input."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = REPO_ROOT / "config" / "bsp_generation_input.json"
IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
GPIO_CONTACT_RE = re.compile(r"GPIO([0-9]+)")
PA_CONTACT_RE = re.compile(r"PA([0-9]+)(?:_[A-Za-z0-9_]+)?")


def load(relative: str) -> tuple[Path, dict]:
    path = REPO_ROOT / relative
    return path, json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


def main() -> int:
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    if model.get("stage") != "F2.3.0" or model.get("status") != "reviewed":
        errors.append("BSP generation input is not reviewed at F2.3.0")
    contract_path, contract = load(model.get("source_contract", ""))
    integration_path, integration = load(model.get("integration_contract", ""))
    identity = model.get("source_identity", {})
    expected_identity = {
        "export_id": contract.get("export_id"),
        "hardware_stage": contract.get("stage"),
        "hardware_status": contract.get("status"),
        "contract_id": integration.get("contract_id"),
        "review_status": integration.get("review_status"),
        "source_sha256": digest(contract_path),
        "integration_sha256": digest(integration_path),
    }
    if identity != expected_identity:
        errors.append("reviewed hardware source identity or digest changed")
    if contract.get("integration_contract") != integration:
        errors.append("standalone integration contract differs from the H2 export")
    authority = contract.get("authority", {})
    integration_authority = integration.get("authority", {})
    if (
        authority.get("baseline") != "R1"
        or authority.get("lifecycle") != "historical_single_rp_import"
        or authority.get("allowed_as_r2_authority") is not False
    ):
        errors.append("legacy BSP input is not fail-closed as historical single-RP R1")
    if (
        integration_authority.get("baseline") != "R1"
        or integration_authority.get("lifecycle")
        != "historical_single_rp_integration_contract"
        or integration_authority.get("allowed_as_r2_authority") is not False
    ):
        errors.append("legacy integration input is not fail-closed as historical R1")
    if contract.get("bsp", {}).get("temporary_pin_assignments_allowed") is not False:
        errors.append("temporary pin assignments must remain forbidden")

    expected_domains = model.get("domains", [])
    actual_domains = contract.get("bsp", {}).get("domains", [])
    if len(actual_domains) != len(expected_domains):
        errors.append("domain count changed")

    all_pins: list[dict] = []
    contact_keys: list[tuple[str, str]] = []
    pin_model = model.get("pin_model", {})
    required_fields = set(pin_model.get("required_fields", []))
    optional_fields = set(pin_model.get("optional_proof_fields", []))
    allowed_fields = required_fields | optional_fields
    allowed_directions = set(pin_model.get("directions", []))
    allowed_controllers = set(pin_model.get("controllers", []))

    for expected, actual in zip(expected_domains, actual_domains, strict=False):
        for key in ("domain", "instance", "mpn"):
            if actual.get(key) != expected.get(key):
                errors.append(f"{expected.get('domain', '?')}: {key} changed")
        pins = actual.get("pins", [])
        if actual.get("allocated_contact_count") != expected.get("contacts"):
            errors.append(f"{expected.get('domain', '?')}: allocated count changed")
        if len(pins) != expected.get("contacts"):
            errors.append(f"{expected.get('domain', '?')}: pin row count changed")

        domain = expected.get("domain", "?")
        for pin in pins:
            fields = set(pin)
            if not required_fields <= fields:
                errors.append(f"{domain}.{pin.get('contact', '?')}: missing required field")
            if fields - allowed_fields:
                errors.append(
                    f"{domain}.{pin.get('contact', '?')}: unmodelled fields "
                    f"{sorted(fields - allowed_fields)}"
                )
            if pin.get("instance") != expected.get("instance"):
                errors.append(f"{domain}.{pin.get('contact', '?')}: owner instance changed")
            for field in ("instance", "contact", "net", "controller"):
                if not IDENTIFIER_RE.fullmatch(str(pin.get(field, ""))):
                    errors.append(f"{domain}.{pin.get('contact', '?')}: invalid {field}")
            if pin.get("direction") not in allowed_directions:
                errors.append(f"{domain}.{pin.get('contact', '?')}: unknown direction")
            if pin.get("controller") not in allowed_controllers:
                errors.append(f"{domain}.{pin.get('contact', '?')}: unknown controller")
            if not isinstance(pin.get("peers"), list) or not pin.get("peers"):
                errors.append(f"{domain}.{pin.get('contact', '?')}: peers must be non-empty")
            if any(
                not isinstance(peer, str)
                or ("." not in peer and not peer.startswith("abstract:"))
                for peer in pin.get("peers", [])
            ):
                errors.append(f"{domain}.{pin.get('contact', '?')}: invalid peer reference")

            contact = str(pin.get("contact", ""))
            contact_match = (
                GPIO_CONTACT_RE.fullmatch(contact)
                if domain in {"S3", "C5", "RP"}
                else PA_CONTACT_RE.fullmatch(contact)
            )
            if contact_match is None:
                errors.append(f"{domain}.{contact}: contact-number rule cannot parse contact")

            all_pins.append(pin)
            contact_keys.append((str(pin.get("instance")), contact))

    if len(contact_keys) != len(set(contact_keys)):
        errors.append("duplicate programmable contact in generator input")

    counts = model.get("expected_counts", {})
    net_counts = Counter(str(pin.get("net")) for pin in all_pins)
    actual_counts = {
        "domains": len(actual_domains),
        "allocated_contacts": len(all_pins),
        "unique_nets": len(net_counts),
        "shared_nets": sum(value > 1 for value in net_counts.values()),
        "strap_proofs": sum("strap_proof" in pin for pin in all_pins),
        "sharing_proofs": sum("sharing_proof" in pin for pin in all_pins),
        "reset_proofs": sum("reset_proof" in pin for pin in all_pins),
        "transports": len(integration.get("transports", [])),
        "signal_groups": len(integration.get("signal_groups", [])),
    }
    if counts != actual_counts:
        errors.append(f"generator input counts changed: {actual_counts}")

    endpoints = {
        f"{pin['instance']}.{pin['contact']}": pin["net"]
        for pin in all_pins
    }
    for transport in integration.get("transports", []):
        for role, references in transport.get("pins", {}).items():
            if len(references) != 2:
                errors.append(f"{transport.get('id')}.{role}: endpoint count is not two")
                continue
            resolved = [endpoints.get(reference) for reference in references]
            if None in resolved or len(set(resolved)) != 1:
                errors.append(f"{transport.get('id')}.{role}: endpoints do not resolve to one net")

    domain_names = {domain.get("domain") for domain in actual_domains}
    for group in integration.get("signal_groups", []):
        if group.get("owner") not in domain_names:
            errors.append(f"signal group {group.get('firmware')} has an unknown owner")

    claims = model.get("claims", {})
    if claims.get("input_model_validated") is not True:
        errors.append("F2.3.0 input model is not claimed validated")
    for unexecuted in (
        "generated_sources_created",
        "target_projects_consume_generated_sources",
        "target_configure_run",
        "target_builds_run",
    ):
        if claims.get(unexecuted) is not False:
            errors.append(f"F2.3.0 cannot claim {unexecuted}")

    if errors:
        return fail(errors)
    print(
        "BSP generation input OK: 5 domains, 125 contacts, 112 nets, "
        "4 transports and 10 signal groups; input-only review"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
