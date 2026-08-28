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


if __name__ == "__main__":
    unittest.main()
