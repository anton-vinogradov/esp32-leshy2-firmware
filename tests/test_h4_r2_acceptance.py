import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sync_h4_r2_acceptance.py"


class H4R2AcceptanceImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("sync_h4_r2_acceptance", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.module)
        cls.contract = cls.module.build()

    def test_checked_in_import_is_current(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_global_result_is_imported(self):
        reviewed = self.contract["reviewed_result"]
        self.assertEqual((24, 6, 173, 173, 80, 12), (reviewed["joined_inputs"], reviewed["compute_domains"], reviewed["h2_controller_rows"], reviewed["generated_bsp_rows"], reviewed["m1_contacts"], reviewed["qualified_target_configurations"]))
        self.assertEqual(0, reviewed["cross_domain_contradictions_remaining"])
        self.assertEqual(51, reviewed["physical_residuals_transferred"])

    def test_import_advances_hardware_only_and_keeps_release_closed(self):
        self.assertEqual(("H5", "H5.0.3-R1"), (self.contract["current_hardware_stage"], self.contract["current_hardware_substep"]))
        claims = self.contract["claims"]
        self.assertTrue(claims["joined_prelayout_gate_reviewed"])
        self.assertFalse(claims["runtime_boot_proven"])
        self.assertFalse(claims["purchase_layout_or_fabrication_authorized"])


if __name__ == "__main__":
    unittest.main()
