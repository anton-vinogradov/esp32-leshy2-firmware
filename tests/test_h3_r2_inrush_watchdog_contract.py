import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sync_h3_r2_inrush_watchdog_contract.py"


class H3R2InrushWatchdogContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("sync_h3_r2_inrush_watchdog_contract", SCRIPT)
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

    def test_watchdog_and_fault_display_contract_is_fail_closed(self):
        watchdog = self.contract["watchdog"]
        self.assertEqual(500, watchdog["service_period_ms"])
        self.assertEqual(1000, watchdog["s3_heartbeat_deadline_ms"])
        self.assertTrue(watchdog["wdo_is_output_duration_not_extra_detection_latency"])
        self.assertEqual(2, self.contract["fault_journal"]["slots"])
        self.assertIn("clear FAULT_KILL", self.contract["fault_display"]["screen_forbidden_actions"])
        self.assertEqual(0, self.contract["evidence"]["automatic_restarts"])
        self.assertFalse(self.contract["claims"]["order_authorized"])


if __name__ == "__main__":
    unittest.main()
