import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class F2R2RebaselineTests(unittest.TestCase):
    def test_plan_is_current_and_fail_closed(self):
        result = subprocess.run(
            ["python3", "tools/check_f2_r2_rebaseline.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("5 historical targets -> 6 R2 targets", result.stdout)
        self.assertIn("0 R2 builds/runs claimed", result.stdout)

    def test_two_rp_projects_are_independent(self):
        plan = json.loads(
            (ROOT / "config/f2_r2_target_rebaseline.json").read_text(
                encoding="utf-8"
            )
        )
        projects = {row["id"]: row for row in plan["r2_target_plan"]}
        self.assertNotEqual(projects["rf_rp"]["project_dir"], projects["hub_rp"]["project_dir"])
        self.assertEqual("rp2350-arm-s", projects["rf_rp"]["sdk_target"])
        self.assertEqual("rp2350-arm-s", projects["hub_rp"]["sdk_target"])
        self.assertEqual("F2-R2.1", plan["next"])

    def test_six_target_build_matrix_is_exact_and_non_executed(self):
        result = subprocess.run(
            ["python3", "tools/check_f2_r2_build_matrix.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("6 targets x 2 configurations", result.stdout)
        self.assertIn("0 projects/builds/executions claimed", result.stdout)
        matrix = json.loads(
            (ROOT / "config/f2_r2_build_matrix.json").read_text(encoding="utf-8")
        )
        self.assertEqual(12, len(matrix["jobs"]))
        self.assertEqual(60, matrix["evidence"]["artifact_paths_per_complete_pass"])
        self.assertEqual(16, matrix["evidence"]["map_paths_per_complete_pass"])
        self.assertFalse(matrix["locked_environment"]["network_during_configure_or_build"])
        self.assertEqual("F2-R2.2", matrix["next"])

    def test_six_production_sdk_project_roots_are_independent_and_non_executed(self):
        result = subprocess.run(
            ["python3", "tools/check_f2_r2_target_projects.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("6 production-SDK roots", result.stdout)
        self.assertIn("2 independent RP trees", result.stdout)
        review = json.loads(
            (ROOT / "config/f2_r2_target_projects.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("F2-R2.2", review["stage"])
        self.assertEqual("reviewed_structure", review["status"])
        self.assertEqual(
            ["s3", "c5", "rf_rp", "hub_rp", "pack", "safety"],
            [row["id"] for row in review["projects"]],
        )
        self.assertFalse(review["claims"]["rf_and_hub_share_project_tree"])
        self.assertFalse(review["claims"]["rf_and_hub_share_entry_source"])
        self.assertFalse(review["claims"]["rf_and_hub_share_application_image"])
        self.assertFalse(review["claims"]["r2_bsp_generated"])
        self.assertFalse(review["claims"]["r2_build_run"])
        self.assertEqual("F2-R2.3", review["next"])


if __name__ == "__main__":
    unittest.main()
