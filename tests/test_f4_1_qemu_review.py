import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class F41QemuReviewTests(unittest.TestCase):
    def test_exact_build_and_fake_sdio_qemu_review_is_current(self):
        subprocess.run(
            [sys.executable, "tools/review_f4_1_qemu.py", "--check"],
            cwd=REPO_ROOT,
            check=True,
        )
        review = json.loads(
            (REPO_ROOT / "config/f4_1_3_s3_c5_qemu_review.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("reviewed", review["status"])
        self.assertEqual(4, review["execution_counts"]["exact_target_adapter_builds"])
        self.assertEqual(2, review["execution_counts"]["s3_qemu_fake_runs"])
        self.assertEqual(0, review["execution_counts"]["physical_transport_runs"])
        self.assertEqual(6, len(review["scenarios"]))
        self.assertEqual({"debug", "release"}, {
            row["configuration"] for row in review["qemu_runs"]
        })


if __name__ == "__main__":
    unittest.main()
