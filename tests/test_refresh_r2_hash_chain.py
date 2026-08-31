import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "refresh_r2_hash_chain.py"


def load_module():
    spec = importlib.util.spec_from_file_location("refresh_r2_hash_chain", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class RefreshR2HashChainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.zero = "0" * 64
        self.hardware_sha = "1" * 64
        self.projection = {
            "id": "FW-H0-R2",
            "hardware_source": "esp32-leshy2/hardware/architecture/h0-r2-rebaseline.json",
            "hardware_source_sha256": self.hardware_sha,
            "hardware_sources": {
                "functional": {
                    "path": "esp32-leshy2/hardware/architecture/h0-r2-rebaseline.json",
                    "sha256": self.hardware_sha,
                }
            },
            "domains": [],
        }
        self.write_json(self.module.PROJECTION, self.projection)
        self.write_json(
            self.module.F0_EXECUTION_GATES,
            {"stage": "F0-R2.4", "display_clock_mhz": 20},
        )
        self.write_json(
            self.module.F0_REVIEW,
            {
                "stage": "F0-R2",
                "hardware_source": self.projection["hardware_source"],
                "hardware_source_sha256": self.zero,
            },
        )
        self.write_json(
            self.module.F1_PORTABLE,
            {
                "stage": "F1-R2.0",
                "inputs": {"f0_review": self.lock(self.module.F0_REVIEW)},
            },
        )
        self.write_json(
            self.module.F2_REBASELINE,
            {
                "stage": "F2-R2.0",
                "inputs": {
                    "r2_hardware_projection": self.lock(self.module.PROJECTION),
                    "execution_gates": self.lock(self.module.F0_EXECUTION_GATES),
                }
            },
        )
        self.write_json(
            self.module.F2_MATRIX,
            {
                "stage": "F2-R2.1",
                "inputs": {
                    "rebaseline_plan": self.lock(self.module.F2_REBASELINE),
                    "execution_gates": self.lock(self.module.F0_EXECUTION_GATES),
                },
            },
        )
        self.write_json(
            self.module.F2_PROJECTS,
            {
                "stage": "F2-R2.2",
                "inputs": {
                    "build_matrix": self.lock(self.module.F2_MATRIX),
                    "r2_hardware_projection": self.lock(self.module.PROJECTION),
                }
            },
        )
        self.write_json(
            self.module.F2_BSP_MODEL,
            {
                "stage": "F2-R2.3",
                "source": self.lock(self.module.PROJECTION),
                "outputs": copy.deepcopy(self.module.EXPECTED_BSP_OUTPUTS),
            },
        )

    def tearDown(self):
        self.temporary.cleanup()

    def lock(self, path):
        return {"path": path, "sha256": self.zero}

    def write_json(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def fake_renderer(model, hardware):
        outputs = {
            "generated/r2/source_manifest.json": json.dumps(
                {"source": model["source"], "domains": hardware["domains"]},
                indent=2,
            )
            + "\n"
        }
        for index in range(13):
            outputs[f"generated/r2/hardware/file-{index}.txt"] = (
                f"{model['source']['sha256']}:{index}\n"
            )
        return outputs

    def snapshot(self):
        return {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }

    def test_default_check_is_read_only_and_reports_complete_stale_set(self):
        before = self.snapshot()
        output = StringIO()
        with redirect_stdout(output):
            result = self.module.run(
                root=self.root, write=False, render_bsp=self.fake_renderer
            )
        self.assertEqual(1, result)
        self.assertEqual(before, self.snapshot())
        self.assertIn("stale: config/f0_r2_review.json", output.getvalue())
        self.assertIn("stale: generated/r2/source_manifest.json", output.getvalue())

    def test_write_refreshes_the_ordered_chain_and_generated_bsp(self):
        self.assertEqual(
            0,
            self.module.run(
                root=self.root, write=True, render_bsp=self.fake_renderer
            ),
        )
        projection_text = (self.root / self.module.PROJECTION).read_text()
        execution_gates_text = (
            self.root / self.module.F0_EXECUTION_GATES
        ).read_text()
        f0_text = (self.root / self.module.F0_REVIEW).read_text()
        rebaseline_text = (self.root / self.module.F2_REBASELINE).read_text()
        matrix_text = (self.root / self.module.F2_MATRIX).read_text()

        f0 = json.loads(f0_text)
        f1 = json.loads((self.root / self.module.F1_PORTABLE).read_text())
        rebaseline = json.loads(rebaseline_text)
        matrix = json.loads(matrix_text)
        projects = json.loads((self.root / self.module.F2_PROJECTS).read_text())
        bsp = json.loads((self.root / self.module.F2_BSP_MODEL).read_text())

        self.assertEqual(self.hardware_sha, f0["hardware_source_sha256"])
        self.assertEqual(sha(f0_text), f1["inputs"]["f0_review"]["sha256"])
        self.assertEqual(
            sha(projection_text),
            rebaseline["inputs"]["r2_hardware_projection"]["sha256"],
        )
        self.assertEqual(
            sha(execution_gates_text),
            rebaseline["inputs"]["execution_gates"]["sha256"],
        )
        self.assertEqual(
            sha(rebaseline_text), matrix["inputs"]["rebaseline_plan"]["sha256"]
        )
        self.assertEqual(
            sha(execution_gates_text),
            matrix["inputs"]["execution_gates"]["sha256"],
        )
        self.assertEqual(
            sha(matrix_text), projects["inputs"]["build_matrix"]["sha256"]
        )
        self.assertEqual(
            sha(projection_text),
            projects["inputs"]["r2_hardware_projection"]["sha256"],
        )
        self.assertEqual(sha(projection_text), bsp["source"]["sha256"])
        self.assertEqual(
            0,
            self.module.run(
                root=self.root, write=False, render_bsp=self.fake_renderer
            ),
        )

    def test_mutated_lock_path_is_rejected_without_any_write(self):
        value = json.loads((self.root / self.module.F2_PROJECTS).read_text())
        value["inputs"]["build_matrix"]["path"] = "config/not-the-matrix.json"
        self.write_json(self.module.F2_PROJECTS, value)
        before = self.snapshot()
        with self.assertRaisesRegex(self.module.ChainError, "path changed"):
            self.module.run(
                root=self.root, write=True, render_bsp=self.fake_renderer
            )
        self.assertEqual(before, self.snapshot())

    def test_mutated_digest_is_rejected_without_any_write(self):
        value = json.loads((self.root / self.module.F1_PORTABLE).read_text())
        value["inputs"]["f0_review"]["sha256"] = "NOT-A-DIGEST"
        self.write_json(self.module.F1_PORTABLE, value)
        before = self.snapshot()
        with self.assertRaisesRegex(self.module.ChainError, "not a lowercase SHA-256"):
            self.module.run(
                root=self.root, write=True, render_bsp=self.fake_renderer
            )
        self.assertEqual(before, self.snapshot())

    def test_generated_output_escape_is_rejected(self):
        def escaped_renderer(model, hardware):
            outputs = self.fake_renderer(model, hardware)
            outputs.pop("generated/r2/hardware/file-12.txt")
            outputs["../outside.txt"] = "no\n"
            return outputs

        before = self.snapshot()
        with self.assertRaisesRegex(self.module.ChainError, "unsafe generated BSP path"):
            self.module.run(
                root=self.root, write=True, render_bsp=escaped_renderer
            )
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root.parent / "outside.txt").exists())

    def test_cli_rejects_unknown_arguments(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--not-a-mode"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("unrecognized arguments", result.stdout)

    def test_cli_defaults_to_check_and_requires_explicit_write(self):
        with mock.patch.object(self.module, "run", return_value=0) as run:
            self.assertEqual(0, self.module.main([]))
            run.assert_called_once_with(write=False)
        with mock.patch.object(self.module, "run", return_value=0) as run:
            self.assertEqual(0, self.module.main(["--check"]))
            run.assert_called_once_with(write=False)
        with mock.patch.object(self.module, "run", return_value=0) as run:
            self.assertEqual(0, self.module.main(["--write"]))
            run.assert_called_once_with(write=True)


if __name__ == "__main__":
    unittest.main()
