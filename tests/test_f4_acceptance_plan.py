import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class F4AcceptancePlanTests(unittest.TestCase):
    def test_plan_and_snapshot_preserve_evidence_boundaries(self):
        for mode in ("--check-plan", "--check-snapshot"):
            subprocess.run(
                [sys.executable, "tools/run_f4_acceptance.py", mode],
                cwd=REPO_ROOT,
                check=True,
            )
        matrix = json.loads(
            (REPO_ROOT / "config/f4_0_2_acceptance_matrix.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(matrix["policy"]["evidence_class_substitution_allowed"])
        self.assertFalse(matrix["policy"]["qemu_fake_transport_may_claim_physical_execution"])
        self.assertEqual(4, len(matrix["transport_tracks"]))
        self.assertEqual(6, len(matrix["evidence_classes"]))
        self.assertEqual(17, len(matrix["scenario_campaign"]["common"]))
        self.assertEqual(
            20,
            sum(len(rows) for rows in matrix["scenario_campaign"]["transport_specific"].values()),
        )
        self.assertEqual(0, matrix["execution_counts"]["dev_board_phy_runs"])
        self.assertEqual(0, matrix["execution_counts"]["assembled_hil_runs"])
        self.assertTrue(all(value is False for value in matrix["authorization"].values()))

    def test_dry_run_exposes_all_tracks_without_authorizing_purchase(self):
        result = subprocess.run(
            [sys.executable, "tools/run_f4_acceptance.py", "--dry-run"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        plan = json.loads(result.stdout)
        self.assertEqual(24, len(plan["tracks"]))
        self.assertFalse(plan["authorized_purchase"])
        self.assertEqual(
            {"reviewed", "planned", "deferred_to_F10"},
            {row["state"] for row in plan["tracks"]},
        )


if __name__ == "__main__":
    unittest.main()
