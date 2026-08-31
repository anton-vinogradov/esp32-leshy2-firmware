import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sync_h3_r2_thermal_fault.py"


class H3R2ThermalFaultContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("sync_h3_r2_thermal_fault", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.module)
        cls.contract = cls.module.build()

    def test_checked_in_import_is_current(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_thermal_fault_and_proof_contracts_are_exact(self):
        thermal = self.contract["thermal_contract"]
        self.assertEqual((65, 75, 60), (thermal["warning_c"], thermal["fault_kill_c"], thermal["rearm_below_c"]))
        self.assertEqual(30, len(self.contract["fault_contract"]["faults"]))
        self.assertEqual(1760, self.contract["fault_contract"]["maximum_analytical_detection_ms"])
        self.assertEqual("EVERY_48_H", self.contract["extended_operation_contract"]["full_fault_plane_proof"]["default"])
        self.assertFalse(self.contract["claims"]["runtime_safety_policy_implemented"])


if __name__ == "__main__":
    unittest.main()
