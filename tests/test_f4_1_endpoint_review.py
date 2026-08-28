import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import review_f4_1_endpoints as endpoint_review


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

    def test_r2_keeps_the_exact_historical_r1_hardware_digest(self):
        with mock.patch.object(
            endpoint_review, "current_baseline_is_r2", return_value=True
        ):
            expected = endpoint_review.expected_locked_inputs()
        self.assertEqual(
            endpoint_review.HISTORICAL_R1_HARDWARE_CONTRACT_SHA256,
            expected["hardware_contract_sha256"],
        )
        self.assertNotEqual(
            endpoint_review.sha256(endpoint_review.HARDWARE_CONTRACT_PATH),
            expected["hardware_contract_sha256"],
        )

    def test_r2_rejects_a_relabelled_historical_hardware_digest(self):
        review = json.loads(
            (REPO_ROOT / "config/f4_1_2_s3_c5_endpoint_review.json").read_text(
                encoding="utf-8"
            )
        )
        review["locked_inputs"]["hardware_contract_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            review_path = Path(directory) / "review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            with (
                mock.patch.object(endpoint_review, "REVIEW_PATH", review_path),
                mock.patch.object(
                    endpoint_review, "current_baseline_is_r2", return_value=True
                ),
            ):
                errors = endpoint_review.check_review()
        self.assertIn("F4.1.2 historical locked inputs changed", errors)


if __name__ == "__main__":
    unittest.main()
