import importlib.util
import copy
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sync_h3_r2_digital_interfaces.py"


class H3R2DigitalInterfaceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("sync_h3_r2_digital_interfaces", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.module)
        cls.contract = cls.module.build()

    def test_checked_in_import_is_current(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_exact_display_clock_and_m1_boundary_are_fail_closed(self):
        display = self.contract["display"]
        self.assertEqual(20_000_000, display["requested_clock_hz"])
        self.assertEqual(20_000_000, display["actual_clock_hz"])
        self.assertGreater(display["forbidden_request_actual_hz"], 25_000_000)
        self.assertEqual(9, len(self.contract["m1"]["true_nc_contacts"]))
        self.assertTrue(all(self.contract["usb_and_service_ownership"].values()))
        self.assertFalse(self.contract["claims"]["target_driver_implemented"])

    def test_c5_boot_topology_does_not_qualify_download_recovery(self):
        boot = self.contract["c5_boot_strap"]
        self.assertEqual("pass", boot["topology_status"])
        self.assertEqual({"GPIO27": 1, "GPIO28": 0}, boot["joint_download_boot_0_straps"])
        self.assertEqual(3, boot["hold_after_en_release_ms_min"])
        for field in ("sampled_levels_and_timing_qualified", "usb_mux_sel_oe_qualified",
                      "kill_recovery_policy_qualified", "end_to_end_download_qualified"):
            self.assertIs(False, boot[field])

    def test_c5_source_topology_and_typical_bandwidth_are_not_timing_authority(self):
        control = self.contract["c5_mux_control"]
        self.assertEqual("pass", control["source_topology_status"])
        self.assertTrue(control["checks"])
        for field in ("timing_qualified", "power_sequences_qualified",
                      "firmware_service_manager_implemented", "production_release_allowed"):
            self.assertIs(False, control[field])
        loading = self.contract["loading"]
        self.assertTrue(loading["models"]["hub_c5_sdio"]["bandwidth_is_typical_not_timing_proof"])
        self.assertIn("c5_mux_typical_bandwidth_screen_is_at_least_10x_bus_clock", loading["checks"])
        self.assertIn("service_switch_has_usb_full_speed_capability", self.contract["usb_and_service_ownership"])
        self.assertIn("power_off_port_leakage_limit_is_2ua", self.contract["usb_and_service_ownership"])
        self.assertIn("conditional, not measured", self.contract["runtime_invariants"]["c5_mux"])
        self.assertIs(False, self.contract["claims"]["target_execution_authorized"])


class C5DiagnosticSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("digital_c5_schema_fixture", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def fixture(self):
        return {
            "c5_mux_control": {"checks": {"pin:fixture": True}, "source_topology_status": "pass",
                "scope": "source topology only", "timing_qualified": False,
                "power_sequences_qualified": False, "firmware_service_manager_implemented": False,
                "production_release_allowed": False},
            "usb_and_service_ownership": {"service_switch_has_usb_full_speed_capability": True,
                                           "power_off_port_leakage_limit_is_2ua": True},
            "loading": {"checks": {"c5_mux_typical_bandwidth_screen_is_at_least_10x_bus_clock": True},
                "models": {"hub_c5_sdio": {"bandwidth_is_typical_not_timing_proof": True}}},
        }

    def test_pass_and_explicit_failed_diagnostics_can_be_retained(self):
        source = self.fixture()
        before = copy.deepcopy(source)
        self.module.validate_c5_diagnostics(source)
        self.assertEqual(before, source)
        source["c5_mux_control"]["checks"]["pin:fixture"] = False
        source["c5_mux_control"]["source_topology_status"] = "fail"
        source["usb_and_service_ownership"]["power_off_port_leakage_limit_is_2ua"] = False
        self.module.validate_c5_diagnostics(source)

    def test_missing_inconsistent_or_self_qualified_control_is_rejected(self):
        source = self.fixture()
        source.pop("c5_mux_control")
        with self.assertRaises(ValueError):
            self.module.validate_c5_diagnostics(source)
        for key in ("timing_qualified", "power_sequences_qualified",
                    "firmware_service_manager_implemented", "production_release_allowed"):
            for value in (True, None, 0):
                source = self.fixture()
                source["c5_mux_control"][key] = value
                with self.assertRaises(ValueError):
                    self.module.validate_c5_diagnostics(source)
        source = self.fixture()
        source["c5_mux_control"]["source_topology_status"] = "fail"
        with self.assertRaises(ValueError):
            self.module.validate_c5_diagnostics(source)

    def test_old_usb_keys_and_typical_as_guarantee_are_rejected(self):
        for group, key in (
            ("usb_and_service_ownership", "service_switch_has_usb_full_speed_capability"),
            ("usb_and_service_ownership", "power_off_port_leakage_limit_is_2ua"),
            ("loading", "c5_mux_typical_bandwidth_screen_is_at_least_10x_bus_clock"),
        ):
            source = self.fixture()
            values = source[group] if group != "loading" else source[group]["checks"]
            values.pop(key)
            with self.assertRaises(ValueError):
                self.module.validate_c5_diagnostics(source)
        source = self.fixture()
        source["loading"]["models"]["hub_c5_sdio"]["bandwidth_is_typical_not_timing_proof"] = False
        with self.assertRaises(ValueError):
            self.module.validate_c5_diagnostics(source)


if __name__ == "__main__":
    unittest.main()
