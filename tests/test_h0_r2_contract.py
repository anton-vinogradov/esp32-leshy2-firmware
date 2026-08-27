import importlib.util
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

    def test_six_targets_and_hub_owner_are_explicit(self):
        self.assertEqual(6, len(self.actual["domains"]))
        self.assertEqual("hub_rp", self.actual["firmware_rebaseline"]["new_target"])
        self.assertEqual("hub_rp", self.actual["airband"]["owner"])
        self.assertEqual(6, self.actual["firmware_rebaseline"]["target_count"])

    def test_airband_is_receive_only_and_fail_low(self):
        air = self.actual["airband"]
        self.assertEqual([118.0, 137.0], air["user_range_mhz"])
        self.assertEqual([6.0, 25.0], air["if_range_mhz"])
        self.assertIn("pulled low", air["gp41"])
        self.assertTrue(any("transmit" in item.lower() for item in air["excluded"]))

    def test_pack_and_safety_have_a_real_hub_transport(self):
        transports = {row["id"]: row for row in self.actual["transports"]}
        self.assertIn("HUB_PACK_SAFETY", transports)
        self.assertEqual(400_000, transports["HUB_PACK_SAFETY"]["clock_hz"])
        groups = {tuple(row["gpios"]): row["role"] for row in self.actual["hub_pin_groups"]}
        self.assertIn("Pack and Safety", groups[(43, 44)])
        self.assertEqual(3, self.actual["hub_gpio_budget"]["free"])

    def test_direct_ui_and_display_contract_survives_rebaseline(self):
        self.assertEqual(40_000_000, self.actual["display"]["selected_clock_hz"])
        s3_nets = {row["net"] for row in self.actual["s3_pin_map"]}
        self.assertTrue({"LCD_QSPI_SCK", "LCD_QSPI_D0", "LCD_QSPI_D1_DC", "LCD_QSPI_D2", "LCD_QSPI_D3"}.issubset(s3_nets))

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


if __name__ == "__main__":
    unittest.main()
