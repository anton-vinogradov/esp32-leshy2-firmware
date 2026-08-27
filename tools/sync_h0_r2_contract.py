#!/usr/bin/env python3
"""Project the reviewed hardware H0-R2 boundary into the firmware repository."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HW_SOURCE = ROOT.parent / "esp32-leshy2/hardware/architecture/h0-r2-rebaseline.json"
OUTPUT = ROOT / "config/h0_r2_hardware_contract.json"


def build() -> dict:
    raw = HW_SOURCE.read_bytes()
    hw = json.loads(raw)
    air = hw["airband_contract"]
    return {
        "schema_version": 1,
        "id": "FW-H0-R2",
        "hardware_source": "esp32-leshy2/hardware/architecture/h0-r2-rebaseline.json",
        "hardware_source_sha256": hashlib.sha256(raw).hexdigest(),
        "hardware_status": hw["status"],
        "firmware_marker": "F0-R2.3",
        "domains": [
            {"id": item["id"], "mpn": item["mpn"], "role": item["role"]}
            for item in hw["compute_domains"]
        ],
        "transports": hw["transport_contracts"],
        "s3_pin_map": hw["s3"]["pin_map"],
        "hub_gpio_budget": hw["hub_rp"]["gpio_budget"],
        "hub_pin_groups": hw["hub_rp"]["pin_groups"],
        "display": hw["display_contract"],
        "fpv": hw["video_contract"],
        "airband": {
            "owner": air["owner"],
            "signal_group": air["signal_group"],
            "user_range_mhz": air["user_range_mhz"],
            "lo_mhz": air["frequency_plan"]["lo_mhz"],
            "if_range_mhz": air["frequency_plan"]["if_range_mhz"],
            "image_range_mhz": air["frequency_plan"]["image_range_mhz"],
            "i2c": air["control"]["i2c"],
            "gp41": air["control"]["gp41"],
            "gp42": air["control"]["gp42"],
            "included": air["performance_boundary"]["included"],
            "excluded": air["performance_boundary"]["excluded"],
        },
        "power": hw["power_rebaseline"],
        "firmware_rebaseline": {
            "r1_status": "F0-F4 R1 artifacts remain regression evidence but no longer describe the physical topology.",
            "target_count": 6,
            "new_target": "hub_rp",
            "required_work": [
                "replace direct S3-C5 and S3-RF links with S3-Hub, Hub-C5 and Hub-RF transports",
                "route Pack status and Safety heartbeat/lease/fault mailboxes through the dedicated Hub GP43/44 I2C bus without weakening local watchdog or FAULT_KILL ownership",
                "move storage, audio and BROADCAST_RX ownership from S3 to Hub RP",
                "add fail-low Airband mode control, Si5351 setup, scan/record and ACARS receive pipeline",
                "preserve direct S3 UI/display/FPV scheduling and all existing safety/quiet-state semantics",
                "regenerate six-target build, memory, update, emulator/dev-board and HIL matrices before resuming F4",
            ],
        },
    }


def main() -> None:
    OUTPUT.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
