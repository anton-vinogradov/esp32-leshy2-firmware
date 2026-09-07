import json
import tempfile
import unittest
from pathlib import Path

from tests.test_f2_r2_dispatcher import evidence_fixture, fixture_git


class R2EvidenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.dispatcher, self.matrix_path, self.matrix, self.evidence = evidence_fixture(self.repo)
        self.evidence_path = self.repo / "evidence.json"
        self.artifact = self.repo / self.evidence["jobs"][0]["artifacts"][0]["path"]

    def errors(self):
        self.evidence_path.write_text(json.dumps(self.evidence), encoding="utf-8")
        return self.dispatcher.check_evidence(
            self.evidence_path, self.matrix_path, self.matrix, self.repo
        )

    def assert_finding(self, text):
        errors = self.errors()
        self.assertTrue(any(text in error for error in errors), errors)

    def test_docs_only_head_descendant_does_not_invalidate_input_commit(self):
        (self.repo / "README.md").write_text("Evidence publication only.\n")
        fixture_git(self.repo, "add", "README.md")
        fixture_git(self.repo, "commit", "-qm", "publish documentation")
        self.assertNotEqual(self.evidence["repo_commit"], fixture_git(self.repo, "rev-parse", "HEAD"))
        self.assertEqual([], self.errors())

    def test_same_size_artifact_replacement_is_rehashed(self):
        self.artifact.write_bytes(b"NO")
        self.assert_finding("artifact bytes/hash differ")

    def test_missing_artifact_fails(self):
        self.artifact.unlink()
        self.assert_finding("missing or aliased artifact")

    def test_symlink_to_identical_artifact_fails(self):
        replacement = self.repo / "replacement.bin"
        replacement.write_bytes(self.artifact.read_bytes())
        self.artifact.unlink()
        self.artifact.symlink_to(replacement)
        self.assert_finding("missing or aliased artifact")

    def test_numeric_but_wrong_epoch_fails(self):
        self.evidence["source_date_epoch"] = str(int(self.evidence["source_date_epoch"]) + 1)
        self.assert_finding("SOURCE_DATE_EPOCH differs from its Git commit")

    def test_well_formed_unavailable_commit_fails(self):
        self.evidence["repo_commit"] = "f" * 40
        self.assert_finding("Git commit is unavailable")

    def test_blob_object_is_not_a_commit(self):
        self.evidence["repo_commit"] = fixture_git(
            self.repo, "rev-parse", "HEAD:config/f2_r2_build_matrix.json"
        )
        self.assert_finding("Git object is not a commit")

    def test_current_matrix_cannot_be_bound_to_different_committed_bytes(self):
        self.matrix_path.write_text(self.matrix_path.read_text() + "\n")
        self.evidence["inputs"]["matrix"]["sha256"] = self.dispatcher.sha256(self.matrix_path)
        self.assert_finding("input differs from its Git commit: config/f2_r2_build_matrix.json")

    def test_pinned_build_input_is_checked_on_disk(self):
        relative = self.matrix["inputs"]["build_policy"]["path"]
        policy_path = self.repo / relative
        policy_path.write_text(policy_path.read_text() + "\n")
        self.assert_finding(f"input differs from its Git commit: {relative}")

    def test_changed_artifact_path_is_rejected_before_reading_it(self):
        self.evidence["jobs"][0]["artifacts"][0]["path"] = "../outside.bin"
        self.assert_finding("artifact inventory changed")


if __name__ == "__main__":
    unittest.main()
