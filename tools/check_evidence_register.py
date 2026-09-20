#!/usr/bin/env python3
"""Bind TCA9535 through current H2 native ledgers and source provenance.

This does not perform a fresh KiCad/PCB pad export; that check remains separate.
Neither ledger agreement nor host-only helpers grant runtime/EV qualification.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
HW_ROOT = ROOT.parent / "esp32-leshy2"
PROTOCOL = ROOT / "config/interdomain_protocol.json"
POLICY = ROOT / "config/u219_cap_policy.json"
HEADER = ROOT / "common/include/leshy2/evidence_register.h"
SOURCE = ROOT / "common/src/evidence_register.c"
RAW_EV_MASK, LOGICAL_EV_MASK = 0x81FF, 0x11FF
REQUIRED_INPUT_MASK, SERVICE_OUTPUT_MASK = 0xE3FF, 0x1C00
IDENTITY = {"project": "LESHY2-RF-R2", "instance": "evidence_mask", "reference": "U111",
            "device_id": "ti_tca9535_pwr", "mpn": "TCA9535PWR",
            "footprint": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm"}
# Physical port index is 8 * port + pin, not the decimal suffix of Pxy.
CONTACTS = (
    ("P00", "4", "EV_N0_S3", 0), ("P01", "5", "EV_N1_C5", 1),
    ("P02", "6", "EV_N2_NRF0", 2), ("P03", "7", "EV_N3_NRF1", 3),
    ("P04", "8", "EV_N4_NRF2", 4), ("P05", "9", "EV_N5_CC", 5),
    ("P06", "10", "EV_N6_VOICE", 6), ("P07", "11", "EV_N7_IR", 7),
    ("P10", "13", "EV_N8_LORA_EXT", 8), ("P11", "14", "FAULT_ASSERT_SENSE", None),
    ("P12", "15", "C5_MUX_SEL_REQUEST", None), ("P13", "16", "C5_SERVICE_PATH_ACK", None),
    ("P14", "17", "AON_SERVICE_RELEASE_REQ", None), ("P15", "18", "C5_SERVICE_OWNED", None),
    ("P16", "19", "HUB_AON_ALERT_N", None), ("P17", "20", "EV_N9_U219_NFC", 12),
)
LOGICAL_NAMES = ["S3_RF", "C5_RF", "NRF0_RF", "NRF1_RF", "NRF2_RF", "CC_RF",
                 "VOICE_RF", "IR_OPTICAL", "LORA_EXT_RF", None, None, None, "EV_N9_U219_NFC"]


def _crossings():
    if not (HW_ROOT / "hardware/verification/h6_r2_power_domain_crossings.py").is_file():
        raise FileNotFoundError("current sibling hardware provenance checker is unavailable")
    if str(HW_ROOT) not in sys.path:
        sys.path.insert(0, str(HW_ROOT))
    module = importlib.import_module("hardware.verification.h6_r2_power_domain_crossings")
    if module.ROOT.resolve() != HW_ROOT.resolve():
        raise ValueError("hardware checker resolved outside the current sibling repository")
    return module


def source_paths():
    """Files to guard before/after consumers; missing sibling is not qualified."""
    paths = {Path(__file__), PROTOCOL, POLICY, HEADER, SOURCE,
             ROOT / "tools/check_u219_cap_policy.py", *_crossings().source_paths()}
    for path in paths:
        if not path.is_absolute() or path.resolve() != path or path.is_symlink():
            raise ValueError("noncanonical or symlinked evidence source: " + str(path))
        if not any(path.is_relative_to(root) for root in (ROOT, HW_ROOT)):
            raise ValueError("evidence source outside current repositories: " + str(path))
    return sorted(paths)


def _same(left, right):
    # JSON types matter: booleans/floats are not integer contact/ABI indices.
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def _snapshot():
    return {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths()}


def _validate(data, reviews, protocol, policy):
    """Validate supplied content; build() additionally requires fresh provenance."""
    c = _crossings()
    native, by_instance = c.indexes(data, reviews)
    key = (IDENTITY["project"], IDENTITY["instance"])
    part = native.get(key, {})
    c.require(all(part.get(k) == value for k, value in IDENTITY.items()), "TCA native identity differs")
    c.require(reviews.get(IDENTITY["device_id"], {}).get("mpn") == IDENTITY["mpn"], "TCA reviewed identity differs")
    pins = {row["contact"]: row for row in by_instance[key]}
    c.require({name for name in pins if name.startswith("P")} == {row[0] for row in CONTACTS},
              "TCA port contact coverage differs")
    actual = []
    for raw_bit, (contact, pad, net, logical_bit) in enumerate(CONTACTS):
        pin = pins[contact]
        c.require(pin.get("physical") == pad and pin.get("pads") == [pad]
                  and pin.get("net") == net and pin.get("type") == "bidirectional"
                  and pin.get("disposition") == "connected", "TCA physical contact differs: " + contact)
        actual.append({"contact": contact, "pad": pad, "net": pin["net"],
                       "raw_bit": raw_bit, "logical_bit": logical_bit})
    for contact, pad, net in (("VCC", "24", "AON_SAFE_3V3"), ("GND", "12", "POWER_GROUND"),
                              ("A0", "21", "POWER_GROUND"), ("A1", "2", "POWER_GROUND"),
                              ("A2", "3", "POWER_GROUND")):
        pin = pins[contact]
        c.require(pin.get("physical") == pad and pin.get("pads") == [pad] and pin.get("net") == net
                  and pin.get("disposition") == "connected", "TCA supply/address differs: " + contact)
    register = protocol["evidence_register"]
    expected = {"device": "TCA9535PWR", "i2c_7bit_address": "0x20", "width_bits": 16,
                "polarity": "active_low", "used_bits": 10, "bit_names": LOGICAL_NAMES,
                "unused_bits": [9, 10, 11, 13, 14, 15], "bit_numbering": "logical_evidence_abi",
                "logical_asserted_level": 1}
    c.require(all(_same(register.get(k), value) for k, value in expected.items()), "logical evidence ABI differs")
    binding = register["physical_binding"]
    expected_binding = {"identity": IDENTITY, "contacts": actual, "raw_word_order": "port0_low_byte_port1_high_byte",
        "raw_evidence_mask": "0x81ff", "logical_evidence_mask": "0x11ff",
        "required_input_mask": "0xe3ff", "service_output_allowed_mask": "0x1c00",
        "evidence_polarity_inversion_mask": "0x0000", "runtime_driver_implemented": False,
        "gpio_modes_proven": False, "pull_modes_proven": False}
    c.require(_same(binding, expected_binding), "physical evidence binding differs")
    groups = protocol["signal_groups"]
    c.require(len({row["name"] for row in groups}) == len(groups), "duplicate signal group")
    masks = {"S3_RF": [0], "C5_RF": [1], "NRF24": [2, 3, 4], "CC1101": [5], "VOICE": [6],
             "IR": [7], "LORA_CAP": [8], "U219_NFC": [12], "NONE": [], "M5_UNIT": [], "BROADCAST_RX": []}
    c.require(_same({row["name"]: row["evidence_bits"] for row in groups}, masks), "signal-group evidence ABI differs")
    ev9 = policy["nfc_reader"]["evidence"]
    c.require(_same(ev9, {"name": "EV_N9_U219_NFC", "register": "TCA9535PWR", "input": "P17",
        "raw_bit": 15, "bit": 12, "bit_numbering": "logical_evidence_abi", "polarity": "active_low",
        "aggregate": "ANY_TX_AON_N", "lease_group": "U219_NFC"}), "U219 physical/logical evidence binding differs")
    c.require(policy["implementation"].get("target_adapter_integrated") is False, "U219 target adapter overclaimed")
    header = HEADER.read_text(encoding="utf-8")
    for macro, value in (("L2_EVIDENCE_TCA9535_RAW_MASK", RAW_EV_MASK),
                         ("L2_EVIDENCE_LOGICAL_MASK", LOGICAL_EV_MASK),
                         ("L2_EVIDENCE_TCA9535_REQUIRED_INPUT_MASK", REQUIRED_INPUT_MASK)):
        c.require(f"#define {macro} UINT16_C(0x{value:04x})" in header, "portable evidence constant differs: " + macro)
    return actual


def build():
    result = {"status": "fail", "scope": "current_H2_native_ledger_TCA9535_binding_with_source_provenance_only",
              "qualified": False, "full_EV_qualified": False, "runtime_driver_implemented": False,
              "gpio_modes_proven": False, "pull_modes_proven": False, "input_provenance_verified": False,
              "actual_mapping": [], "errors": [], "source_sha256": {},
              "limits": ["Current H2 native ledgers with source provenance; fresh KiCad/PCB checking is separate",
                         "Pure decode/readback helpers are host-tested only, not compiled into current SDK targets or connected to target drivers",
                         "No I2C transaction, runtime readback, Safety PA22 or C5 GPIO23/24 mode/pull proof",
                         "No loaded-voltage, current, timing, off-state or whole-EV qualification"]}
    try:
        c = _crossings()
    except FileNotFoundError as exc:
        result.update(status="unqualified", errors=[str(exc)])
        return result
    except (ValueError, OSError, ImportError) as exc:
        result["errors"] = [str(exc)]
        return result
    try:
        before = _snapshot()
        data = {key: c.load(c.ROOT / path) for key, path in c.INPUTS.items()}
        c.require(data["nets"].get("artifact") == "H2-R2-native-net-ledger", "current native ledger artifact required")
        contracts = {key: c.load(c.ROOT / path) for key, path in c.LEDGER_CONTRACTS.items()}
        hw_hashes = {str(Path(path).relative_to(c.ROOT)): digest for path, digest in before.items()
                     if Path(path).is_relative_to(c.ROOT)}
        c.validate_provenance(data, contracts, hw_hashes)
        reviews = c.semantics.reviewed_maps([c.load(p) for p in c.semantics.MAPS], data["material"]["groups"])
        actual = _validate(data, reviews, c.load(PROTOCOL), c.load(POLICY))
        c.require(_snapshot() == before, "evidence binding sources changed during check")
        result.update(status="pass", actual_mapping=actual, source_sha256=before, input_provenance_verified=True)
    except (ValueError, KeyError, TypeError, OSError, ImportError) as exc:
        result["errors"] = [str(exc)]
    return result


def main():
    result = build()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
