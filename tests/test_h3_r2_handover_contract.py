import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sync_h3_r2_handover_contract.py"


class H3R2HandoverContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("sync_h3_r2_handover_contract", SCRIPT)
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

    def test_runtime_contract_is_fail_closed(self):
        self.assertEqual(7316, self.contract["evidence"]["transition_cases"])
        self.assertEqual(0, self.contract["evidence"]["failed_cases"])
        self.assertFalse(self.contract["charger"]["otg_enabled"])
        self.assertFalse(self.contract["charger"]["backup_enabled"])
        self.assertTrue(self.contract["charger"]["masked_readback_required"])
        self.assertIn("AON diagnostics only", self.contract["runtime_contract"]["unqualified_5v"])
        self.assertFalse(self.contract["claims"]["physical_droop_or_handover_time_proven"])
        self.assertFalse(self.contract["claims"]["order_authorized"])


if __name__ == "__main__":
    unittest.main()
