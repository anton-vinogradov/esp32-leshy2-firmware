import json
import shutil
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class HostCoreExecutionTests(unittest.TestCase):
    def test_environment_lock_is_complete_and_self_consistent(self):
        result = subprocess.run(
            ["python3", "tools/verify_environment_lock.py"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("environment lock OK: 26 archives", result.stdout)

    def test_portable_safety_core_executes_all_scenarios(self):
        self.assertIsNotNone(shutil.which("make"))
        self.assertIsNotNone(shutil.which("cc"))
        result = subprocess.run(
            ["make", "host-test"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("host safety core: 8 scenarios passed", result.stdout)
        self.assertIn("host L2IP core: 4 scenarios passed", result.stdout)
        self.assertIn("host update core: 5 scenarios passed", result.stdout)
        self.assertIn("host five-domain model: 7 scenarios passed", result.stdout)

    def test_preorder_contract_does_not_overstate_firmware_or_emulation(self):
        contract_path = REPO_ROOT / "config/preorder_verification_contract.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        self.assertEqual("LESHY2-PREORDER-1", contract["contract_id"])
        self.assertIn(
            "reviewed portable C safety, L2IP, update",
            contract["current_truth"]["executable_firmware"],
        )
        self.assertIn("not run", contract["current_truth"]["instruction_emulation"])
        gates = {gate["id"]: gate["status"] for gate in contract["gates"]}
        self.assertEqual(
            "reviewed",
            gates["P4_EXECUTABLE_FIRMWARE_MODEL"],
        )
        self.assertEqual("not_started", gates["P5_TARGET_BUILDS_EMULATION"])
        self.assertEqual("not_authorized", gates["P7_ENGINEERING_SAMPLE_ORDER"])

        hardware_copy = (
            REPO_ROOT.parent
            / "esp32-leshy2/hardware/verification/preorder-verification-contract.json"
        )
        if hardware_copy.is_file():
            self.assertEqual(
                contract_path.read_bytes(),
                hardware_copy.read_bytes(),
                "hardware and firmware pre-order gates diverged",
            )


if __name__ == "__main__":
    unittest.main()
