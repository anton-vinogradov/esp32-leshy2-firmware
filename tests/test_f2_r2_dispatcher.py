import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/build_f2_r2_targets.py"


def load_dispatcher():
    spec = importlib.util.spec_from_file_location("build_f2_r2_targets", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class F2R2DispatcherTest(unittest.TestCase):
    def run_tool(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

    def test_matrix_and_policy_are_executable_but_unexecuted(self):
        result = self.run_tool("verify-matrix")
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("6 targets x 2 configurations", result.stdout)
        self.assertIn("0 executions", result.stdout)

        matrix = json.loads(
            (ROOT / "config/f2_r2_build_matrix.json").read_text(encoding="utf-8")
        )
        policy = json.loads(
            (ROOT / "config/f2_r2_build_policy.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            "generated/r2/hardware/**",
            policy["scope"]["strict_warnings_apply_to"][-1],
        )
        self.assertEqual(matrix["build_root"], policy["reproducibility"]["build_root"])
        self.assertEqual({0}, set(policy["execution"].values()))
        for target in ("rf_rp", "hub_rp"):
            cmake = (ROOT / "targets" / target / "CMakeLists.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("set(CMAKE_C_EXTENSIONS ON)", cmake)
            self.assertIn("set_source_files_properties(", cmake)
            self.assertIn("-std=c17", cmake)
            self.assertNotIn(
                f"target_compile_options(leshy2_{target} PRIVATE", cmake
            )

    def test_full_qualification_dry_run_is_24_shell_free_argv_commands(self):
        evidence = ROOT / "config/f2_r2_build_qualification.json"
        self.assertTrue(evidence.exists())
        before = evidence.read_bytes()
        result = self.run_tool("qualify", "--dry-run")
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertEqual(12, result.stdout.count('"action": "configure"'))
        self.assertEqual(12, result.stdout.count('"action": "build"'))
        self.assertIn("0 executions; 0 evidence writes", result.stdout)
        self.assertEqual(before, evidence.read_bytes())

    def test_evidence_check_fails_closed_when_no_complete_record_exists(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = self.run_tool(
                "verify-evidence", "--evidence", str(Path(temporary) / "missing.json")
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("qualification evidence is absent", result.stdout)

    def test_complete_synthetic_evidence_validates_and_tampering_fails(self):
        dispatcher = load_dispatcher()
        matrix_path = ROOT / "config/f2_r2_build_matrix.json"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        environment = dispatcher.local_environment()
        source_date_epoch = environment["SOURCE_DATE_EPOCH"]
        environment.update(matrix["locked_environment"]["environment"])
        environment["SOURCE_DATE_EPOCH"] = source_date_epoch
        targets = dispatcher.matrix_targets(matrix)
        jobs = []
        for target_id in dispatcher.TARGET_IDS:
            target = targets[target_id]
            for configuration in dispatcher.CONFIGURATIONS:
                build = dispatcher.job_build_root(matrix, target_id, configuration)
                artifacts = [
                    {
                        "kind": artifact["kind"],
                        "path": str(
                            dispatcher.artifact_path(
                                artifact["path"], build
                            ).relative_to(ROOT)
                        ),
                        "bytes": 1,
                        "sha256": "0" * 64,
                    }
                    for artifact in target["artifacts"]
                ]
                gates = [
                    {
                        "artifact": str(
                            dispatcher.artifact_path(
                                gate["artifact"], build
                            ).relative_to(ROOT)
                        ),
                        "bytes": 1,
                        "warning_bytes": gate["warning_bytes"],
                        "maximum_bytes": gate["maximum_bytes"],
                        "status": "passed",
                        "source": gate["source"],
                    }
                    for gate in target["size_gates"]
                ]
                jobs.append(
                    {
                        "target": target_id,
                        "configuration": configuration,
                        "artifacts": artifacts,
                        "size_gates": gates,
                        "warnings": [],
                    }
                )
        commands = dispatcher.evidence_command_rows(
            matrix,
            dispatcher.TARGET_IDS,
            dispatcher.CONFIGURATIONS,
            ("configure", "build"),
        )
        for command in commands:
            command["status"] = "passed"
        evidence = dispatcher.qualification_evidence(
            matrix_path,
            matrix,
            jobs,
            commands,
            environment,
            "0" * 40,
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "evidence.json"
            path.write_text(json.dumps(evidence), encoding="utf-8")
            self.assertEqual(
                [],
                dispatcher.check_evidence(
                    path, matrix_path, matrix
                ),
            )
            evidence["jobs"][0]["artifacts"][0]["sha256"] = "tampered"
            path.write_text(json.dumps(evidence), encoding="utf-8")
            self.assertTrue(
                dispatcher.check_evidence(path, matrix_path, matrix)
            )

    def test_artifact_verifier_rejects_missing_and_oversized_images(self):
        dispatcher = load_dispatcher()
        matrix = json.loads(
            (ROOT / "config/f2_r2_build_matrix.json").read_text(encoding="utf-8")
        )
        target = copy.deepcopy(
            next(row for row in matrix["targets"] if row["id"] == "s3")
        )
        target["size_gates"][0]["warning_bytes"] = 1
        target["size_gates"][0]["maximum_bytes"] = 2
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            build = repo / "build/r2/targets/s3/debug"
            build.mkdir(parents=True)
            with self.assertRaises(dispatcher.QualificationError):
                dispatcher.verify_job(matrix, target, "debug", repo)

            for artifact in target["artifacts"]:
                path = Path(artifact["path"].format(build=str(build)))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"ok")
            verified = dispatcher.verify_job(matrix, target, "debug", repo)
            self.assertEqual(5, len(verified["artifacts"]))

            image = Path(target["size_gates"][0]["artifact"].format(build=str(build)))
            image.write_bytes(b"xxx")
            with self.assertRaises(dispatcher.QualificationError):
                dispatcher.verify_job(matrix, target, "debug", repo)

    def test_actual_qualification_requires_atomic_evidence_mode(self):
        result = self.run_tool("qualify")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("requires --write-evidence", result.stdout)

    def test_matrix_validator_rejects_shell_boundaries(self):
        dispatcher = load_dispatcher()
        matrix = json.loads(
            (ROOT / "config/f2_r2_build_matrix.json").read_text(encoding="utf-8")
        )
        matrix["targets"][0]["commands"]["build"] = ["sh", "-c", "false"]
        errors = dispatcher.validate_matrix(matrix)
        self.assertTrue(any("shell" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
