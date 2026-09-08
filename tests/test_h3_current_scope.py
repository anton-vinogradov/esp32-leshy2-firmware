import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import h3_current_scope as scope


class CurrentH3ScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.hw = Path(self.temp.name)
        (self.hw / "model.py").write_text("model = 1\n")
        self.owner = SimpleNamespace(
            REQUIREMENTS={"H3-fixture": ("fitted_part",)},
            required_sources=lambda _artifact: {"model.py"},
            _proof=self.proof,
            admits_current=lambda data, _artifact: data["status"] == "pass",
        )
        self.path = self.hw / "fixture.json"
        self.data = self.fixture()
        self.save()
        self.addCleanup(patch.stopall)
        patch.object(scope, "HW", self.hw).start()
        patch.object(scope, "hardware_scope", return_value=self.owner).start()

    @staticmethod
    def proof(artifact, numerical, applicability):
        findings = [] if numerical is True and applicability == {"fitted_part": True} else ["applicability:fitted_part"]
        return {"schema_version": 1, "artifact": artifact,
                "status": "review_required" if findings else "pass",
                "numerical_status": "provisional_pass", "numerical_checks_pass": numerical,
                "applicability_checks": applicability, "open_findings": findings,
                "current_analytical_scope_complete": not findings,
                "production_release_authorized": False, "battery_energization_authorized": False}

    def fixture(self, complete=False):
        proof = self.proof("H3-fixture", True, {"fitted_part": complete})
        bindings = {"model.py": hashlib.sha256((self.hw / "model.py").read_bytes()).hexdigest()}
        proof["source_sha256"] = bindings
        return {"artifact": "H3-fixture", "status": proof["status"],
                "current_power_scope": proof, "source_sha256": bindings,
                "current_analytical_scope_complete": complete,
                "open_analytical_findings": proof["open_findings"],
                "production_release_authorized": False, "battery_energization_authorized": False,
                "authorization": {"fabrication": False}, "errors": list(proof["open_findings"])}

    def save(self):
        self.path.write_text(json.dumps(self.data))

    def inspect(self):
        return scope.inspect_current_power([(self.path, "H3-fixture")])

    def test_review_import_is_diagnostic_and_fail_closed(self):
        result = scope.bind_scope({"claims": {"h3_r2_analytical_scope_imported": True}}, self.inspect())
        self.assertEqual("review_required", result["status"])
        self.assertEqual("provisional", result["evidence_status"])
        self.assertFalse(any(result["claims"].values()))

    def test_analytical_pass_never_grants_target_or_production(self):
        self.data = self.fixture(True)
        self.save()
        result = self.inspect()
        self.assertTrue(result["current_analytical_scope_complete"])
        for key in ("production_release_authorized", "battery_energization_authorized", "target_execution_authorized"):
            self.assertIs(result[key], False)

    def test_old_plausible_pass_without_proof_is_rejected(self):
        self.data.pop("current_power_scope")
        self.data["status"] = "pass"
        self.save()
        with self.assertRaises(ValueError):
            self.inspect()

    def test_stale_source_is_rejected_even_for_review(self):
        (self.hw / "model.py").write_text("model = 2\n")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.inspect()

    def test_source_change_after_inspection_cannot_publish_unchecked_payload(self):
        proof = self.inspect()
        self.data["status"] = "forged-after-inspection"
        self.save()
        with self.assertRaisesRegex(ValueError, "after inspection"):
            scope.bind_scope({"claims": {}}, proof)

    def test_transient_absolute_snapshot_is_not_published(self):
        result = scope.bind_scope({"claims": {}}, self.inspect())
        self.assertNotIn("_verified_input_snapshot", result["current_power_scope"])
        self.assertNotIn(str(self.hw), json.dumps(result))

    def test_omitting_both_source_maps_cannot_shrink_required_scope(self):
        self.data["source_sha256"].clear()
        self.save()
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.inspect()

    def test_forged_closed_flag_is_rejected(self):
        self.data["current_analytical_scope_complete"] = True
        self.save()
        with self.assertRaises(ValueError):
            self.inspect()

    def test_forged_authority_is_rejected(self):
        self.data["authorization"]["fabrication"] = True
        self.save()
        with self.assertRaises(ValueError):
            self.inspect()

    def test_foreign_artifact_identity_is_rejected(self):
        self.data["artifact"] = "H3-other"
        self.save()
        with self.assertRaises(ValueError):
            self.inspect()

    def test_extra_parent_path_is_rejected(self):
        self.data["source_sha256"]["../outside.json"] = "0" * 64
        self.save()
        with self.assertRaises(ValueError):
            self.inspect()

    def test_recursive_dependency_is_checked(self):
        child = self.hw / "child.json"
        child.write_text(json.dumps({"artifact": "H3-child", "source_sha256": {"model.py": "0" * 64}}))
        self.data["source_sha256"]["child.json"] = hashlib.sha256(child.read_bytes()).hexdigest()
        self.save()
        with self.assertRaisesRegex(ValueError, "stale"):
            self.inspect()

    def test_required_transitive_artifact_cannot_rename_itself_out_of_scope(self):
        self.owner.REQUIREMENTS["H3-required"] = ("fitted_part",)
        relative = "hardware/verification/generated/H3-required.json"
        child = self.hw / relative
        child.parent.mkdir(parents=True)
        child.write_text(json.dumps({"artifact": "not-an-H3-artifact", "status": "pass"}))
        self.data["source_sha256"][relative] = hashlib.sha256(child.read_bytes()).hexdigest()
        self.save()
        with self.assertRaisesRegex(ValueError, "identity"):
            self.inspect()

    def test_alias_pass_cannot_replace_an_open_artifact_proof(self):
        alias = self.hw / "alias.json"
        alias.write_text(json.dumps(self.fixture(True)))
        self.data["source_sha256"]["alias.json"] = hashlib.sha256(alias.read_bytes()).hexdigest()
        self.save()
        with self.assertRaisesRegex(ValueError, "duplicate H3 artifact"):
            self.inspect()


class CurrentH3ImportIntegrationTests(unittest.TestCase):
    def test_all_seven_imports_preserve_open_scope_and_disabled_authority(self):
        for path in sorted((ROOT / "tools").glob("sync_h3_r2_*.py")):
            with self.subTest(path=path.name):
                spec = importlib.util.spec_from_file_location(path.stem, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                result = module.build()
                self.assertEqual("review_required", result["status"])
                self.assertEqual("provisional", result["evidence_status"])
                self.assertGreater(len(result["current_power_scope"]["artifacts"]), 0)
                self.assertFalse(result["claims"]["current_h3_analytical_scope_complete"])
                for key in ("production_release_authorized", "battery_energization_authorized", "target_execution_authorized"):
                    self.assertIs(result["claims"][key], False)


if __name__ == "__main__":
    unittest.main()
