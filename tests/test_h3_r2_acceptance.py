import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sync_h3_r2_acceptance.py"


class H3R2AcceptanceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("sync_h3_r2_acceptance", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.module)
        cls.contract = cls.module.build()

    def test_checked_in_import_is_current(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_reviewed_boundary_and_residuals_are_exact(self):
        boundary = self.contract["reviewed_boundary"]
        self.assertEqual(20, boundary["current_artifacts"])
        self.assertGreater(boundary["recorded_source_hashes_checked"], 50)
        self.assertEqual(0, boundary["hash_mismatches"])
        self.assertEqual(51, boundary["physical_residuals"])
        self.assertEqual("H4-R2.2", self.contract["current_hardware_substep"])

    def test_firmware_obligation_remains_open(self):
        self.assertEqual("F5/F6", self.contract["firmware_obligations"][0]["owner"])
        self.assertFalse(self.contract["claims"]["h4_r2_join_complete"])
        self.assertFalse(self.contract["claims"]["i8080_target_implementation_proven"])
        self.assertFalse(self.contract["claims"]["physical_residuals_complete"])


if __name__ == "__main__":
    unittest.main()
