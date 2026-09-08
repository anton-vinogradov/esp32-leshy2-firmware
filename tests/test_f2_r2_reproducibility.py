import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.test_f2_r2_dispatcher import ROOT, evidence_fixture, fixture_git

sys.path.insert(0, str(ROOT / "tools"))
import build_f2_r2_targets as build
import check_f2_r2_build_matrix as matrix_guard
import normalize_r2_map_paths as maps
import review_f2_r2_reproducibility as repro


class MapPublicationTest(unittest.TestCase):
    def test_exact_prefix_only_preserves_addresses_and_symbols(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            path, raw = root / "link.map", root / "recovery/link.map"
            original = b".text 0x00001000 my_symbol\n" + str(root).encode() + b"/common/a.o\n/alien/vendor/b.o\n"
            path.write_bytes(original)
            record = maps.publish_map(path, raw, root)
            self.assertEqual(original, raw.read_bytes())
            self.assertEqual(original.replace(str(root).encode(), b"."), path.read_bytes())
            self.assertEqual([], maps.publication_errors(record, original, path.read_bytes(), str(root).encode()))
            self.assertTrue(maps.source_path_findings(path.read_bytes(), root))
            with self.assertRaises(ValueError):
                maps.publish_map(path, raw, root)

    def test_non_map_and_symlink_are_not_rewritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            image = root / "app.elf"
            image.write_bytes(b"ELF")
            with self.assertRaises(ValueError):
                maps.publish_map(image, root / "raw", root)
            alias = root / "alias.map"
            alias.symlink_to(image)
            with self.assertRaises(ValueError):
                maps.publish_map(alias, root / "raw", root)

    def test_sibling_root_with_same_name_prefix_is_not_normalized(self):
        prefix = b"/workspace/firmware"
        source = prefix + b"/source.c\n" + prefix + b"-other/vendor/startup.c\n"
        published, count = maps.replace_checkout_prefix(source, prefix)
        self.assertEqual(1, count)
        self.assertEqual(b"./source.c\n/workspace/firmware-other/vendor/startup.c\n", published)
        self.assertTrue(maps.source_path_findings(published, Path(prefix.decode())))

    def test_publication_proof_rejects_old_sibling_prefix_rewrite(self):
        raw = b"/workspace/firmware-other/vendor/startup.c"
        wrong = b".-other/vendor/startup.c"
        record = {"raw_sha256": maps.digest(raw), "published_sha256": maps.digest(wrong),
                  "replacement_count": 1, "other_bytes_unchanged": True}
        self.assertTrue(maps.publication_errors(record, raw, wrong, b"/workspace/firmware"))

    def test_other_byte_or_replacement_count_tamper_fails(self):
        raw = b"/workspace/tree/.text 0x1234"
        published = b"./.text 0x1234"
        record = {"raw_sha256": maps.digest(raw), "published_sha256": maps.digest(published),
                  "replacement_count": 1, "other_bytes_unchanged": True}
        self.assertEqual([], maps.publication_errors(record, raw, published, b"/workspace/tree"))
        self.assertTrue(maps.publication_errors(record, raw, b"./.text 0x1235", b"/workspace/tree"))
        record["replacement_count"] = 2
        self.assertTrue(maps.publication_errors(record, raw, published, b"/workspace/tree"))

    def test_scan_covers_binary_unknown_roots_and_relative_paths(self):
        root = Path("/Users/example/checkout")
        for data in (b"ELF\x00/Users/example/checkout/shared\x00", b"\x00/alien/vendor/startup.c\x00", b"/home/builder/sources/x"):
            self.assertTrue(maps.source_path_findings(data, root), data)
        self.assertEqual([], maps.source_path_findings(b"./common/file.c\x00relative/src/a.h\x00/IDF/components/a.c\x00/COMPONENT_main_DIR/main.c\x00/COMPONENT_ESP_SYSTEM_DIR/port/include/private/esp_private", root))

    def test_unknown_dwarf_directory_and_assembler_paths_fail_closed(self):
        root = Path("/workspace/checkout")
        for data in (b"/mnt/runner/sdk/src\0", b"/ci/vendor/library/src\0",
                     b"/Library/Developer/source\0", b"/vendor/foo/startup.asm\0",
                     b"/unusual name/sdk sources\0", b"C:\\vendor\\sources\\startup.asm\0"):
            self.assertTrue(maps.source_path_findings(data, root), data)
        self.assertEqual([], maps.source_path_findings(b"https://example.invalid/source/path\0", root))
        self.assertEqual([], maps.source_path_findings(b"/y7@\x01/y7@\x02\0/W7@/W7@5W7@;W7@\0", root))

    def test_ti_normalization_is_one_known_header_only(self):
        raw = b">> Linked Wed Sep 9 2026\n.text 0x1234\nunknown timestamp 11:22\n"
        expected = b">> Linked SOURCE_DATE_EPOCH=123\n.text 0x1234\nunknown timestamp 11:22\n"
        self.assertEqual(expected, maps.ti_epoch_bytes(raw, "123"))
        for invalid in (b"no known header", raw + b">> Linked duplicate\n"):
            with self.assertRaises(ValueError):
                maps.ti_epoch_bytes(invalid, "123")

    def test_ti_real_helper_retains_raw_sdk_map_exclusively(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "app.map"
            raw = b">> Linked fixture time\n.text 0x1234\n"
            path.write_bytes(raw)
            recovery = root / "recovery"
            recovery.mkdir()
            environment = dict(os.environ, SOURCE_DATE_EPOCH="123", LESHY2_R2_RAW_MAP_RECOVERY=str(recovery))
            argv = [sys.executable, str(ROOT / "tools/normalize_ti_map.py"), str(path)]
            result = subprocess.run(argv, env=environment, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(raw, (recovery / "app.map").read_bytes())
            self.assertEqual(maps.ti_epoch_bytes(raw, "123"), path.read_bytes())
            self.assertNotEqual(0, subprocess.run(argv, env=environment, capture_output=True).returncode)
            self.assertEqual(raw, (recovery / "app.map").read_bytes())

    def test_pico_sdk_flags_allow_only_path_maps_not_project_warnings(self):
        text = (ROOT / "targets/rf_rp/CMakeLists.txt").read_text()
        self.assertEqual([], matrix_guard.pico_sdk_option_errors(text, "leshy2_rf_rp"))
        for extra in ("-Werror", "-std=c17", "-w"):
            broken = text.replace('"-fdebug-prefix-map=${LESHY2_REPO_ROOT}=."', f'"{extra}"')
            self.assertTrue(matrix_guard.pico_sdk_option_errors(broken, "leshy2_rf_rp"))


class TwoPassRunnerTest(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory) / "firmware"
        root.mkdir()
        _, matrix_path, matrix, evidence = evidence_fixture(root)
        (root / ".gitignore").write_text("/build/\n")
        (root / "config/f2_r2_build_qualification.json").write_text(json.dumps(evidence))
        (root / "targets").mkdir()
        (root / "targets/input.c").write_text("int input;\n")
        fixture_git(root, "add", ".")
        fixture_git(root, "commit", "-qm", "qualified input fixture")
        return root, matrix_path, matrix

    def fake_pass(self, matrix_path, matrix, environment, commit, root, recovery, number):
        build.require_pristine_build_roots(matrix, root)
        jobs, publications = [], []
        for target in matrix["targets"]:
            for configuration in build.CONFIGURATIONS:
                job_root = build.job_build_root(matrix, target["id"], configuration, root)
                for artifact in target["artifacts"]:
                    path = build.artifact_path(artifact["path"], job_root)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    data = b"tiny fixture image"
                    if artifact["kind"] in {"map", "boot_map"}:
                        data = b".text 0x1234 symbol " + str(root.resolve()).encode() + b"/source.o\n"
                        if target["id"] in {"pack", "safety"}:
                            data = b">> Linked test fixture wall clock\n" + data
                            sdk = recovery / f"sdk-maps/pass-{number}/{target['id']}/{configuration}/{path.name}"
                            sdk.parent.mkdir(parents=True, exist_ok=True)
                            sdk.write_bytes(data)
                            data = maps.ti_epoch_bytes(data, environment["SOURCE_DATE_EPOCH"])
                    path.write_bytes(data)
                publications.extend(repro.publish_job_maps(matrix, target, configuration, root, recovery, number, environment["SOURCE_DATE_EPOCH"]))
                jobs.append(build.verify_job(matrix, target, configuration, root))
        commands = build.evidence_command_rows(matrix, build.TARGET_IDS, build.CONFIGURATIONS, ("configure", "build"))
        for command in commands:
            command["status"] = "passed"
        qualification = build.qualification_evidence(matrix_path, matrix, jobs, commands, environment, commit, root)
        build.atomic_write(recovery / f"pass-{number}.json", repro.serialized(qualification))
        return {"number": number, "qualification": qualification, "map_publications": publications}

    def run_fixture(self, root, matrix_path, side_effect=None):
        with patch.object(build, "local_environment", return_value={}), patch.object(build, "preflight"), patch.object(repro, "run_pass", side_effect=side_effect or self.fake_pass) as mocked:
            record = repro.run(matrix_path, root)
        self.assertEqual([1, 2], [call.args[-1] for call in mocked.call_args_list])
        return record

    def test_two_real_fixture_passes_all_60_and_raw_32_verified(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, matrix_path, matrix = self.fixture(temporary)
            previous = (root / "config/f2_r2_build_qualification.json").read_bytes()
            record = self.run_fixture(root, matrix_path)
            self.assertEqual(60, len(record["comparisons"]))
            self.assertEqual(32, sum(len(row["map_publications"]) for row in record["passes"]))
            self.assertEqual([], repro.check_record(record, matrix_path, matrix, root))
            recovery = root.parent / "work" / record["recovery_directory"]
            self.assertEqual(previous, (recovery / "previous-f2_r2_build_qualification.json").read_bytes())
            self.assertTrue((recovery / "baseline-builds/build/r2/targets/rf_rp/debug/leshy2_rf_rp.bin").is_file())

    def test_failed_second_pass_keeps_previous_evidence_and_first_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, matrix_path, _ = self.fixture(temporary)
            previous = (root / "config/f2_r2_build_qualification.json").read_bytes()
            def fail_second(*args):
                if args[-1] == 2:
                    raise build.QualificationError("intentional test failure")
                return self.fake_pass(*args)
            with self.assertRaises(build.QualificationError):
                self.run_fixture(root, matrix_path, fail_second)
            self.assertEqual(previous, (root / "config/f2_r2_build_qualification.json").read_bytes())
            self.assertFalse((root / "config/f2_r2_reproducibility.json").exists())
            recovery = next((root.parent / "work").iterdir())
            self.assertTrue((recovery / "pass-1-builds/build/r2/targets/s3/debug/leshy2_s3.elf").exists())
            self.assertEqual("failed_not_published", json.loads((recovery / "failure.json").read_text())["status"])

    def test_second_canonical_write_failure_restores_previous_pair(self):
        for existing_repro in (False, True):
            with self.subTest(existing_repro=existing_repro), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / "config").mkdir()
                qualification = root / "config/f2_r2_build_qualification.json"
                result = root / "config/f2_r2_reproducibility.json"
                qualification.write_text('{"previous": "qualification"}\n')
                if existing_repro:
                    result.write_text('{"previous": "repro"}\n')
                before = {p: p.read_bytes() if p.exists() else None for p in (qualification, result)}
                original = build.atomic_write
                failed = False
                def fail_second(path, content):
                    nonlocal failed
                    if path == result and not failed:
                        failed = True
                        raise OSError("injected second-write error")
                    original(path, content)
                with patch.object(build, "atomic_write", side_effect=fail_second):
                    with self.assertRaisesRegex(build.QualificationError, "both previous records restored"):
                        repro.publish_records(root, {"new": "qualification"}, {"new": "repro"})
                for path, old in before.items():
                    self.assertEqual(old, path.read_bytes() if path.exists() else None)

    def test_failed_rollback_is_never_called_not_published(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config").mkdir()
            for name in ("f2_r2_build_qualification.json", "f2_r2_reproducibility.json"):
                (root / "config" / name).write_text("{}\n")
            original = build.atomic_write
            writes = 0
            def fail_after_first(path, content):
                nonlocal writes
                writes += 1
                if writes > 1:
                    raise OSError("injected continuing I/O failure")
                original(path, content)
            with patch.object(build, "atomic_write", side_effect=fail_after_first):
                with self.assertRaises(repro.PublicationRollbackError):
                    repro.publish_records(root, {"new": "qualification"}, {"new": "repro"})

    def test_byte_mismatch_refuses_publication_after_two_builds(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, matrix_path, _ = self.fixture(temporary)
            previous = (root / "config/f2_r2_build_qualification.json").read_bytes()
            def different_second(*args):
                result = self.fake_pass(*args)
                if args[-1] == 2:
                    artifact = result["qualification"]["jobs"][0]["artifacts"][0]
                    path = root / artifact["path"]
                    path.write_bytes(b"X" * artifact["bytes"])
                    artifact["sha256"] = build.sha256(path)
                return result
            with self.assertRaises(build.QualificationError):
                self.run_fixture(root, matrix_path, different_second)
            self.assertEqual(previous, (root / "config/f2_r2_build_qualification.json").read_bytes())
            self.assertFalse((root / "config/f2_r2_reproducibility.json").exists())

    def test_unknown_source_root_refuses_equal_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, matrix_path, _ = self.fixture(temporary)
            previous = (root / "config/f2_r2_build_qualification.json").read_bytes()
            def leaked(*args):
                result = self.fake_pass(*args)
                artifact = next(a for a in result["qualification"]["jobs"][0]["artifacts"] if a["path"].endswith(".elf"))
                path = root / artifact["path"]
                path.write_bytes(b"ELF\x00/unknownvendor/source/startup.c\x00")
                artifact.update({"bytes": path.stat().st_size, "sha256": build.sha256(path)})
                build.atomic_write(args[-2] / f"pass-{args[-1]}.json", repro.serialized(result["qualification"]))
                return result
            with self.assertRaisesRegex(build.QualificationError, "absolute source path"):
                self.run_fixture(root, matrix_path, leaked)
            self.assertEqual(previous, (root / "config/f2_r2_build_qualification.json").read_bytes())

    def test_plan_is_read_only_and_execution_requires_explicit_publication(self):
        evidence = ROOT / "config/f2_r2_build_qualification.json"
        before = evidence.read_bytes()
        runner = ROOT / "tools/review_f2_r2_reproducibility.py"
        result = subprocess.run([sys.executable, str(runner), "--plan"], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("60 artifacts", result.stdout)
        self.assertNotEqual(0, subprocess.run([sys.executable, str(runner), "--run"], capture_output=True).returncode)
        self.assertEqual(before, evidence.read_bytes())

    def test_elf_change_cannot_hide_behind_equal_distributables(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, matrix_path, matrix = self.fixture(temporary)
            record = self.run_fixture(root, matrix_path)
            elf = next(row for row in record["comparisons"] if row["path"].endswith(".elf"))
            (root / elf["path"]).write_bytes(b"X" * elf["bytes"])
            self.assertTrue(repro.check_record(record, matrix_path, matrix, root))

    def test_missing_map_raw_or_partial_inventory_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, matrix_path, matrix = self.fixture(temporary)
            record = self.run_fixture(root, matrix_path)
            changed = copy.deepcopy(record)
            changed["passes"][0]["map_publications"].pop()
            self.assertTrue(repro.check_record(changed, matrix_path, matrix, root))
            recovery = root.parent / "work" / record["recovery_directory"]
            raw = recovery / record["passes"][0]["map_publications"][0]["prepublication_map"]
            raw.write_bytes(b"tampered")
            self.assertTrue(repro.check_record(record, matrix_path, matrix, root))

    def test_build_inputs_changed_rejected_but_docs_only_descendant_allowed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, matrix_path, matrix = self.fixture(temporary)
            record = self.run_fixture(root, matrix_path)
            (root / "README.md").write_text("Docs only\n")
            fixture_git(root, "add", ".")
            fixture_git(root, "commit", "-qm", "docs and evidence")
            self.assertEqual([], repro.check_record(record, matrix_path, matrix, root))
            (root / "targets/input.c").write_text("int changed;\n")
            self.assertTrue(repro.check_record(record, matrix_path, matrix, root))

    def test_epoch_overclaim_and_recovery_escape_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, matrix_path, matrix = self.fixture(temporary)
            record = self.run_fixture(root, matrix_path)
            for key, value in (("source_date_epoch", "1"), ("recovery_directory", "../elsewhere"), ("passes", record["passes"][:1])):
                changed = copy.deepcopy(record)
                changed[key] = value
                self.assertTrue(repro.check_record(changed, matrix_path, matrix, root), key)
            changed = copy.deepcopy(record)
            changed["claims"]["runtime_boot_proven"] = True
            self.assertTrue(repro.check_record(changed, matrix_path, matrix, root))

    def test_recovery_refuses_symlink_build_root_without_moving_others(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, _, matrix = self.fixture(temporary)
            first = root / "build/r2/targets/s3/debug"
            safety = root / "build/r2/targets/safety/debug"
            moved = root / "build/r2/targets/safety/old-debug"
            safety.rename(moved)
            safety.symlink_to(moved, target_is_directory=True)
            with self.assertRaises(build.QualificationError):
                repro.move_build_roots(matrix, root.parent / "recovery", root)
            self.assertTrue(first.is_dir())


if __name__ == "__main__":
    unittest.main()
