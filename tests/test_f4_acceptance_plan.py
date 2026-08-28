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
        self.assertEqual("historical_superseded_by_r2", plan["status"])
        self.assertEqual("R1", plan["authority"]["baseline"])
        self.assertFalse(plan["authority"]["allowed_as_r2_current_progress"])
        self.assertIsNone(plan["next"])
        self.assertEqual(24, len(plan["tracks"]))
        self.assertFalse(plan["authorized_purchase"])
        self.assertEqual(
            {"reviewed", "planned", "deferred_to_F10"},
            {row["state"] for row in plan["tracks"]},
        )

    def test_integrated_r1_evidence_is_historical_and_has_no_next_gate(self):
        subprocess.run(
            [sys.executable, "tools/run_f4_acceptance.py", "--check-evidence"],
            cwd=REPO_ROOT,
            check=True,
        )
        record = json.loads(
            (REPO_ROOT / "config/f4_acceptance_current.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("historical_superseded_by_r2", record["status"])
        self.assertEqual("F4.1.3", record["historical_last_reviewed_substep"])
        self.assertNotIn("current_substep", record)
        self.assertIsNone(record["next"])
        self.assertEqual(
            "not_run_superseded_by_r2",
            record["superseded_physical_gate"]["status"],
        )
        self.assertEqual(0, record["execution_counts"]["physical_transport_runs"])

    def test_superseded_r1_runner_cannot_advance_or_rewrite_evidence(self):
        for mode in ("--snapshot", "--run-available"):
            result = subprocess.run(
                [sys.executable, "tools/run_f4_acceptance.py", mode, "--write"],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertNotEqual(0, result.returncode, result.stdout)
            self.assertIn("superseded by R2", result.stdout)

    def test_every_superseded_f4_writer_is_fail_closed_and_read_only(self):
        writers = (
            ("tools/review_f4_1_core.py", "config/f4_1_1_high_speed_core_review.json"),
            ("tools/review_f4_1_endpoints.py", "config/f4_1_2_s3_c5_endpoint_review.json"),
            ("tools/review_f4_1_qemu.py", "config/f4_1_3_s3_c5_qemu_review.json"),
        )
        before = {
            artifact: (REPO_ROOT / artifact).read_bytes()
            for _, artifact in writers
        }
        for script, _ in writers:
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, script, "--run", "--write"],
                    cwd=REPO_ROOT,
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                self.assertNotEqual(0, result.returncode, result.stdout)
                self.assertIn("superseded by R2", result.stdout)
                self.assertIn("immutable", result.stdout)
        after = {
            artifact: (REPO_ROOT / artifact).read_bytes()
            for _, artifact in writers
        }
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
