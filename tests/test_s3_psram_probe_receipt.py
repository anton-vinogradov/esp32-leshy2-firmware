"""Validate a scoped public receipt, not locally unavailable ELF/binary bytes."""
import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "config/f2_r2_s3_psram_probe.json"
INPUT = "4a0088726dcdecf30de48e0f63e5d9678338716f"
ARTIFACTS = {"leshy2_s3.bin", "leshy2_s3.elf", "leshy2_s3.map", "bootloader/bootloader.bin",
             "bootloader/bootloader.elf", "bootloader/bootloader.map", "partition_table/partition-table.bin"}
PSRAM_OBJECTS = {
    "esp-idf/esp_psram/libesp_psram.a",
    "esp-idf/esp_psram/CMakeFiles/__idf_esp_psram.dir/system_layer/esp_psram.c.obj",
    "esp-idf/esp_psram/CMakeFiles/__idf_esp_psram.dir/esp32s3/esp_psram_impl_octal.c.obj",
}
MANDATORY_SOURCES = {
    "targets/s3/CMakeLists.txt", "targets/s3/main/CMakeLists.txt", "targets/s3/main/app_main.c",
    "targets/s3/verify_memory_config.py", "targets/s3/sdkconfig.defaults", "targets/s3/sdkconfig.debug",
    "config/sdkconfig.defaults.esp32s3", "config/partitions_16m.csv", "config/s3_image_limits.json",
    "environment/toolchains.lock.json", "generated/r2/hardware/src/s3_bsp.c",
    "generated/r2/hardware/include/leshy2/r2/hardware/s3_bsp.h",
    "generated/r2/hardware/include/leshy2/r2/hardware/bsp_types.h",
    "targets/s3/components/leshy2_portable/CMakeLists.txt",
    "targets/s3/components/leshy2_s3_c5/CMakeLists.txt",
    "targets/s3/components/leshy2_s3_c5/s3_c5_fake.c",
    "targets/s3/components/leshy2_s3_c5/include/leshy2/s3_c5_fake.h",
}
MANDATORY_SOURCES |= {f"common/{folder}/{name}.{extension}" for folder, extension in (
    ("src", "c"), ("include/leshy2", "h")) for name in (
        "l2ip", "update_core", "safety_core", "high_speed_adapter", "system_model", "receiver_core")}


