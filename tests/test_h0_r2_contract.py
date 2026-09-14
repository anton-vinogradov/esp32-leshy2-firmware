import importlib.util
import copy
import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sync_h0_r2_contract.py"
OUTPUT = ROOT / "config/h0_r2_hardware_contract.json"


def load_sync_module():
    spec = importlib.util.spec_from_file_location("sync_h0_r2_contract", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class H0R2FirmwareContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_sync_module()
        cls.actual = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_generated_contract_is_current(self):
        self.assertEqual(self.module.build(), self.actual)

    def test_sync_cli_is_fail_safe_and_rejects_unknown_modes(self):
        checked = subprocess.run(
            ["python3", str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, checked.returncode, checked.stdout)
        self.assertIn("current:", checked.stdout)
        unknown = subprocess.run(
            ["python3", str(SCRIPT), "--not-a-real-mode"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertNotEqual(0, unknown.returncode, unknown.stdout)

    def test_six_targets_and_hub_owner_are_explicit(self):
        self.assertEqual(6, len(self.actual["domains"]))
        self.assertEqual("hub_rp", self.actual["firmware_rebaseline"]["new_target"])
        self.assertEqual("rf_rp", self.actual["airband"]["owner"])
        self.assertEqual(6, self.actual["firmware_rebaseline"]["target_count"])

    def test_native_boundary_includes_both_rp2354_qspi_supplies(self):
        summary = self.actual["native_kicad"]["summary"]
        self.assertEqual(4321, summary["physical_symbol_pin_count"])
        self.assertEqual(4085, summary["connected_physical_pin_count"])
        self.assertEqual(236, summary["explicit_no_connect_physical_pin_count"])
        self.assertEqual(
            summary["physical_symbol_pin_count"],
            summary["connected_physical_pin_count"]
            + summary["explicit_no_connect_physical_pin_count"],
        )
        self.assertEqual(789, summary["canonical_net_count"])

    def test_airband_is_receive_only_and_fail_low(self):
        air = self.actual["airband"]
        self.assertEqual([118.0, 137.0], air["user_range_mhz"])
        self.assertEqual([6.0, 25.0], air["if_range_mhz"])
        self.assertIn("pulled low", air["gp35"])
        self.assertTrue(any("transmit" in item.lower() for item in air["excluded"]))

    def test_open_panel_te_has_no_hub_irq_assignment(self):
        hub = {row["gpio"]: row for row in self.actual["hub_pin_map"]}
        s3 = {row["gpio"]: row for row in self.actual["domain_contracts"][0]["pin_map"]}
        self.assertEqual(("HUB_RESERVE_45", "reserve"), (hub[45]["net"], hub[45]["direction"]))
        self.assertEqual("LCD_BL_PWM", hub[46]["net"])
        self.assertEqual("LCD_DC", s3[45]["net"])
        self.assertNotIn("LCD_TE", {row["net"] for row in hub.values()})
        self.assertIn("contact 39 is deliberately open", self.actual["display"]["interface"])
        self.assertIn("must not wait for a TE interrupt", self.actual["display"]["interface"])
        self.assertIn("No TE-synchronized or tear-free claim", self.actual["display"]["hil"])

    def test_pack_and_safety_have_a_real_hub_transport(self):
        transports = {row["id"]: row for row in self.actual["transports"]}
        self.assertIn("HUB_PACK_SAFETY", transports)
        self.assertEqual(400_000, transports["HUB_PACK_SAFETY"]["clock_hz"])
        hub = {row["gpio"]: row for row in self.actual["hub_pin_map"]}
        self.assertEqual("HUB_SAFE_I2C_SDA", hub[42]["net"])
        self.assertEqual("HUB_SAFE_I2C_SCL", hub[43]["net"])
        self.assertEqual("SD_DETECT_N", hub[44]["net"])
        self.assertEqual(2, self.actual["hub_gpio_budget"]["reserve"])
        rear_reserve = {
            row["gpio"]
            for row in self.actual["rear_pin_map"]
            if row["direction"] == "reserve"
        }
        self.assertEqual(self.actual["rear_gpio_budget"]["reserve"], len(rear_reserve))
        self.assertEqual(
            set(self.actual["rear_gpio_budget"]["reserve_gpios"]), rear_reserve
        )
        self.assertEqual({32, 33, 34, 37, 38}, rear_reserve)

    def test_s3_rom_uart_and_hub_have_separate_exact_pins(self):
        pins = {row["gpio"]: row for row in self.actual["s3_pin_map"]}
        for gpio, expected in {
            7: ("S3_HUB_D2", "SPI3", "io"), 8: ("S3_HUB_D3", "SPI3", "io"),
            43: ("S3_UART_SERVICE_TX", "UART0_TX", "out"),
            44: ("S3_UART_SERVICE_RX", "UART0_RX", "in"),
        }.items():
            self.assertEqual(expected, tuple(pins[gpio][key] for key in ("net", "peripheral", "direction")))
        self.assertNotIn("s3_rom_uart_isolation", self.actual)
        routing = self.actual["s3_rom_uart_routing"]
        self.assertEqual("dedicated_gpio", routing["mode"])
        self.assertEqual({"tx": 43, "rx": 44}, routing["uart0_gpio"])
        self.assertEqual({"S3_HUB_D2": 7, "S3_HUB_D3": 8}, routing["hub_data_gpio"])
        self.assertIs(False, routing["uart0_shared_with_hub"])
        self.assertTrue(all(value is False for value in routing["qualification"].values()))

    def test_locality_first_repartition_is_explicit(self):
        domains = {row["id"]: row["role"] for row in self.actual["domains"]}
        self.assertIn("three fully concurrent local nRF24", domains["hub_rp"])
        self.assertIn("CC1101", domains["rf_rp"])
        self.assertNotIn("video", self.actual["interboard"])
        self.assertEqual(9, len(self.actual["interboard"]["released_legacy_nets"]))
        self.assertEqual(9, self.actual["interboard"]["current_budget"]["no_connect_reserve"])
        self.assertEqual(80, len(self.actual["interboard"]["pin_map"]))
        self.assertIn("nine true NC reserve contacts", self.actual["interboard"]["result"])

    def test_current_sources_are_hash_bound_and_pre_h2(self):
        self.assertEqual("H1-R2.31", self.actual["hardware_marker"])
        self.assertEqual("H1-R2.39", self.actual["physical_h1"]["marker"])
        self.assertEqual(
            self.actual["hardware_marker"],
            self.actual["physical_h1"]["pin_authority_marker"],
        )
        for source in self.actual["hardware_sources"].values():
            path = ROOT.parent / source["path"]
            self.assertTrue(path.is_file(), source["path"])
            self.assertEqual(source["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(48, len(self.actual["hub_pin_map"]))
        self.assertEqual(48, len(self.actual["rear_pin_map"]))
        self.assertTrue(self.actual["claims"]["h2_closed"])
        self.assertTrue(self.actual["claims"]["kicad_authorized"])
        self.assertFalse(self.actual["claims"]["physical_or_hil_execution"])
        self.assertEqual("H2-R2.1.5", self.actual["current_hardware_substep"])
        inventory = self.actual["native_r2_inventory"]
        self.assertEqual("H2-R2.1.1", inventory["marker"])
        self.assertEqual(2, inventory["summary"]["project_count"])
        self.assertEqual(22, inventory["summary"]["sheet_count"])
        self.assertEqual(252, inventory["summary"]["component_group_count"])
        self.assertEqual(0, inventory["summary"]["native_schematic_nets_created"])
        self.assertFalse(inventory["authorization"]["schematic_symbols_or_nets"])
        self.assertTrue(self.actual["claims"]["native_r2_inventory_imported"])
        ledger = self.actual["exact_component_ledger"]
        self.assertEqual("H2-R2.1.2", ledger["marker"])
        self.assertEqual(246, ledger["summary"]["board_component_group_count"])
        self.assertEqual(6, ledger["summary"]["explicit_non_pcba_group_count"])
        self.assertEqual(1615, ledger["summary"]["logical_contact_count"])
        self.assertEqual(0, ledger["summary"]["unresolved_groups"])
        self.assertFalse(ledger["authorization"]["symbol_or_footprint_files"])
        self.assertFalse(ledger["authorization"]["schematic_nets"])
        self.assertTrue(self.actual["claims"]["exact_component_ledger_imported"])
        self.assertTrue(self.actual["claims"]["native_kicad_imported"])
        self.assertTrue(self.actual["claims"]["h2_hwfw_reconciliation_imported"])
        self.assertEqual(1210, self.actual["native_kicad"]["summary"]["fitted_symbol_instance_count"])
        self.assertEqual(789, self.actual["native_kicad"]["summary"]["canonical_net_count"])
        self.assertEqual(173, self.actual["h2_hwfw_reconciliation"]["summary"]["controller_pin_rows"])
        self.assertEqual(0, self.actual["h2_hwfw_reconciliation"]["summary"]["errors"])
        self.assertEqual(
            self.module.build()["physical_h1"]["pre_r2_h2_gates"],
            self.actual["physical_h1"]["pre_r2_h2_gates"],
        )
        self.assertEqual([], self.actual["physical_h1"]["pre_r2_h2_gates"])

    def test_usb_unification_is_preserved_after_c5_source_correction(self):
        source = self.module.HW_REPO / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
        rows = json.loads(source.read_text())["rows"]
        ports = [row for row in rows if row["device_id"] == "gct_usb4105_gf_a"]
        self.assertEqual(
            {("LESHY2-UI-R2", "J9"), ("LESHY2-UI-R2", "J11"),
             ("LESHY2-RF-R2", "J1"), ("LESHY2-RF-R2", "J4")},
            {(row["project"], row["reference"]) for row in ports},
        )
        self.assertEqual(4, len(ports))
        self.assertFalse(any(row["device_id"] == "jae_dx07s016ja1r1500" for row in rows))
        self.assertEqual(1210, len(rows))
        self.assertEqual(246, len({row["device_id"] for row in rows}))
        # Four unchanged GCT instances; TS10/NX6 unique definitions are added
        # independently of the second NAND14 + bypass2 fitted-pin increment.
        self.assertEqual(1616 - 17 + 10 + 6, self.actual["exact_component_ledger"]["summary"]["logical_contact_count"])
        self.assertEqual(4305 + 14 + 2, self.actual["native_kicad"]["summary"]["physical_symbol_pin_count"])
        self.assertEqual(4085, self.actual["native_kicad"]["summary"]["connected_physical_pin_count"])
        self.assertEqual(173, self.actual["h2_hwfw_reconciliation"]["summary"]["controller_pin_rows"])

    def test_c5_transport_is_quad_and_40mhz_qualification_only(self):
        transport = {row["id"]: row for row in self.actual["transports"]}["HUB_C5"]
        self.assertEqual(20_000_000, transport["bringup_clock_hz"])
        self.assertEqual(40_000_000, transport["clock_hz"])
        self.assertEqual(40_000_000, transport["qualification_frequency_hz"])
        self.assertEqual(7.5, transport["qualified_payload_floor_mb_s"])
        self.assertEqual(6, len(self.actual["c5_sdio_pin_map"]))
        self.assertEqual(
            {"SDIO_DAT0", "SDIO_DAT1", "SDIO_DAT2_USB_DP", "SDIO_DAT3_USB_DM", "SDIO_CLK", "SDIO_CMD"},
            {row["net"] for row in self.actual["c5_sdio_pin_map"]},
        )
        ownership = self.actual["c5_sdio_service_mux"]["ownership"]
        self.assertTrue(ownership["latch"]["firmware_cannot_override"])
        self.assertEqual(
            "accepted",
            ownership["detector_latch_implementation"]["selection_status"],
        )
        self.assertTrue(
            self.actual["claims"]["c5_service_vbus_detector_latch_release_accepted"]
        )
        self.assertIn(
            "SN74LVC1G74DCUR",
            " ".join(self.actual["resolved_post_h1_gates"]),
        )
        self.assertNotIn("service-VBUS", " ".join(self.actual["pre_h2_gates"]))
        self.assertEqual([], self.actual["pre_h2_gates"])
        self.assertFalse(self.actual["claims"]["r1_f4_1_2_is_current_authority"])
        c5 = self.actual["c5_sdio_service_mux"]
        self.assertEqual([], self.module.c5_boundary_errors(c5))
        self.assertFalse(any(c5["qualification"].values()))
        self.assertFalse(self.actual["claims"]["c5_firmware_service_manager_implemented"])
        self.assertFalse(self.actual["claims"]["c5_switching_or_recovery_qualified"])
        route = ownership["detector_latch_implementation"]["release_qualifier"]["live_inventory"]
        self.assertEqual((0, None, 21, []), tuple(route[k] for k in
                         ("stock", "available_order_quantity", "moq", "price_tiers_usd")))
        self.assertTrue(route["price_is_estimate"])

    def test_pack_safety_boundary_is_exact_and_not_hard_kill(self):
        boundary = self.actual["pack_safety_i2c_boundary"]
        self.assertEqual("H2-R2.0.3", boundary["marker"])
        self.assertEqual("TCA9803DGKR", boundary["buffer"]["mpn"])
        self.assertEqual("C2687966", boundary["buffer"]["jlcpcb_part_number"])
        self.assertEqual(
            {"sda": "Hub RP GPIO42 / M1.32", "scl": "Hub RP GPIO43 / M1.33"},
            boundary["bus"]["hub_endpoints"],
        )
        self.assertFalse(boundary["bus"]["hard_safety_dependency"])
        self.assertTrue(
            self.actual["claims"]["pack_safety_powered_off_boundary_accepted"]
        )

    def test_all_six_domains_have_exact_hardware_pin_maps(self):
        contracts = self.actual["domain_contracts"]
        self.assertEqual(
            ["s3", "c5", "rf_rp", "hub_rp", "pack", "safety"],
            [row["id"] for row in contracts],
        )
        self.assertTrue(all(row.get("pin_map") for row in contracts))
        c5 = {row["contact"]: row for row in contracts[1]["pin_map"]}
        self.assertEqual("IR_RX_DEMOD", c5["GPIO0"]["net"])
        self.assertEqual("C5_SDIO_D3_USB_DM", c5["GPIO13"]["net"])
        self.assertTrue(c5["GPIO13"]["muxed_with_usb"])
        self.assertEqual(13, len(contracts[4]["pin_map"]))
        self.assertEqual(17, len(contracts[5]["pin_map"]))

    def test_dual_rp_exact_m1_binding_is_consistent(self):
        hub = {row["gpio"]: row for row in self.actual["hub_pin_map"]}
        rear = {row["gpio"]: row for row in self.actual["rear_pin_map"]}
        self.assertEqual(5, len(self.actual["hub_rf_m1_binding"]))
        for binding in self.actual["hub_rf_m1_binding"]:
            self.assertEqual(binding["net"], hub[binding["hub_gpio"]]["net"])
            self.assertEqual(binding["net"], rear[binding["rf_gpio"]]["net"])

    def test_direct_ui_and_display_contract_survives_rebaseline(self):
        self.assertEqual(20_000_000, self.actual["display"]["selected_clock_hz"])
        self.assertEqual(
            20_000_000,
            self.actual["display"]["idf_clock_contract"]["actual_clock_hz"],
        )
        s3_nets = {row["net"] for row in self.actual["s3_pin_map"]}
        self.assertTrue({"LCD_WR_N", "LCD_DC", *(f"LCD_DB{i}" for i in range(8))}.issubset(s3_nets))
        self.assertIn("ordinary serial SPI, not QSPI", self.actual["display"]["fallback"])

    def test_six_target_identity_contract_passes(self):
        result = subprocess.run(
            ["python3", "tools/check_f0_r2_target_identities.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("6 application images", result.stdout)

    def test_six_target_memory_rollback_contract_passes(self):
        result = subprocess.run(
            ["python3", "tools/check_f0_r2_memory_rollback.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("6 independent dual-slot domains", result.stdout)

    def test_six_target_update_policy_passes(self):
        result = subprocess.run(
            ["python3", "tools/check_f0_r2_update_policy.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("6 staged/pending/commit targets", result.stdout)

    def test_six_target_execution_gate_matrix_passes(self):
        result = subprocess.run(
            ["python3", "tools/check_f0_r2_execution_gates.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("1 exact emulator", result.stdout)
        self.assertIn("2 explicit surrogates", result.stdout)

    def test_integrated_f0_r2_closure_passes(self):
        result = subprocess.run(
            ["python3", "tools/review_f0_r2.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("F0-R2 closure review OK", result.stdout)


class C5SourceProjectionTests(unittest.TestCase):
    """Pure source fixtures: these do not rewrite/wait for generated imports."""

    @classmethod
    def setUpClass(cls):
        cls.module = load_sync_module()
        cls.source = json.loads(cls.module.C5_MUX_SOURCE.read_text())
        cls.inventory = {"component_groups": [
            {"device_id": "ti_ts3usb221erser", "mpn": "TS3USB221ERSER", "quantity_per_product": 1},
            {"device_id": "ti_sn74lv20apwr", "mpn": "SN74LV20APWR", "quantity_per_product": 2},
            {"device_id": "nexperia_nx3008nbks_115", "mpn": "NX3008NBKS,115", "quantity_per_product": 3},
        ]}

    def test_current_projection_preserves_qualification_and_inputs(self):
        before = copy.deepcopy((self.source, self.inventory))
        result = self.module.c5_projection(self.source, self.inventory)
        self.assertEqual([], self.module.c5_boundary_errors(result))
        self.assertEqual(self.source["qualification"], result["qualification"])
        self.assertEqual(before, (self.source, self.inventory))

    def test_source_identity_quantity_and_duplicate_are_rejected(self):
        for mutate in (
            lambda x: x["component_groups"].pop(),
            lambda x: x["component_groups"].append(x["component_groups"][0]),
            lambda x: x["component_groups"][0].update(mpn="FSUSB42MUX"),
            lambda x: x["component_groups"][1].update(quantity_per_product=1),
        ):
            inventory = copy.deepcopy(self.inventory)
            mutate(inventory)
            with self.assertRaises(ValueError):
                self.module.c5_projection(self.source, inventory)

    def test_preorder_is_explicit_not_zero_stock_inferred_availability(self):
        part = self.source["ownership"]["detector_latch_implementation"]["release_qualifier"]
        inventory = part["live_inventory"]
        self.assertTrue(self.module.documented_pcba_route(part, inventory))
        for key in ("explicit_preorder_offered", "preorder_estimate", "moq", "checked_at"):
            broken = copy.deepcopy(inventory)
            broken.pop(key)
            self.assertFalse(self.module.documented_pcba_route(part, broken), key)
        broken = copy.deepcopy(inventory)
        broken["price_is_estimate"] = False
        self.assertFalse(self.module.documented_pcba_route(part, broken))

    def test_stocked_route_needs_actual_order_quantity_and_price(self):
        route = self.source["production_mux_route"]
        self.assertTrue(self.module.documented_pcba_route(route["candidate"], route["live_inventory"]))
        for field, value in (("available_order_quantity", None), ("stock", 0),
                             ("moq", 0), ("price_tiers_usd", [])):
            broken = copy.deepcopy(route["live_inventory"])
            broken[field] = value
            self.assertFalse(self.module.documented_pcba_route(route["candidate"], broken))


if __name__ == "__main__":
    unittest.main()
