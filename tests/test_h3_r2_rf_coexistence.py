import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sync_h3_r2_rf_coexistence.py"


class H3R2RfCoexistenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("sync_h3_r2_rf_coexistence", SCRIPT)
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

    def test_ports_cables_quiet_states_and_nrf_modes_are_exact(self):
        self.assertEqual(5, len(self.contract["port_topology"]["front"]))
        self.assertEqual(5, len(self.contract["port_topology"]["rear"]))
        self.assertEqual(5, len(self.contract["microcoax"]["paths"]))
        self.assertEqual(2, self.contract["microcoax"]["thirty_mm_paths"])
        self.assertEqual(3, self.contract["microcoax"]["sixty_mm_paths"])
        self.assertGreaterEqual(self.contract["microcoax"]["minimum_conservative_slack_mm"], 5.0)
        self.assertEqual(9, len(self.contract["quiet_matrix"]))
        self.assertEqual(4, len(self.contract["nrf_concurrency"]["role_modes"]))
        self.assertEqual(8, self.contract["nrf_concurrency"]["identity_permutations"])
        self.assertFalse(self.contract["claims"]["runtime_radio_arbiter_implemented"])


if __name__ == "__main__":
    unittest.main()
