#!/usr/bin/env python3
"""Validate the fail-closed U214/U219 firmware policy without claiming hardware."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config/u219_cap_policy.json"
PROTOCOL_PATH = ROOT / "config/interdomain_protocol.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    policy = load(POLICY_PATH)
    protocol = load(PROTOCOL_PATH)
    errors: list[str] = []

    if policy.get("policy_id") != "LESHY2-CAP-PROFILES-01":
        errors.append("unexpected Cap policy identity")
    if policy.get("status") != "host_policy_implemented_hardware_gate_open":
        errors.append("policy must keep the hardware gate open")

    reset = policy.get("reset_and_unknown", {})
    expected_reset = {
        "profile": "UNKNOWN",
        "cap_branch_power": False,
        "io_connected": False,
        "pin8_level": "low",
        "pin10_direction": "input",
        "pin10_output_preload": "high",
        "pin14_chip_select": "high",
    }
    for key, value in expected_reset.items():
        if reset.get(key) != value:
            errors.append(f"unsafe reset default: {key}")

    selection = policy.get("selection", {})
    if not selection.get("mutually_exclusive") or not selection.get("signature_required"):
        errors.append("profiles must be mutually exclusive and signed")
    if selection.get("hot_profile_change") is not False:
        errors.append("hot profile changes must remain forbidden")

    profiles = {row.get("id"): row for row in policy.get("profiles", [])}
    if set(profiles) != {"U214", "U219"}:
        errors.append("exact U214/U219 profile set changed")
    else:
        if profiles["U214"].get("pin10_active_role") != "LORA_BUSY input":
            errors.append("U214 pin 10 is no longer BUSY input")
        if profiles["U219"].get("pin10_active_role") != "NFC_CS output active low":
            errors.append("U219 pin 10 is no longer NFC_CS output")
        if "hard RX-only" not in profiles["U219"].get("cc1101_policy", ""):
            errors.append("U219 CC1101 is not hard RX-only")

    spi = {row["target"]: row for row in policy.get("shared_spi", {}).get("contracts", [])}
    if spi.get("U219_CC1101", {}).get("mode") != 0:
        errors.append("U219 CC1101 SPI mode must be 0")
    if spi.get("U219_ST25R3916", {}).get("mode") != 1:
        errors.append("U219 ST25R3916 SPI mode must be 1")
    if spi.get("U219_ST25R3916", {}).get("frequency_hz") != 10_000_000:
        errors.append("U219 ST25R3916 SPI rate must remain 10 MHz")

    firewall = policy.get("cc1101_rx_firewall", {})
    if firewall.get("raw_spi_access_outside_firewall") is not False:
        errors.append("raw CC1101 SPI bypass is enabled")
    for forbidden in ("SFSTXON", "STX"):
        if forbidden not in firewall.get("forbidden_strobes", []):
            errors.append(f"CC1101 firewall permits {forbidden}")
    for forbidden in ("PATABLE", "TX_FIFO"):
        if forbidden not in firewall.get("forbidden_write_targets", []):
            errors.append(f"CC1101 firewall permits {forbidden}")

    nfc = policy.get("nfc_reader", {})
    if nfc.get("allowed_operations") != ["POLL", "READ"]:
        errors.append("NFC operations are not poll/read only")
    if set(nfc.get("forbidden_operations", [])) != {"WRITE", "CARD_EMULATION"}:
        errors.append("NFC write/emulation ban changed")
    gate = nfc.get("compile_gate", {})
    if gate.get("macro") != "L2_U219_NFC_FIELD_HIL_CLOSED" or gate.get("default") != 0:
        errors.append("NFC field compile gate is not fail-closed")
    if gate.get("target_definitions") != []:
        errors.append("a target claims the U219 field gate is closed")
    evidence = nfc.get("evidence", {})
    if (evidence.get("input"), evidence.get("bit"), evidence.get("aggregate")) != (
        "P12", 12, "ANY_TX_AON_N"
    ):
        errors.append("EV_N9 evidence route changed")

    dependencies = policy.get("dependency_policy", {})
    if dependencies.get("st_driver_integrated") is not False:
        errors.append("policy falsely claims an ST driver integration")
    if any(row.get("status", "").find("not integrated") < 0 for row in dependencies.get("evaluated_not_integrated", [])):
        errors.append("reference dependency is presented as integrated")

    groups = {row["name"]: row for row in protocol.get("signal_groups", [])}
    if groups.get("U219_NFC", {}).get("evidence_bits") != [12]:
        errors.append("interdomain U219_NFC lease lacks P12 evidence")
    register = protocol.get("evidence_register", {})
    if register.get("used_bits") != 10 or 12 in register.get("unused_bits", []):
        errors.append("interdomain evidence register does not consume P12")
    bit_names = register.get("bit_names", [])
    if (
        not isinstance(bit_names, list)
        or len(bit_names) <= 12
        or bit_names[12] != "EV_N9_U219_NFC"
    ):
        errors.append("interdomain evidence register lost the P12 EV_N9 name")
    if protocol.get("cap_profile_policy", {}).get("canonical_contract") != str(
        POLICY_PATH.relative_to(ROOT)
    ):
        errors.append("interdomain contract lost the canonical policy link")

    header = (ROOT / "common/include/leshy2/system_model.h").read_text(encoding="utf-8")
    source = (ROOT / "common/src/system_model.c").read_text(encoding="utf-8")
    for token in (
        "#define L2_U219_NFC_FIELD_HIL_CLOSED 0",
        "L2_CAP_PROFILE_UNKNOWN",
        "L2_CAP_NFC_CARD_EMULATION",
        "L2_CC1101_WRITE_TX_FIFO",
    ):
        if token not in header:
            errors.append(f"portable header lost {token}")
    for token in (
        "L2_CC1101_STROBE_RX",
        "L2_CC1101_STROBE_RESET",
        "L2_CC1101_MCSM0_PIN_CTRL_EN",
        "L2_U219_NFC_FIELD_HIL_CLOSED == 0",
    ):
        if token not in source:
            errors.append(f"portable implementation lost {token}")

    for target_root in (ROOT / "targets").iterdir():
        if not target_root.is_dir():
            continue
        for path in target_root.rglob("*"):
            if path.is_file() and "L2_U219_NFC_FIELD_HIL_CLOSED" in path.read_text(
                encoding="utf-8", errors="ignore"
            ):
                errors.append(f"target closes unqualified U219 field gate: {path.relative_to(ROOT)}")

    docs = {
        "docs/architecture.md": ("Optional U214/U219 Cap profiles", "Host tests prove only"),
        "docs/architecture.ru.md": ("Опциональные Cap-профили U214/U219", "Host-тесты доказывают только"),
        "docs/roadmap.md": ("Optional U219 Cap policy", "VNA/HIL"),
        "docs/roadmap.ru.md": ("Политика опционального U219 Cap", "VNA/HIL"),
    }
    for relative, tokens in docs.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                errors.append(f"{relative} lost {token}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        "U219 Cap policy OK: signed exclusive profiles, CC1101 RX-only, "
        "NFC poll/read and EV_N9 field gate; 0 target/HIL runs claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
