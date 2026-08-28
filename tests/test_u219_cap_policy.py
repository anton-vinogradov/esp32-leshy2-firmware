import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "tools/check_u219_cap_policy.py"
SPEC = importlib.util.spec_from_file_location("check_u219_cap_policy", CHECKER_PATH)
CHECKER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECKER)


class U219CapPolicyBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads((ROOT / "config/u219_cap_policy.json").read_text())
        cls.hardware = json.loads((ROOT / "config/h0_r2_hardware_contract.json").read_text())

    def test_exact_projected_hardware_security_boundary_is_bound(self):
        self.assertEqual([], CHECKER.hardware_binding_errors(self.policy, self.hardware))

    def test_tx_permission_or_nfc_relaxation_breaks_the_binding(self):
        mutations = {
            "CC1101 TX": lambda hardware: hardware["cap_profile"]["radio_policy"]["cc1101"].update(
                hardware_tx_evidence="present; TX allowed", forbidden_commands=[]
            ),
            "NFC write": lambda hardware: hardware["cap_profile"]["radio_policy"]["nfc"].update(
                forbidden=[]
            ),
            "closed HIL": lambda hardware: hardware["cap_profile"]["acceptance_gates"][0].update(
                closed=True
            ),
            "source hash": lambda hardware: hardware["hardware_sources"]["u219_cap_profile"].update(
                sha256="0" * 64
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                hardware = copy.deepcopy(self.hardware)
                mutate(hardware)
                self.assertTrue(CHECKER.hardware_binding_errors(self.policy, hardware))


if __name__ == "__main__":
    unittest.main()
