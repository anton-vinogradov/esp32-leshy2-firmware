#!/usr/bin/env python3
"""Project the current native H2-R2 hardware boundary into firmware."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HW_REPO = ROOT.parent / "esp32-leshy2"
HW_ROOT = HW_REPO / "hardware" / "architecture"
HW_SOURCE = HW_ROOT / "h0-r2-rebaseline.json"
C5_MUX_SOURCE = HW_ROOT / "c5-sdio-service-mux-contract.json"
DUAL_RP_SOURCE = HW_ROOT / "h1-r2-dual-rp-pinout.json"
U219_SOURCE = HW_ROOT / "h1-r2-u219-cap.json"
PHYSICAL_H1_SOURCE = HW_REPO / "hardware/product-design/h1-r2-placement.json"
R2_AUTHORITY_SOURCE = HW_ROOT / "generated/H0-R2-authority-gate.json"
PACK_SAFETY_SOURCE = HW_ROOT / "pack-safety-i2c-boundary-contract.json"
NATIVE_INVENTORY_SOURCE = HW_REPO / "hardware/ecad/generated/H2-R2-native-inventory.json"
EXACT_LEDGER_SOURCE = HW_REPO / "hardware/ecad/generated/H2-R2-symbol-footprint-ledger.json"
NATIVE_KICAD_SOURCE = HW_REPO / "hardware/ecad/generated/H2-R2-native-kicad-projects.json"
H2_HWFW_SOURCE = HW_REPO / "hardware/ecad/generated/H2-R2-hwfw-contract.json"
H2_M1_SOURCE = HW_REPO / "hardware/ecad/generated/H2-R2-interboard-m1.json"
OUTPUT = ROOT / "config/h0_r2_hardware_contract.json"
BSP_OUTPUT = ROOT / "config/hardware_bsp_contract.json"
INTEGRATION_OUTPUT = ROOT / "config/hardware_integration_contract.json"
U219_POLICY_OUTPUT = ROOT / "config/u219_cap_policy.json"
PREORDER_SOURCE = HW_REPO / "hardware/verification/preorder-verification-contract.json"
PREORDER_OUTPUT = ROOT / "config/preorder_verification_contract.json"


def source_record(path: Path) -> dict:
    raw = path.read_bytes()
    return {
        "path": f"esp32-leshy2/{path.relative_to(HW_REPO)}",
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def project_rp_pin(pin: dict) -> dict:
    return {
        "gpio": pin["gpio"],
        "net": pin["net"],
        "peripheral": pin["controller"],
        "direction": pin["direction"],
        "endpoint": pin["endpoint"],
        "gate": pin["reset"],
    }


def project_c5_pin(signal: dict) -> dict:
    direction = "in" if signal["signal"] == "SDIO_CLK" else "io"
    return {
        "gpio": int(signal["gpio"].removeprefix("GPIO")),
        "net": signal["signal"],
        "peripheral": "SDIO_SLAVE_FIXED_IOMUX",
        "direction": direction,
        "endpoint": f"module pad {signal['module_pad']}",
        "gate": (
            "GPIO13/14 common segment is hardware-switched between service USB and runtime SDIO"
            if signal["muxed_with_usb"]
            else "Hub remains reset/high-Z until always-on ownership establishes runtime SDIO"
        ),
    }


def build() -> dict:
    raw = HW_SOURCE.read_bytes()
    hw = json.loads(raw)
    c5_raw = C5_MUX_SOURCE.read_bytes()
    c5_mux = json.loads(c5_raw)
    rp_raw = DUAL_RP_SOURCE.read_bytes()
    dual_rp = json.loads(rp_raw)
    u219_raw = U219_SOURCE.read_bytes()
    u219 = json.loads(u219_raw)
    physical_h1_raw = PHYSICAL_H1_SOURCE.read_bytes()
    physical_h1 = json.loads(physical_h1_raw)
    r2_authority = json.loads(R2_AUTHORITY_SOURCE.read_bytes())
    pack_safety_raw = PACK_SAFETY_SOURCE.read_bytes()
    pack_safety = json.loads(pack_safety_raw)
    native_inventory_raw = NATIVE_INVENTORY_SOURCE.read_bytes()
    native_inventory = json.loads(native_inventory_raw)
    exact_ledger_raw = EXACT_LEDGER_SOURCE.read_bytes()
    exact_ledger = json.loads(exact_ledger_raw)
    native_kicad = json.loads(NATIVE_KICAD_SOURCE.read_bytes())
    h2_hwfw = json.loads(H2_HWFW_SOURCE.read_bytes())
    h2_m1 = json.loads(H2_M1_SOURCE.read_bytes())
    air = hw["airband_contract"]
    mux_route = c5_mux["production_mux_route"]
    mux_inventory = mux_route["live_inventory"]
    mux_route_closed = (
        mux_route["selection_status"] == "accepted"
        and all(
            mux_inventory.get(key) is not None
            for key in ("stock", "available_order_quantity", "moq", "price_tiers_usd")
        )
    )
    detector_latch = c5_mux["ownership"].get("detector_latch_implementation", {})
    detector_parts = [
        detector_latch.get("detector", {}),
        detector_latch.get("latch", {}),
        detector_latch.get("release_qualifier", {}),
    ]
    detector_latch_closed = (
        c5_mux["ownership"]["service_vbus"].get("detector_and_latch_mpn_status")
        == "accepted"
        and detector_latch.get("selection_status") == "accepted"
        and all(
            part.get("mpn")
            and part.get("jlcpcb_part_number")
            and all(
                part.get("live_inventory", {}).get(key) is not None
                for key in ("stock", "available_order_quantity", "moq", "price_tiers_usd")
            )
            for part in detector_parts
        )
    )
    pack_safety_closed = (
        pack_safety.get("marker") == "H2-R2.0.3"
        and pack_safety.get("status") == "reviewed_exact_factory_placeable_boundary"
        and pack_safety.get("buffer", {}).get("mpn") == "TCA9803DGKR"
        and pack_safety.get("buffer", {}).get("jlcpcb_part_number") == "C2687966"
        and pack_safety.get("bus", {}).get("hub_endpoints")
        == {"sda": "Hub RP GPIO42 / M1.32", "scl": "Hub RP GPIO43 / M1.33"}
        and pack_safety.get("bus", {}).get("hard_safety_dependency") is False
    )
    native_inventory_closed = (
        native_inventory.get("marker") == "H2-R2.1.1"
        and native_inventory.get("status") == "pass"
        and native_inventory.get("summary", {}).get("project_count") == 3
        and native_inventory.get("summary", {}).get("sheet_count") == 23
        and native_inventory.get("summary", {}).get("domain_count") == 6
        and native_inventory.get("summary", {}).get("component_group_count") == 242
        and native_inventory.get("summary", {}).get("component_quantity_per_product") == 1197
        and native_inventory.get("summary", {}).get("unresolved_pre_ecad_prerequisites") == 0
        and native_inventory.get("authorization", {}).get("native_source_and_sheet_inventory") is True
        and native_inventory.get("authorization", {}).get("schematic_symbols_or_nets") is False
        and native_inventory.get("errors") == []
    )
    if not native_inventory_closed:
        raise ValueError("H2-R2.1.1 native R2 inventory is not a closed, net-free input boundary")
    exact_ledger_closed = (
        exact_ledger.get("marker") == "H2-R2.1.2"
        and exact_ledger.get("status") == "pass"
        and exact_ledger.get("summary", {}).get("component_group_count") == 242
        and exact_ledger.get("summary", {}).get("board_component_group_count") == 237
        and exact_ledger.get("summary", {}).get("explicit_non_pcba_group_count") == 5
        and exact_ledger.get("summary", {}).get("logical_contact_count") == 1662
        and exact_ledger.get("summary", {}).get("unresolved_groups") == 0
        and exact_ledger.get("authorization", {}).get("exact_group_ledger") is True
        and exact_ledger.get("authorization", {}).get("symbol_or_footprint_files") is False
        and exact_ledger.get("authorization", {}).get("schematic_nets") is False
        and exact_ledger.get("errors") == []
    )
    if not exact_ledger_closed:
        raise ValueError("H2-R2.1.2 exact component ledger is not a closed, net-free input boundary")
    native_kicad_closed = (
        native_kicad.get("marker") == "H2-R2.1.3"
        and native_kicad.get("status") == "pass"
        and native_kicad.get("summary", {}).get("project_count") == 3
        and native_kicad.get("summary", {}).get("fitted_symbol_instance_count") == 1187
        and native_kicad.get("summary", {}).get("physical_symbol_pin_count") == 4327
        and native_kicad.get("summary", {}).get("canonical_net_count") == 826
        and native_kicad.get("authorization", {}).get("native_schematic_symbols_and_nets") is True
        and native_kicad.get("authorization", {}).get("pcb_placement_or_routing") is False
        and native_kicad.get("errors") == []
    )
    if not native_kicad_closed:
        raise ValueError("H2-R2.1.3 native KiCad result is not a clean schematic boundary")
    h2_hwfw_closed = (
        h2_hwfw.get("stage") == "H2-R2.1.4"
        and h2_hwfw.get("status") == "pass"
        and h2_hwfw.get("summary", {}).get("domain_count") == 6
        and h2_hwfw.get("summary", {}).get("controller_pin_rows") == 173
        and h2_hwfw.get("summary", {}).get("cross_project_net_count") == 50
        and h2_hwfw.get("summary", {}).get("cross_sheet_net_count") == 234
        and h2_hwfw.get("authorization", {}).get("hardware_firmware_machine_authority") is True
        and h2_hwfw.get("errors") == []
        and h2_m1.get("summary", {}).get("physical_contacts") == 80
        and h2_m1.get("summary", {}).get("no_connect_reserve_contacts") == 11
        and h2_m1.get("errors") == []
        and r2_authority.get("status") == "pass_current_r2_h2_reconciled"
        and r2_authority.get("r2_h2_authoritative") is True
    )
    if not h2_hwfw_closed:
        raise ValueError("H2-R2.1.4 hardware/firmware reconciliation is not authoritative")
    review_time_pin_gates = dual_rp["authority_chain"]["remaining_h2_gates"]
    review_time_physical_gates = physical_h1["pre_r2_h2_gates"]
    current_pin_gates = [
        gate for gate in review_time_pin_gates
        if not (mux_route_closed and "FSUSB42MUX" in gate)
        and not (detector_latch_closed and "service-VBUS" in gate)
        and not (pack_safety_closed and "Pack/Safety" in gate)
    ]
    current_physical_gates = [
        gate for gate in review_time_physical_gates
        if not (mux_route_closed and "FSUSB42MUX" in gate)
        and not (detector_latch_closed and "service-VBUS" in gate)
        and not (pack_safety_closed and "Pack/Safety" in gate)
    ]
    resolved_post_h1_gates = []
    if mux_route_closed:
        resolved_post_h1_gates.append(
            "exact live onsemi FSUSB42MUX / JLCPCB C11355 Standard-PCBA route, MOQ and price"
        )
    if detector_latch_closed:
        resolved_post_h1_gates.append(
            "exact DMN2056U-7 / C332302 detector, SN74LVC1G74DCUR / C70285 latch "
            "and 74HC20PW,118 / C546719 release qualifier"
        )
    if pack_safety_closed:
        resolved_post_h1_gates.append(
            "exact TCA9803DGKR / C2687966 powered-off Pack/Safety I2C boundary"
        )
    transports = []
    for transport in hw["transport_contracts"]:
        row = dict(transport)
        if row["id"] == "HUB_C5":
            performance = c5_mux["performance"]
            row.update(
                {
                    "transport": "native C5 4-bit SDIO through fail-safe service mux",
                    "clock_hz": performance["target_clock_hz"],
                    "bringup_clock_hz": performance["bringup_clock_hz"],
                    "raw_payload_mb_s": performance["target_raw_mb_s"],
                    "qualified_payload_floor_mb_s": performance[
                        "qualified_payload_floor_mb_s"
                    ],
                    "qualification_frequency_hz": performance[
                        "qualification_frequency_hz"
                    ],
                    "service_mux": (
                        "FSUSB42 reference switches C5 GPIO13/14 between data-only "
                        "service USB and runtime SDIO D3/D2; an always-on latch owns "
                        "reset, high-Z and break-before-make sequencing"
                    ),
                }
            )
        transports.append(row)
    return {
        "schema_version": 1,
        "id": "FW-H0-R2",
        "hardware_marker": dual_rp["marker"],
        "hardware_status": "reviewed_h2_r2_1_5_six_domain_hwfw_reconciled_not_layout_or_hil",
        "current_hardware_substep": "H2-R2.1.5",
        "hardware_sources": {
            "functional": source_record(HW_SOURCE),
            "c5_sdio_service_mux": source_record(C5_MUX_SOURCE),
            "dual_rp_pinout": source_record(DUAL_RP_SOURCE),
            "u219_cap_profile": source_record(U219_SOURCE),
            "physical_h1": source_record(PHYSICAL_H1_SOURCE),
            "r2_authority_gate": source_record(R2_AUTHORITY_SOURCE),
            "pack_safety_i2c_boundary": source_record(PACK_SAFETY_SOURCE),
            "native_r2_inventory": source_record(NATIVE_INVENTORY_SOURCE),
            "exact_component_ledger": source_record(EXACT_LEDGER_SOURCE),
            "native_kicad": source_record(NATIVE_KICAD_SOURCE),
            "h2_hwfw_reconciliation": source_record(H2_HWFW_SOURCE),
            "h2_interboard_m1": source_record(H2_M1_SOURCE),
        },
        "hardware_source": "esp32-leshy2/hardware/architecture/h0-r2-rebaseline.json",
        "hardware_source_sha256": hashlib.sha256(raw).hexdigest(),
        "firmware_marker": "F2-R2.0",
        "domains": [
            {
                "id": item["id"],
                "mpn": item["mpn"],
                "role": dual_rp[item["id"]]["role"]
                if item["id"] == "rf_rp"
                else item["role"],
            }
            for item in hw["compute_domains"]
        ],
        "domain_contracts": r2_authority["current_exact_domain_contracts"],
        "transports": transports,
        "s3_pin_map": hw["s3"]["pin_map"],
        "c5_sdio_pin_map": [
            project_c5_pin(signal) for signal in c5_mux["c5_module"]["signals"]
        ],
        "c5_sdio_service_mux": {
            "contract_id": c5_mux["contract_id"],
            "status": c5_mux["status"],
            "module": c5_mux["c5_module"]["mpn"],
            "mux_reference": c5_mux["mux"]["electrical_reference"],
            "production_route": c5_mux["production_mux_route"],
            "ownership": c5_mux["ownership"],
            "transition_sequences": c5_mux["transition_sequences"],
            "performance": c5_mux["performance"],
            "hil_gates": c5_mux["hil_gates"],
        },
        "pack_safety_i2c_boundary": pack_safety,
        "native_r2_inventory": {
            "marker": native_inventory["marker"],
            "status": native_inventory["status"],
            "projects": native_inventory["projects"],
            "summary": native_inventory["summary"],
            "historical_quarantine": native_inventory["historical_quarantine"],
            "authorization": native_inventory["authorization"],
        },
        "exact_component_ledger": {
            "marker": exact_ledger["marker"],
            "status": exact_ledger["status"],
            "summary": exact_ledger["summary"],
            "authorization": exact_ledger["authorization"],
        },
        "native_kicad": {
            "marker": native_kicad["marker"],
            "status": native_kicad["status"],
            "projects": native_kicad["projects"],
            "summary": native_kicad["summary"],
            "authorization": native_kicad["authorization"],
        },
        "h2_hwfw_reconciliation": {
            "stage": h2_hwfw["stage"],
            "status": h2_hwfw["status"],
            "summary": h2_hwfw["summary"],
            "source_sha256": source_record(H2_HWFW_SOURCE)["sha256"],
            "m1_source_sha256": source_record(H2_M1_SOURCE)["sha256"],
        },
        "hub_gpio_budget": dual_rp["hub_rp"]["gpio_budget"],
        "hub_pin_map": [project_rp_pin(pin) for pin in dual_rp["hub_rp"]["pin_map"]],
        "hub_resource_budget": {
            "pio": dual_rp["hub_rp"]["pio_budget"],
            "dma": dual_rp["hub_rp"]["dma_budget"],
        },
        "rear_gpio_budget": dual_rp["rf_rp"]["gpio_budget"],
        "rear_pin_map": [project_rp_pin(pin) for pin in dual_rp["rf_rp"]["pin_map"]],
        "rear_resource_budget": {
            "pio": dual_rp["rf_rp"]["pio_budget"],
            "dma": dual_rp["rf_rp"]["dma_budget"],
        },
        "hub_rf_m1_binding": dual_rp["m1_binding"],
        "s3_rom_uart_isolation": dual_rp["s3_rom_uart_isolation"],
        "pre_h2_gates": current_pin_gates,
        "review_time_pre_h2_gates": review_time_pin_gates,
        "resolved_post_h1_gates": resolved_post_h1_gates,
        "physical_h1": {
            "marker": physical_h1["marker"],
            "pin_authority_marker": physical_h1["pin_authority_marker"],
            "status": physical_h1["status"],
            "current_h1_blockers": physical_h1["current_h1_blockers"],
            "pre_r2_h2_gates": current_physical_gates,
            "review_time_pre_r2_h2_gates": review_time_physical_gates,
            "resolved_post_h1_gates": resolved_post_h1_gates,
        },
        "execution_gates": dual_rp["execution_gates"],
        "cap_profile": {
            "source_status": u219["status"],
            "slot_population": u219["accessories"]["slot_population"],
            "shared_i2c": u219["shared_i2c_contract"],
            "shared_irq": u219["shared_irq_contract"],
            "radio_policy": u219["radio_policy"],
            "acceptance_gates": u219["acceptance_gates"],
        },
        "interboard": hw["interboard_rebaseline"],
        "display": hw["display_contract"],
        "airband": {
            "owner": air["owner"],
            "signal_group": air["signal_group"],
            "user_range_mhz": air["user_range_mhz"],
            "lo_mhz": air["frequency_plan"]["lo_mhz"],
            "if_range_mhz": air["frequency_plan"]["if_range_mhz"],
            "image_range_mhz": air["frequency_plan"]["image_range_mhz"],
            "i2c": air["control"]["i2c"],
            "gp35": air["control"]["gp35"],
            "gp36": air["control"]["gp36"],
            "included": air["performance_boundary"]["included"],
            "excluded": air["performance_boundary"]["excluded"],
        },
        "power": hw["power_rebaseline"],
        "firmware_rebaseline": {
            "r1_status": "F0-F4 R1 artifacts, including F4.1.2 one-bit direct S3-C5 SDIO, remain regression evidence only and are not current R2 hardware authority.",
            "target_count": 6,
            "new_target": "hub_rp",
            "required_work": [
                "implement S3-Hub quad, Hub-C5 native 4-bit SDIO and Hub-RF SPI+alert; never reactivate the historical direct S3-C5 endpoint",
                "route Pack status and Safety heartbeat/lease/fault mailboxes through the dedicated Hub GPIO42/43 I2C1 bus and an exact powered-off-Ioff 3V3_MAIN/AON boundary without weakening local watchdog or FAULT_KILL ownership",
                "keep storage and three complete nRF24 paths on the front Hub RP while moving audio, BROADCAST_RX, CC1101, voice, M5 and exactly one signed U214/U219 Cap profile to the rear RF RP",
                "keep all display traffic front-local and preserve the eleven released S3 GPIOs plus M1 contacts 35-36 as true reserves",
                "add fail-low Airband mode control, Si5351 setup, scan/record and ACARS receive pipeline",
                "preserve direct S3 UI/display scheduling and all existing safety/quiet-state semantics",
                "qualify the six target builds before implementing R2 F4 transports, then run emulator/dev-board and HIL gates without reusing R1 physical claims",
            ],
        },
        "claims": {
            "exact_dual_rp_gpio_maps_imported": True,
            "c5_fixed_sdio_contacts_imported": True,
            "c5_service_mux_hardware_owned": True,
            "c5_production_mux_route_accepted": mux_route_closed,
            "c5_service_vbus_detector_latch_release_accepted": detector_latch_closed,
            "pack_safety_powered_off_boundary_accepted": pack_safety_closed,
            "native_r2_inventory_imported": native_inventory_closed,
            "exact_component_ledger_imported": exact_ledger_closed,
            "native_kicad_imported": native_kicad_closed,
            "h2_hwfw_reconciliation_imported": h2_hwfw_closed,
            "r1_f4_1_2_is_current_authority": False,
            "h2_closed": True,
            "kicad_authorized": True,
            "target_transport_implemented": False,
            "physical_or_hil_execution": False,
        },
    }


def render() -> str:
    return json.dumps(build(), ensure_ascii=False, indent=2) + "\n"


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def firmware_reconciliation(hardware_contract: dict) -> dict:
    """Return the exact firmware-side digest of the reviewed native H2 export."""
    return {
        "source_contract": "config/h0_r2_hardware_contract.json",
        "hardware_contract_sha256": canonical_sha256(hardware_contract),
        "hardware_marker": hardware_contract.get("hardware_marker"),
        "hardware_sources": hardware_contract.get("hardware_sources"),
        "domain_ids": ["s3", "c5", "rf_rp", "hub_rp", "pack", "safety"],
        "domain_contracts": hardware_contract.get("domain_contracts"),
        "rp_domains": ["rf_rp", "hub_rp"],
        "hub_pin_map": hardware_contract.get("hub_pin_map"),
        "rear_pin_map": hardware_contract.get("rear_pin_map"),
        "c5_sdio_service_mux": hardware_contract.get("c5_sdio_service_mux"),
        "pack_safety_i2c_boundary": hardware_contract.get("pack_safety_i2c_boundary"),
        "native_r2_inventory": hardware_contract.get("native_r2_inventory"),
        "exact_component_ledger": hardware_contract.get("exact_component_ledger"),
        "native_kicad": hardware_contract.get("native_kicad"),
        "h2_hwfw_reconciliation": hardware_contract.get("h2_hwfw_reconciliation"),
        "interboard": {
            "connector": hardware_contract.get("interboard", {}).get("connector"),
            "current_budget": hardware_contract.get("interboard", {}).get("current_budget"),
            "pin_map": hardware_contract.get("interboard", {}).get("pin_map"),
        },
        "pre_h2_gates": [],
        "physical_h1": hardware_contract.get("physical_h1"),
    }


def current_integration_contract(hardware_contract: dict) -> dict:
    return {
        "schema_version": 3,
        "contract_id": "LESHY2-HWFW-R2",
        "status": "reviewed_native_h2_r2",
        "authority": {
            "baseline": "R2",
            "lifecycle": "current_native_six_domain_h2",
            "allowed_as_r2_authority": True,
            "source": "config/h0_r2_hardware_contract.json",
            "r2_sync_gate": "config/r2_h2_sync_gate.json",
        },
        "controllers": hardware_contract["domain_contracts"],
        "r2_reconciliation": firmware_reconciliation(hardware_contract),
    }


def current_bsp_contract(hardware_contract: dict, integration: dict) -> dict:
    return {
        "schema_version": 3,
        "stage": "H2-R2.1.5",
        "status": "reviewed_native_h2_r2",
        "export_id": "LESHY2-H2-R2-FIRMWARE-BSP",
        "authority": {
            "baseline": "R2",
            "lifecycle": "current_native_six_domain_h2",
            "allowed_as_r2_authority": True,
            "source": "config/h0_r2_hardware_contract.json",
            "r2_sync_gate": "config/r2_h2_sync_gate.json",
        },
        "bsp": {"domains": hardware_contract["domain_contracts"]},
        "r2_reconciliation": firmware_reconciliation(hardware_contract),
        "integration_contract": integration,
    }


def render_u219_policy(hardware_contract: dict) -> str:
    policy = json.loads(U219_POLICY_OUTPUT.read_text(encoding="utf-8"))
    imported = policy["imported_hardware_boundary"]
    source = hardware_contract["hardware_sources"]["u219_cap_profile"]
    imported["marker"] = hardware_contract["hardware_marker"]
    imported["u219_source"] = source["path"]
    imported["u219_source_sha256"] = source["sha256"]
    imported["cap_profile_sha256"] = canonical_sha256(hardware_contract["cap_profile"])
    return json.dumps(policy, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate or verify the hash-bound R2 hardware projection."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="update the checked-in projection")
    mode.add_argument("--check", action="store_true", help="verify without writing (default)")
    args = parser.parse_args(argv)

    hardware_contract = build()
    integration = current_integration_contract(hardware_contract)
    bsp = current_bsp_contract(hardware_contract, integration)
    outputs = {
        OUTPUT: json.dumps(hardware_contract, ensure_ascii=False, indent=2) + "\n",
        BSP_OUTPUT: json.dumps(bsp, ensure_ascii=False, indent=2) + "\n",
        INTEGRATION_OUTPUT: json.dumps(integration, ensure_ascii=False, indent=2) + "\n",
        U219_POLICY_OUTPUT: render_u219_policy(hardware_contract),
        PREORDER_OUTPUT: PREORDER_SOURCE.read_text(encoding="utf-8"),
    }
    if args.write:
        for path, expected in outputs.items():
            path.write_text(expected, encoding="utf-8")
            print(f"updated: {path.relative_to(ROOT)}")
        return 0

    stale = [
        path for path, expected in outputs.items()
        if not path.is_file() or path.read_text(encoding="utf-8") != expected
    ]
    if stale:
        for path in stale:
            print(f"stale: {path.relative_to(ROOT)}")
        return 1
    print("current: " + ", ".join(str(path.relative_to(ROOT)) for path in outputs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
