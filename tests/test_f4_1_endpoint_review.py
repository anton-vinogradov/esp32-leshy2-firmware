import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class F41EndpointReviewTests(unittest.TestCase):
    def test_exact_s3_and_c5_endpoints_are_reviewed(self):
        subprocess.run(
            [sys.executable, "tools/review_f4_1_endpoints.py", "--check"],
            cwd=REPO_ROOT,
            check=True,
        )
        review = json.loads(
            (REPO_ROOT / "config/f4_1_2_s3_c5_endpoint_review.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("reviewed", review["status"])
        self.assertEqual(2, review["execution_counts"]["exact_target_adapter_builds"])
        self.assertEqual(0, review["execution_counts"]["s3_qemu_fake_runs"])
        self.assertEqual(0, review["execution_counts"]["physical_transport_runs"])
        self.assertEqual(1, review["endpoint_contract"]["s3_host"]["bus_width_bits"])
        self.assertEqual(8, review["endpoint_contract"]["c5_slave"]["dma_receive_cells"])
        self.assertIn(
            "SDIO_SLAVE_FLAG_DAT2_DISABLED",
            review["endpoint_contract"]["c5_slave"]["flags"],
        )


if __name__ == "__main__":
    unittest.main()
