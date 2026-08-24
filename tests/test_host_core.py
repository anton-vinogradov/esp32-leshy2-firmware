import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class HostCoreExecutionTests(unittest.TestCase):
    def test_ti_map_timestamp_normalizer_is_deterministic_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            map_path = Path(directory) / "image.map"
            map_path.write_text(
                "header\n>> Linked Tue Aug 25 02:03:11 2026\nbody\n",
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment["SOURCE_DATE_EPOCH"] = "1234567890"
            result = subprocess.run(
                ["python3", "tools/normalize_ti_map.py", str(map_path)],
                cwd=REPO_ROOT,
                env=environment,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual("", result.stdout)
            self.assertEqual(
                "header\n>> Linked SOURCE_DATE_EPOCH=1234567890\nbody\n",
                map_path.read_text(encoding="utf-8"),
            )

            second = subprocess.run(
                ["python3", "tools/normalize_ti_map.py", str(map_path)],
                cwd=REPO_ROOT,
                env=environment,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(0, second.returncode)
            self.assertEqual(
                "header\n>> Linked SOURCE_DATE_EPOCH=1234567890\nbody\n",
                map_path.read_text(encoding="utf-8"),
            )

            invalid_path = Path(directory) / "invalid.map"
            invalid_path.write_text("header without linker date\n", encoding="utf-8")
            invalid = subprocess.run(
                ["python3", "tools/normalize_ti_map.py", str(invalid_path)],
                cwd=REPO_ROOT,
                env=environment,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertNotEqual(0, invalid.returncode)
            self.assertIn("timestamp header not found", invalid.stdout)

    def test_f2_5_clean_build_evidence_is_complete(self):
        result = subprocess.run(
            ["python3", "tools/review_f2_5_reproducibility.py", "--check"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("52/52 byte-identical artifacts", result.stdout)
        review = json.loads(
            (REPO_ROOT / "config/f2_5_reproducibility_review.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(52, len(review["final_manifest"]))
        self.assertEqual(24, review["distributable_images_scanned_for_absolute_workspace_path"])
        self.assertEqual(0, review["absolute_workspace_path_leaks"])
        self.assertFalse(review["claims"]["runtime_boot_proven"])

    def test_environment_lock_is_complete_and_self_consistent(self):
        result = subprocess.run(
            ["python3", "tools/verify_environment_lock.py"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("environment lock OK: 26 archives", result.stdout)

    def test_five_target_build_matrix_has_one_dispatcher(self):
        result = subprocess.run(
            ["python3", "tools/build_targets.py", "verify-matrix"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("build matrix OK: 5 targets, 2 configurations", result.stdout)

        matrix = json.loads(
            (REPO_ROOT / "config/build_matrix.json").read_text(encoding="utf-8")
        )
        self.assertEqual("F2.0.3", matrix["stage"])
        self.assertEqual("reviewed", matrix["status"])
        self.assertEqual({"debug", "release"}, set(matrix["configurations"]))
        self.assertEqual(
            {"s3", "c5", "rp", "pack", "safety"},
            {target["id"] for target in matrix["targets"]},
        )
        self.assertFalse(matrix["policy"]["shell_execution"])
        self.assertFalse(matrix["policy"]["network_during_configure_or_build"])
        self.assertEqual(26, sum(len(target["artifacts"]) for target in matrix["targets"]))
        for target in matrix["targets"]:
            if target["family"] == "esp_idf":
                self.assertIn("IDF_TOOLS_PATH", target["required_environment"])
                self.assertIn("IDF_PYTHON_ENV_PATH", target["required_environment"])

        dry_run = subprocess.run(
            [
                "python3",
                "tools/build_targets.py",
                "configure",
                "--target",
                "all",
                "--config",
                "debug",
                "--dry-run",
            ],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        for target in ("s3", "c5", "rp", "pack", "safety"):
            self.assertIn(f"{target}:debug:configure", dry_run.stdout)

        preflight_source = (REPO_ROOT / "tools/toolchain_preflight.py").read_text(
            encoding="utf-8"
        )
        dispatcher_source = (REPO_ROOT / "tools/build_targets.py").read_text(
            encoding="utf-8"
        )
        for token in (
            "git\", \"-C\"",
            "pip\", \"check\"",
            "esp32c5_rev0_rom.elf",
            "startup_mspm0c1105_c1106_ticlang.c",
            "validate_exact_environment",
        ):
            self.assertIn(token, preflight_source)
        self.assertGreaterEqual(dispatcher_source.count("validate_exact_environment"), 3)

    def test_source_ownership_boundaries_are_enforced(self):
        result = subprocess.run(
            ["python3", "tools/check_source_layout.py"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("source layout OK: 8 portable files", result.stdout)

        layout = json.loads(
            (REPO_ROOT / "config/source_layout.json").read_text(encoding="utf-8")
        )
        self.assertEqual("F2.1.0", layout["stage"])
        self.assertEqual("reviewed", layout["status"])
        self.assertFalse(layout["principles"]["portable_code_has_target_pins"])
        self.assertFalse(layout["principles"]["generated_files_are_hand_edited"])
        manifest = json.loads(
            (REPO_ROOT / "generated/source_manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual("F2.3.1", manifest["stage"])
        self.assertEqual("generated", manifest["status"])
        self.assertEqual(11, len(manifest["files"]))
        self.assertEqual(125, manifest["allocated_contacts"])
        self.assertFalse(manifest["claims"]["generated_files_are_hand_edited"])
        self.assertFalse(manifest["claims"]["target_projects_consume_generated_sources"])

    def test_build_policy_is_strict_across_sdk_families(self):
        result = subprocess.run(
            ["python3", "tools/check_build_policy.py"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("build policy OK: C17/C++17", result.stdout)

        policy = json.loads(
            (REPO_ROOT / "config/build_policy.json").read_text(encoding="utf-8")
        )
        self.assertEqual("F2.1.1", policy["stage"])
        self.assertEqual("reviewed", policy["status"])
        self.assertEqual("-Og", policy["configurations"]["debug"]["optimization"])
        self.assertEqual("-Os", policy["configurations"]["release"]["optimization"])
        self.assertFalse(policy["configurations"]["release"]["lto"])
        self.assertEqual("required", policy["link"]["map_file"])
        self.assertEqual(
            {"esp_idf", "pico_sdk", "ti_mspm0_sdk"}, set(policy["families"])
        )

    def test_f2_1_boundary_passes_as_one_review(self):
        result = subprocess.run(
            ["python3", "tools/review_f2_1.py"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("F2.1 integrated review OK", result.stdout)

        review = json.loads(
            (REPO_ROOT / "config/f2_1_review.json").read_text(encoding="utf-8")
        )
        self.assertEqual("F2.1.2", review["stage"])
        self.assertEqual("reviewed", review["status"])
        self.assertEqual(24, review["evidence"]["host_scenarios"])
        self.assertFalse(review["claims"]["target_projects_created"])
        self.assertFalse(review["claims"]["target_builds_run"])

    def test_s3_target_project_has_reviewed_structure_without_pin_claims(self):
        result = subprocess.run(
            ["python3", "tools/check_target_projects.py"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("S3/C5/RP/Pack/Safety structures reviewed", result.stdout)

        registry = json.loads(
            (REPO_ROOT / "config/target_projects.json").read_text(encoding="utf-8")
        )
        s3 = registry["projects"]["s3"]
        self.assertEqual("F2.2.0", s3["substep"])
        self.assertEqual("reviewed_structure", s3["status"])
        self.assertFalse(s3["pins_consumed"])
        self.assertFalse(s3["configure_run"])
        self.assertFalse(s3["build_run"])
        c5 = registry["projects"]["c5"]
        self.assertEqual("F2.2.1", c5["substep"])
        self.assertEqual("reviewed_structure", c5["status"])
        self.assertFalse(c5["pins_consumed"])
        self.assertFalse(c5["configure_run"])
        self.assertFalse(c5["build_run"])
        rp = registry["projects"]["rp"]
        self.assertEqual("F2.2.2", rp["substep"])
        self.assertEqual("reviewed_structure", rp["status"])
        self.assertEqual("rp2350-arm-s", rp["sdk_target"])
        self.assertEqual(2097152, rp["flash_bytes"])
        self.assertFalse(rp["pins_consumed"])
        self.assertFalse(rp["configure_run"])
        self.assertFalse(rp["build_run"])
        pack = registry["projects"]["pack"]
        self.assertEqual("F2.2.3", pack["substep"])
        self.assertEqual("reviewed_structure", pack["status"])
        self.assertEqual("MSPM0C1106SDGS20R", pack["device"])
        self.assertEqual("VSSOP-20(DGS20)", pack["package"])
        self.assertEqual({"origin": 0, "bytes": 16384}, pack["boot_flash"])
        self.assertEqual({"origin": 16384, "bytes": 22528}, pack["application_flash"])
        self.assertFalse(pack["pins_consumed"])
        self.assertFalse(pack["configure_run"])
        self.assertFalse(pack["build_run"])
        safety = registry["projects"]["safety"]
        self.assertEqual("F2.2.4", safety["substep"])
        self.assertEqual("reviewed_structure", safety["status"])
        self.assertEqual("MSPM0C1106SDGS20R", safety["device"])
        self.assertEqual("VSSOP-20(DGS20)", safety["package"])
        self.assertEqual({"origin": 0, "bytes": 16384}, safety["boot_flash"])
        self.assertEqual(
            {"origin": 16384, "bytes": 22528}, safety["application_flash"]
        )
        self.assertFalse(safety["pins_consumed"])
        self.assertFalse(safety["configure_run"])
        self.assertFalse(safety["build_run"])

    def test_f2_2_project_boundaries_pass_as_one_review(self):
        result = subprocess.run(
            ["python3", "tools/review_f2_2.py"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("F2.2 integrated review OK", result.stdout)

        review = json.loads(
            (REPO_ROOT / "config/f2_2_review.json").read_text(encoding="utf-8")
        )
        self.assertEqual("F2.2.5", review["stage"])
        self.assertEqual("reviewed", review["status"])
        self.assertEqual(5, review["evidence"]["target_projects"])
        self.assertEqual(29, review["evidence"]["project_files"])
        self.assertEqual(26, review["evidence"]["named_build_artifacts"])
        self.assertEqual(20, review["evidence"]["rendered_configure_and_build_plans"])
        self.assertTrue(review["claims"]["target_projects_created"])
        self.assertFalse(review["claims"]["target_configure_run"])
        self.assertFalse(review["claims"]["target_builds_run"])
        self.assertFalse(review["claims"]["target_emulators_run"])

    def test_f2_3_generator_input_matches_reviewed_h2_contract(self):
        result = subprocess.run(
            ["python3", "tools/validate_bsp_generation_input.py"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("BSP generation input OK: 5 domains, 125 contacts", result.stdout)

        model = json.loads(
            (REPO_ROOT / "config/bsp_generation_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual("F2.3.0", model["stage"])
        self.assertEqual("reviewed", model["status"])
        self.assertEqual(125, model["expected_counts"]["allocated_contacts"])
        self.assertEqual(112, model["expected_counts"]["unique_nets"])
        self.assertTrue(model["claims"]["input_model_validated"])
        self.assertFalse(model["claims"]["generated_sources_created"])

    def test_f2_3_generated_bsp_is_reproducible_and_valid_c17(self):
        result = subprocess.run(
            ["python3", "tools/generate_hardware_bsp.py", "--check"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("generated BSP OK: 11 generated C/header files", result.stdout)

        sources = sorted((REPO_ROOT / "generated/hardware/src").glob("*_bsp.c"))
        self.assertEqual(5, len(sources))
        compile_result = subprocess.run(
            [
                "cc",
                "-std=c17",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-pedantic",
                "-Igenerated/hardware/include",
                "-fsyntax-only",
                *[str(path.relative_to(REPO_ROOT)) for path in sources],
            ],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual("", compile_result.stdout)

    def test_f2_3_each_target_consumes_only_its_generated_domain(self):
        result = subprocess.run(
            ["python3", "tools/check_bsp_target_consumption.py"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("BSP target consumption OK", result.stdout)
        contract = json.loads(
            (REPO_ROOT / "config/bsp_target_consumption.json").read_text(encoding="utf-8")
        )
        self.assertEqual("F2.3.2", contract["stage"])
        self.assertEqual("reviewed", contract["status"])
        self.assertEqual({"s3", "c5", "rp", "pack", "safety"}, set(contract["projects"]))
        self.assertTrue(contract["claims"]["one_generated_domain_per_project"])
        self.assertFalse(contract["claims"]["target_builds_run"])

    def test_f2_3_generated_bsp_boundary_passes_as_one_review(self):
        result = subprocess.run(
            ["python3", "tools/review_f2_3.py"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("F2.3 integrated review OK", result.stdout)
        review = json.loads(
            (REPO_ROOT / "config/f2_3_review.json").read_text(encoding="utf-8")
        )
        self.assertEqual("F2.3.3", review["stage"])
        self.assertEqual("reviewed", review["status"])
        self.assertEqual(125, review["evidence"]["allocated_contacts"])
        self.assertEqual(11, review["evidence"]["generated_files"])
        self.assertEqual(5, review["evidence"]["target_consumers"])
        self.assertTrue(review["claims"]["generated_outputs_are_byte_reproducible"])
        self.assertFalse(review["claims"]["target_builds_run"])

    def test_portable_safety_core_executes_all_scenarios(self):
        self.assertIsNotNone(shutil.which("make"))
        self.assertIsNotNone(shutil.which("cc"))
        result = subprocess.run(
            ["make", "host-test"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertIn("host safety core: 8 scenarios passed", result.stdout)
        self.assertIn("host L2IP core: 4 scenarios passed", result.stdout)
        self.assertIn("host update core: 5 scenarios passed", result.stdout)
        self.assertIn("host five-domain model: 7 scenarios passed", result.stdout)

    def test_preorder_contract_does_not_overstate_firmware_or_emulation(self):
        contract_path = REPO_ROOT / "config/preorder_verification_contract.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        self.assertEqual("LESHY2-PREORDER-1", contract["contract_id"])
        self.assertIn(
            "reviewed portable C safety, L2IP, update",
            contract["current_truth"]["executable_firmware"],
        )
        self.assertIn("not run", contract["current_truth"]["instruction_emulation"])
        gates = {gate["id"]: gate["status"] for gate in contract["gates"]}
        self.assertEqual(
            "reviewed",
            gates["P4_EXECUTABLE_FIRMWARE_MODEL"],
        )
        self.assertEqual("not_started", gates["P5_TARGET_BUILDS_EMULATION"])
        self.assertEqual("not_authorized", gates["P7_ENGINEERING_SAMPLE_ORDER"])

        hardware_copy = (
            REPO_ROOT.parent
            / "esp32-leshy2/hardware/verification/preorder-verification-contract.json"
        )
        if hardware_copy.is_file():
            self.assertEqual(
                contract_path.read_bytes(),
                hardware_copy.read_bytes(),
                "hardware and firmware pre-order gates diverged",
            )


if __name__ == "__main__":
    unittest.main()