def receipt_errors(receipt, source_reader=lambda path: (ROOT / path).read_bytes()):
    def exact(actual, expected):
        # JSON booleans and integer counters must not be interchangeable.
        return type(actual) is type(expected) and actual == expected

    errors = []
    if not exact(receipt.get("schema_version"), 1) or (
        receipt.get("status"), receipt.get("target"), receipt.get("configuration")) != (
        "passed_s3_debug_configure_and_build_only", "s3", "debug"):
        errors.append("S3 DEBUG configure/build-only identity changed")
    if receipt.get("input_commit") != INPUT:
        errors.append("probe must retain its actual input commit, not current HEAD")
    epoch = receipt.get("source_date_epoch")
    timestamp = receipt.get("input_commit_timestamp_utc", "")
    if not exact(epoch, 1788827863) or int(datetime.fromisoformat(timestamp).timestamp()) != epoch:
        errors.append("input commit/epoch timestamp mismatch")
    execution = receipt["execution"]
    for key, expected in {"clean_configure_runs": 1, "build_runs": 1, "configure_returncode": 0,
                          "build_returncode": 0, "network_or_downloads": False, "ccache_enabled": False}.items():
        if not exact(execution.get(key), expected):
            errors.append(f"invalid execution claim: {key}")
    times = [datetime.fromisoformat(execution[key]) for key in (
        "configure_started_utc", "configure_finished_utc", "build_started_utc", "build_finished_utc")]
    if times != sorted(times):
        errors.append("configure/build chronology is invalid")
    scope = receipt["scope"]
    if scope.get("source_snapshot_is_input_commit_not_current_head") is not True:
        errors.append("immutable input snapshot distinction is missing")
    for key in ("current_head_build_qualified", "full_matrix_qualified", "byte_reproducibility_proven",
                "physical_psram_capacity_measured", "psram_runtime_initialization_proven",
                "qualification_evidence_updated", "s3_release_build_run"):
        if scope.get(key) is not False:
            errors.append(f"unsupported scope claim: {key}")
    if not exact(scope.get("runtime_or_flash_runs"), 0):
        errors.append("runtime/flash cannot be inferred from compile")
    sources = receipt["sources"]
    if set(sources) != MANDATORY_SOURCES:
        errors.append("scoped S3 source inventory is incomplete or widened")
    for path, expected in sources.items():
        if path not in MANDATORY_SOURCES:
            continue  # An unexpected receipt path must never cause a filesystem read.
        data = source_reader(path)
        if expected != {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)} or not exact(expected.get("bytes"), len(data)):
            errors.append(f"current scoped S3 source differs from probe input: {path}")
    if set(receipt["artifacts"]) != ARTIFACTS:
        errors.append("artifact inventory is not the captured S3 application/boot set")
    if set(receipt["psram_compiled_objects"]) != PSRAM_OBJECTS:
        errors.append("compiled octal PSRAM object inventory is incomplete")
    for record in [*receipt["artifacts"].values(), *receipt["psram_compiled_objects"].values()]:
        if (not re.fullmatch(r"[0-9a-f]{64}", record.get("sha256", ""))
                or type(record.get("bytes")) is not int or record["bytes"] <= 0):
            errors.append("invalid captured artifact hash/size")
    config = receipt["configuration_evidence"]
    for key, expected in {"esp_psram_in_build_components": True, "configure_guard_passed": True,
                          "unknown_spiram_warnings": 0, "component_count": 53}.items():
        if not exact(config.get(key), expected):
            errors.append(f"configured component/guard proof missing: {key}")
    settings = config["settings"]
    for key, value in settings.items():
        expected_type = (int if key == "CONFIG_SPIRAM_SPEED" else str if key in (
            "CONFIG_ESPTOOLPY_FLASHSIZE", "CONFIG_PARTITION_TABLE_CUSTOM_FILENAME") else bool)
        if type(value) is not expected_type:
            errors.append(f"S3 resolved setting has wrong JSON type: {key}")
    for key, expected in {"CONFIG_SPIRAM": True, "CONFIG_SPIRAM_MODE_OCT": True,
                          "CONFIG_SPIRAM_MODE_QUAD": False, "CONFIG_SPIRAM_SPEED": 80,
                          "CONFIG_SPIRAM_ECC_ENABLE": True, "CONFIG_SPIRAM_BOOT_HW_INIT": True,
                          "CONFIG_SPIRAM_BOOT_INIT": True, "CONFIG_SPIRAM_IGNORE_NOTFOUND": False,
                          "CONFIG_ESPTOOLPY_FLASHSIZE": "16MB"}.items():
        if not exact(settings.get(key), expected):
            errors.append(f"S3 resolved setting differs: {key}")
    if "esp_psram_init" not in receipt["linked_defined_symbols"]:
        errors.append("ELF-defined PSRAM initialization symbol proof missing")
    lock = json.loads((ROOT / "environment/toolchains.lock.json").read_text())
    idf = next(row for row in lock["source_revisions"] if row["id"] == "esp-idf")
    if (receipt["environment_identity"]["esp_idf"], receipt["environment_identity"]["esp_idf_commit"]) != (
        idf["version"], idf["commit"]):
        errors.append("ESP-IDF identity differs from pinned lock")
    preservation = receipt["preservation"]
    for key, expected in {"tracked_and_retained_paths_checked": 450, "prior_declared_artifact_count": 60,
                          "changed_prior_artifacts_or_tracked_paths": [],
                          "scratch_sdkconfig_and_generated_config_unchanged_during_build": True}.items():
        if not exact(preservation.get(key), expected):
            errors.append(f"retained artifact/configuration preservation changed: {key}")
    gate = receipt["application_size_gate"]
    limits = json.loads((ROOT / "config/s3_image_limits.json").read_text())
    if gate.get("status") != "ok" or not exact(gate.get("size_bytes"), receipt["artifacts"]["leshy2_s3.bin"]["bytes"]):
        errors.append("application size result disagrees with artifact")
    if not 0 < gate.get("size_bytes", 0) <= limits["warning_bytes"]:
        errors.append("application is not within accepted warning threshold")
    for key in ("warning_bytes", "maximum_image_bytes", "slot_bytes"):
        if not exact(gate.get(key), limits[key]):
            errors.append(f"application memory gate changed: {key}")
    if not exact(receipt["diagnostics"].get("build_warning_count"), 0):
        errors.append("captured build warning count changed")
    text = json.dumps(receipt)
    if any(token in text for token in ("/Users/", "/private/", "/home/", "/Volumes/", "environment_whitelist", '"PATH"', '"argv"')):
        errors.append("private workstation path/environment exposed")
    return errors


