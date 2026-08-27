import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class F1R2PortableTests(unittest.TestCase):
    def test_rebaseline_plan_is_current_and_fail_closed(self):
        result = subprocess.run(
            ["python3", "tools/check_f1_r2_rebaseline.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("6 domains", result.stdout)
        self.assertIn("5 required deltas", result.stdout)
        plan = json.loads(
            (ROOT / "config/f1_r2_portable_rebaseline.json").read_text(encoding="utf-8")
        )
        self.assertEqual(4, len(plan["planned_substeps"]))
        self.assertIn("RF reception or transmission", plan["evidence_boundary"]["must_not_claim"])

    def test_six_domain_update_review_passes(self):
        result = subprocess.run(
            ["python3", "tools/review_f1_r2_six_domain_update.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("6 independent domains", result.stdout)
        self.assertIn("0 target/physical runs claimed", result.stdout)

    def test_receiver_review_passes_without_tx_claim(self):
        result = subprocess.run(
            ["python3", "tools/review_f1_r2_receiver.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("5 receive-only states", result.stdout)
        self.assertIn("0 target/RF runs claimed", result.stdout)

    def test_integrated_fault_review_passes_without_physical_claim(self):
        result = subprocess.run(
            ["python3", "tools/review_f1_r2_integrated_faults.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("34 scenarios", result.stdout)
        self.assertIn("0 target/physical runs claimed", result.stdout)

    def test_f1_r2_closure_review_passes(self):
        result = subprocess.run(
            ["python3", "tools/review_f1_r2.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("F1-R2 closure review OK", result.stdout)
        self.assertIn("68 normal+sanitizer executions", result.stdout)


if __name__ == "__main__":
    unittest.main()
