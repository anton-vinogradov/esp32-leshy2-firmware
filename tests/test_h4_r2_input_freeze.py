import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sync_h4_r2_input_freeze.py"


class H4R2InputFreezeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("sync_h4_r2_input_freeze", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.module)
        cls.contract = cls.module.build()

    def test_checked_in_import_is_current(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_freeze_counts_and_next_boundary_are_exact(self):
        frozen = self.contract["frozen_boundary"]
        self.assertEqual((10, 14, 24), (frozen["hardware_inputs"], frozen["firmware_inputs"], frozen["total_inputs"]))
        self.assertEqual(0, frozen["cross_repository_h3_hash_mismatches"])
        self.assertEqual(51, frozen["physical_residuals_carried"])
        self.assertEqual("H4-R2.0.2", self.contract["next_contract"]["marker"])

    def test_freeze_does_not_claim_join_or_release(self):
        claims = self.contract["claims"]
        self.assertTrue(claims["joined_inputs_frozen"])
        self.assertFalse(claims["joined_contract_reconciliation_complete"])
        self.assertFalse(claims["physical_evidence_complete"])
        self.assertFalse(claims["purchase_layout_or_fabrication_authorized"])


if __name__ == "__main__":
    unittest.main()
