import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class F41CoreReviewTests(unittest.TestCase):
    def test_sanitized_review_is_current_and_honest(self):
        subprocess.run(
            [sys.executable, "tools/review_f4_1_core.py", "--check"],
            cwd=REPO_ROOT,
            check=True,
        )
        review = json.loads(
            (REPO_ROOT / "config/f4_1_1_high_speed_core_review.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("reviewed", review["status"])
        self.assertEqual(19, len(review["scenarios"]))
        self.assertEqual(["address", "undefined"], review["sanitizers"])
        self.assertEqual(19, review["execution_counts"]["host_sanitized_scenarios"])
        self.assertEqual(0, review["execution_counts"]["exact_target_adapter_builds"])
        self.assertEqual(0, review["execution_counts"]["physical_transport_runs"])
        self.assertIn("granted_total", review["review_finding"]["correction"])


if __name__ == "__main__":
    unittest.main()
