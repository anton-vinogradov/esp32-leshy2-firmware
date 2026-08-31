import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sync_h4_r2_correction_closure.py"


class H4R2CorrectionClosureImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("sync_h4_r2_correction_closure", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.module)
        cls.contract = cls.module.build()

    def test_checked_in_import_is_current(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_complete_maps_and_target_builds_are_imported(self):
        boundary = self.contract["reviewed_boundary"]
        self.assertEqual((173, 173, 38, 0), (boundary["h2_controller_rows"], boundary["generated_bsp_rows"], boundary["restored_rows"], boundary["remaining_contradictions"]))
        self.assertEqual((12, 60, 16, 16), (boundary["qualified_configurations"], boundary["verified_artifacts"], boundary["verified_maps"], boundary["passed_size_gates"]))

    def test_import_keeps_runtime_and_release_claims_bounded(self):
        claims = self.contract["claims"]
        self.assertTrue(claims["all_six_generated_bsp_maps_exact"])
        self.assertFalse(claims["runtime_boot_proven"])
        self.assertFalse(claims["i8080_target_implementation_proven"])
        self.assertFalse(claims["purchase_layout_or_fabrication_authorized"])
        self.assertEqual("H4-R2.3", self.contract["next"]["marker"])


if __name__ == "__main__":
    unittest.main()
