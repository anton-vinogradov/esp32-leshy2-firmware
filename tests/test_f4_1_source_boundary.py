import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class F41SourceBoundaryTests(unittest.TestCase):
    def test_exact_vendor_tree_and_source_boundary_are_reviewed(self):
        subprocess.run(
            [sys.executable, "tools/check_f4_1_source_boundary.py"],
            cwd=REPO_ROOT,
            check=True,
        )
        boundary = json.loads(
            (REPO_ROOT / "config/f4_1_s3_c5_source_boundary.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("reviewed", boundary["status"])
        self.assertEqual("1.1.2", boundary["vendor"]["version"])
        self.assertFalse(boundary["vendor"]["component_manager_enabled"])
        self.assertEqual(30, boundary["counts"]["vendored_files"])
        self.assertEqual(0, boundary["counts"]["target_adapter_builds"])
        self.assertEqual(0, boundary["counts"]["physical_transport_runs"])
        self.assertEqual("F4.1.1", boundary["next"])


if __name__ == "__main__":
    unittest.main()
