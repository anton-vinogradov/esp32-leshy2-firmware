import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sync_h4_r2_contract_reconciliation.py"


class H4R2ContractReconciliationImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("sync_h4_r2_contract_reconciliation", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.module)
        cls.contract = cls.module.build()

    def test_checked_in_import_is_current(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_exact_gap_and_owners_are_imported(self):
        reviewed = self.contract["reviewed_boundary"]
        self.assertEqual((173, 135, 38), (reviewed["hardware_pin_rows"], reviewed["generated_bsp_pin_rows"], reviewed["missing_generated_bsp_rows"]))
        self.assertEqual(["c5", "pack", "safety"], reviewed["correction_domains"])
        self.assertEqual(0, reviewed["unowned_contradictions"])

    def test_import_does_not_claim_completion_or_release(self):
        claims = self.contract["claims"]
        self.assertTrue(claims["hardware_firmware_contract_reconciliation_reviewed"])
        self.assertFalse(claims["generated_bsp_complete"])
        self.assertFalse(claims["joined_h4_complete"])
        self.assertFalse(claims["purchase_layout_or_fabrication_authorized"])
        self.assertEqual("H4-R2.2", self.contract["next"]["marker"])


if __name__ == "__main__":
    unittest.main()