class S3PsramProbeReceiptTests(unittest.TestCase):
    def setUp(self):
        self.receipt = json.loads(RECEIPT.read_text())

    def test_public_receipt_and_current_scoped_sources_match(self):
        self.assertEqual([], receipt_errors(self.receipt))

    def test_current_head_or_other_commit_cannot_replace_input(self):
        self.receipt["input_commit"] = "0" * 40
        self.assertIn("actual input commit", "\n".join(receipt_errors(self.receipt)))

    def test_wrong_epoch_is_rejected(self):
        self.receipt["source_date_epoch"] += 1
        self.assertIn("epoch", "\n".join(receipt_errors(self.receipt)))

    def test_runtime_repro_and_matrix_claims_rejected(self):
        for key in ("current_head_build_qualified", "full_matrix_qualified", "byte_reproducibility_proven",
                    "physical_psram_capacity_measured", "psram_runtime_initialization_proven"):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.receipt)
                changed["scope"][key] = True
                self.assertIn("unsupported scope", "\n".join(receipt_errors(changed)))

    def test_s3_source_drift_is_not_hidden_by_c5_only_changes(self):
        def changed(path):
            data = (ROOT / path).read_bytes()
            return data + b"\n" if path == "targets/s3/main/CMakeLists.txt" else data
        self.assertIn("current scoped S3 source differs", "\n".join(receipt_errors(self.receipt, changed)))

    def test_missing_source_or_artifact_is_rejected(self):
        self.receipt["sources"].pop("targets/s3/verify_memory_config.py")
        self.receipt["artifacts"].pop("leshy2_s3.map")
        errors = "\n".join(receipt_errors(self.receipt))
        self.assertIn("source inventory", errors)
        self.assertIn("artifact inventory", errors)

    def test_wrong_psram_mode_or_missing_elf_symbol_is_rejected(self):
        self.receipt["configuration_evidence"]["settings"]["CONFIG_SPIRAM_ECC_ENABLE"] = False
        self.receipt["linked_defined_symbols"].remove("esp_psram_init")
        errors = "\n".join(receipt_errors(self.receipt))
        self.assertIn("S3 resolved setting", errors)
        self.assertIn("symbol proof missing", errors)

    def test_path_leak_and_preservation_failure_are_rejected(self):
        self.receipt["private_path"] = "/Users/example/build"
        self.receipt["preservation"]["changed_prior_artifacts_or_tracked_paths"] = ["old.elf"]
        errors = "\n".join(receipt_errors(self.receipt))
        self.assertIn("workstation", errors)
        self.assertIn("preservation", errors)

    def test_bad_hash_and_relaxed_image_limit_are_rejected(self):
        self.receipt["artifacts"]["leshy2_s3.elf"]["sha256"] = "unknown"
        self.receipt["application_size_gate"]["maximum_image_bytes"] += 1
        errors = "\n".join(receipt_errors(self.receipt))
        self.assertIn("hash/size", errors)
        self.assertIn("memory gate", errors)

    def test_json_boolean_and_integer_types_are_not_interchangeable(self):
        for section, key, value in (
            ("execution", "build_runs", True), ("execution", "network_or_downloads", 0),
            ("configuration_evidence", "configure_guard_passed", 1),
            ("configuration_evidence", "unknown_spiram_warnings", False),
            ("preservation", "scratch_sdkconfig_and_generated_config_unchanged_during_build", 1),
            ("application_size_gate", "size_bytes", 165936.0),
        ):
            with self.subTest(section=section, key=key):
                changed = copy.deepcopy(self.receipt)
                changed[section][key] = value
                self.assertTrue(receipt_errors(changed))
        for key in ("CONFIG_SPIRAM_ECC_ENABLE", "CONFIG_SPIRAM_MEMTEST", "CONFIG_SPIRAM_TYPE_AUTO",
                    "CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE"):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.receipt)
                changed["configuration_evidence"]["settings"][key] = 1
                self.assertIn("S3 resolved setting", "\n".join(receipt_errors(changed)))

    def test_unknown_source_path_is_rejected_without_reading_it(self):
        self.receipt["sources"]["../../outside-source"] = {"sha256": "0" * 64, "bytes": 1}
        reads = []
        def safe_reader(path):
            self.assertIn(path, MANDATORY_SOURCES)
            reads.append(path)
            return (ROOT / path).read_bytes()
        self.assertIn("source inventory", "\n".join(receipt_errors(self.receipt, safe_reader)))
        self.assertEqual(MANDATORY_SOURCES, set(reads))


if __name__ == "__main__":
    unittest.main()
