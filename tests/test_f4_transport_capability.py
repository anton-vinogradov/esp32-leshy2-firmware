import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class F4TransportCapabilityTests(unittest.TestCase):
    def test_review_is_current_and_fail_closed(self):
        subprocess.run(
            [sys.executable, "tools/check_f4_transport_capability.py"],
            cwd=REPO_ROOT,
            check=True,
        )
        matrix = json.loads(
            (REPO_ROOT / "config/f4_0_transport_capability_matrix.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("reviewed", matrix["status"])
        self.assertEqual("F4.0.1", matrix["next"])
        self.assertEqual(4, matrix["counts"]["production_transports"])
        self.assertEqual(8, matrix["counts"]["exact_sdk_endpoint_bindings"])
        self.assertEqual(0, matrix["counts"]["qemu_phy_paths"])
        self.assertEqual(0, matrix["counts"]["physical_transport_runs"])
        self.assertTrue(all(row["sdk_path_complete"] for row in matrix["transports"]))
        self.assertTrue(all(not row["qemu_phy_execution"] for row in matrix["transports"]))
        self.assertTrue(all(value is False for value in matrix["authorization"].values()))


if __name__ == "__main__":
    unittest.main()
