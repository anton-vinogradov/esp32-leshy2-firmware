import importlib.util
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


if __name__ == "__main__":
    unittest.main()
