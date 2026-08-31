import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sync_h3_r2_transition_contract.py"


class H3R2TransitionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("sync_h3_r2_transition_contract", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.module)
        cls.contract = cls.module.build()

    def test_checked_in_import_is_current(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_fail_closed_runtime_boundary_is_exact(self):
        self.assertEqual(14, self.contract["evidence"]["passed_scenarios"])
        self.assertEqual(0, self.contract["evidence"]["failed_scenarios"])
        self.assertEqual(500, self.contract["timing_contract"]["qualified_kill_ms"])
        self.assertFalse(self.contract["claims"]["automatic_restart_allowed"])
        self.assertTrue(self.contract["claims"]["fresh_qualified_kill_to_run_required"])
        self.assertTrue(self.contract["claims"]["s3_fault_ui_reset_independent"])
        self.assertFalse(self.contract["claims"]["target_implementation_or_execution_proven"])
        self.assertFalse(self.contract["claims"]["order_authorized"])


if __name__ == "__main__":
    unittest.main()
