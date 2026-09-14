"""C5 DEBUG receipt/source integrity; never read local binaries or qualify hardware."""
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "config/f2_r2_c5_build_probe.json"
IDENTITY = {
    "schema_version": 1, "status": "passed_c5_debug_configure_and_build_only",
    "target": "c5", "configuration": "debug",
    "input_commit": "34ec1493f35aac15ad96f6ccb9a38fe1d7c4e5a6",
    "input_tree": "e84f2a1bf68ba18f8552c526f29d88c57dbf121f",
    "source_date_epoch": 1789349895, "captured_utc": "2026-09-14T01:46:32.999Z",
}
EXECUTION = {
    "clean_configure_runs": 1, "build_runs": 1, "configure_returncode": 0,
    "build_returncode": 0, "preflight_exact_checks": 20, "ccache_enabled": False,
    "dependency_downloads_disabled": True, "runtime_or_flash_runs": 0,
}
SCOPE = dict.fromkeys(("input_snapshot_not_moving_head", "isolated_tracked_tree_clean",
                      "toolchain_alias_only_untracked_item"), True)
SCOPE.update(dict.fromkeys(("full_matrix_qualified", "byte_reproducibility_proven",
    "psram_capacity_measured", "psram_runtime_initialization_proven",
    "service_recovery_qualified", "release_build_run", "production_release_allowed"), False))
SETTINGS = {
    "CONFIG_ESPTOOLPY_FLASHSIZE": "8MB", "CONFIG_SPIRAM": True,
    "CONFIG_SPIRAM_MODE_QUAD": True, "CONFIG_SPIRAM_SPEED": 40,
    "CONFIG_SPIRAM_ECC_ENABLE": False, "CONFIG_SPIRAM_BOOT_HW_INIT": True,
    "CONFIG_SPIRAM_BOOT_INIT": True, "CONFIG_SPIRAM_IGNORE_NOTFOUND": False,
    "CONFIG_SPIRAM_MEMTEST": True, "CONFIG_SPIRAM_USE_MALLOC": True,
}
SOURCES = {
    "config/c5_image_limits.json", "config/f2_r2_build_matrix.json",
    "config/partitions_8m_c5.csv", "config/sdkconfig.defaults.esp32c5",
    "environment/toolchains.lock.json",
    "generated/r2/hardware/include/leshy2/r2/hardware/bsp_types.h",
    "generated/r2/hardware/include/leshy2/r2/hardware/c5_bsp.h",
    "generated/r2/hardware/src/c5_bsp.c", "targets/c5/CMakeLists.txt",
    "targets/c5/components/leshy2_portable/CMakeLists.txt",
    "targets/c5/components/leshy2_s3_c5/CMakeLists.txt",
    "targets/c5/components/leshy2_s3_c5/include/leshy2/s3_c5_slave.h",
    "targets/c5/components/leshy2_s3_c5/s3_c5_slave.c",
    "targets/c5/main/CMakeLists.txt", "targets/c5/main/app_main.c",
    "targets/c5/sdkconfig.debug", "targets/c5/sdkconfig.defaults",
    "targets/c5/sdkconfig.release", "targets/c5/verify_memory_config.py",
    "tools/build_f2_r2_targets.py", "tools/review_f2_4_preflight.py",
    "tools/toolchain_preflight.py",
}
SOURCES |= {f"common/{folder}/{name}.{ext}" for folder, ext in (
    ("src", "c"), ("include/leshy2", "h")) for name in (
        "high_speed_adapter", "l2ip", "receiver_core", "safety_core", "system_model", "update_core")}
ARTIFACTS = {"leshy2_c5.bin", "leshy2_c5.elf", "leshy2_c5.map",
    "bootloader/bootloader.bin", "bootloader/bootloader.elf", "bootloader/bootloader.map",
    "partition_table/partition-table.bin"}
PSRAM_OBJECTS = {"esp-idf/esp_psram/libesp_psram.a",
    "esp-idf/esp_psram/CMakeFiles/__idf_esp_psram.dir/system_layer/esp_psram.c.obj",
    "esp-idf/esp_psram/CMakeFiles/__idf_esp_psram.dir/device/esp_psram_impl_ap_quad.c.obj"}
# Freeze the observed metadata, not a claim that CI can inspect or reproduce
# the uncommitted local artifacts. A coordinated receipt/source rebind fails.
RECORD_DIGESTS = {
    "sources": "37985677bae7027301523feb9aeca476799890c09bd5c61f8fed4139b20263d9",
    "artifacts": "4a2d2b7e2a10225ed08f843efd56d4ed494d4d31264850402b6069b804fd42f3",
    "psram_compiled_objects": "aab96c0850af4609779aa09c436b3a3bd51a82b418ffa79a136daec538f0012b",
}
HISTORY = {
    "config/f2_r2_build_qualification.json": {
        "sha256": "4857bb258cc1da5493c151c9950fe700502acb1d89d38ec7c58e49d3ba64d8a7", "bytes": 32019},
    "config/f2_5_reproducibility_review.json": {
        "sha256": "af60fae540a614091be1910236ac78733079cd5ffa147579b26e7e238d4f5196", "bytes": 9950},
    "config/f2_r2_s3_psram_probe.json": {
        "sha256": "6f14485556ba65f86584a0c3d90f5a5672cc31756ff4d96f5cb8bbc17bf40565", "bytes": 10432},
}
SIZE_GATE = {"status": "ok", "size_bytes": 143296, "maximum_image_bytes": 3538944,
             "warning_bytes": 3145728, "slot_bytes": 3670016}
DIAGNOSTICS = {
    "compiler_warning_count": 0,
    "wrapper_warning": "The isolated checkout uses a symlink to the same installed Python environment; IDF emits one lexical venv-path warning per invocation. Real paths are identical and the exact preflight passed. Not a compiler diagnostic.",
    "full_reproducibility_blocker": "Vendor-library DWARF build roots remain an open path-policy gate; this probe does not waive it.",
}
RETENTION = "Local isolated checkout retains binaries, maps, configuration and raw logs. CI checks this receipt and scoped input hashes, not unavailable local build artifacts."
SYMBOLS = {"esp_psram_" + name for name in (
    "check_ptr_addr", "chip_init", "extram_add_to_heap_allocator", "extram_reserve_dma_pool",
    "extram_test", "get_effective_mapped_size", "get_heap_size_to_protect", "impl_enable",
    "impl_get_available_size", "impl_get_cs_io", "impl_get_physical_size", "init",
    "io_get_cs_io", "is_initialized", "mspi_mb_init")}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def receipt_errors(receipt, source_reader=lambda path: (ROOT / path).read_bytes()):
    errors = []

    def exact(actual, expected, label):
        if type(actual) is not type(expected) or actual != expected:
            errors.append(f"{label}: value or JSON type differs")

    def mapping(value, keys, label):
        if type(value) is not dict:
            errors.append(f"{label}: expected object")
            return {}
        if set(value) != set(keys):
            errors.append(f"{label}: missing or unexpected keys")
        return value

    def fixed(value, expected, label):
        value = mapping(value, expected, label)
        for key, wanted in expected.items():
            exact(value.get(key), wanted, f"{label}.{key}")

    def record(value, label):
        value = mapping(value, {"sha256", "bytes"}, label)
        if type(value.get("sha256")) is not str or not re.fullmatch(r"[0-9a-f]{64}", value["sha256"]):
            errors.append(f"{label}: invalid sha256")
        if type(value.get("bytes")) is not int or value["bytes"] <= 0:
            errors.append(f"{label}: invalid byte size")
        return value

    sections = {"execution", "scope", "sources", "configuration_evidence", "artifacts",
        "psram_compiled_objects", "linked_defined_symbols", "application_size_gate",
        "historical_receipts_unchanged", "diagnostics", "evidence_retention"}
    receipt = mapping(receipt, set(IDENTITY) | sections, "receipt")
    for key, expected in IDENTITY.items():
        exact(receipt.get(key), expected, key)
    fixed(receipt.get("execution"), EXECUTION, "execution")
    fixed(receipt.get("scope"), SCOPE, "scope")
    records = {}
    for section, inventory in (("sources", SOURCES), ("artifacts", ARTIFACTS),
                               ("psram_compiled_objects", PSRAM_OBJECTS),
                               ("historical_receipts_unchanged", HISTORY)):
        entries = mapping(receipt.get(section), inventory, section)
        records[section] = entries
        if section in RECORD_DIGESTS and digest(entries) != RECORD_DIGESTS[section]:
            errors.append(f"{section}: captured metadata drift")
        for path in inventory & entries.keys():
            entry = record(entries[path], f"{section}.{path}")
            if section == "historical_receipts_unchanged":
                fixed(entry, HISTORY[path], f"historical identity: {path}")
            if section not in ("sources", "historical_receipts_unchanged"):
                continue  # CI must not read unavailable local build artifacts.
            try:
                data = source_reader(path)
            except (OSError, ValueError) as exc:
                errors.append(f"unreadable scoped input: {path} ({type(exc).__name__})")
                continue
            if type(data) is not bytes:
                errors.append(f"scoped reader did not return bytes: {path}")
            elif entry != {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}:
                errors.append(f"scoped input bytes differ: {path}")
    config = mapping(receipt.get("configuration_evidence"),
                     {"component_count", "esp_psram_in_build_components", "sdkconfig", "settings"}, "configuration")
    exact(config.get("component_count"), 51, "component_count")
    exact(config.get("esp_psram_in_build_components"), True, "PSRAM component")
    fixed(config.get("sdkconfig"), {
        "sha256": "a9ea05a62023a5feeb439a24d7e7e1955da83869279737dc357eef4f4123188f", "bytes": 60085}, "sdkconfig")
    fixed(config.get("settings"), SETTINGS, "settings")
    symbols = receipt.get("linked_defined_symbols")
    if (type(symbols) is not list or not all(type(s) is str for s in symbols)
            or len(symbols) != len(SYMBOLS) or set(symbols) != SYMBOLS):
        errors.append("linked PSRAM symbol inventory differs; esp_psram_init must be defined")
    fixed(receipt.get("application_size_gate"), SIZE_GATE, "application_size_gate")
    binary = records["artifacts"].get("leshy2_c5.bin")
    exact(binary.get("bytes") if type(binary) is dict else None, SIZE_GATE["size_bytes"], "application binary size")
    fixed(receipt.get("diagnostics"), DIAGNOSTICS, "diagnostics")
    exact(receipt.get("evidence_retention"), RETENTION, "evidence retention boundary")
    text = json.dumps(receipt)
    if (re.search(r"/(?:Users|private|home|Volumes|tmp|var|opt|mnt|workspace)/|[A-Za-z]:\\\\", text)
            or any(token in text for token in ('"PATH"', '"argv"', '"environment_whitelist"', "file://"))):
        errors.append("private workstation path/environment exposed")
    return errors


class C5BuildProbeReceiptTests(unittest.TestCase):
    def setUp(self):
        self.receipt = json.loads(RECEIPT.read_text())

    def test_current_receipt_and_exact_34_source_hashes_pass_without_artifact_reads(self):
        reads = []
        def reader(path):
            self.assertIn(path, SOURCES | HISTORY.keys())
            reads.append(path)
            return (ROOT / path).read_bytes()
        self.assertEqual(34, len(SOURCES))
        self.assertEqual([], receipt_errors(self.receipt, reader))
        self.assertCountEqual(SOURCES | HISTORY.keys(), reads)
        limits = json.loads((ROOT / "config/c5_image_limits.json").read_text())
        for key in ("maximum_image_bytes", "warning_bytes", "slot_bytes"):
            self.assertEqual(limits[key], SIZE_GATE[key])
        self.assertLess(SIZE_GATE["size_bytes"], SIZE_GATE["warning_bytes"])

    def test_input_snapshot_execution_and_scope_cannot_be_relabelled(self):
        for section, values in ((None, IDENTITY), ("execution", EXECUTION), ("scope", SCOPE)):
            for key, value in values.items():
                changed = copy.deepcopy(self.receipt)
                target = changed if section is None else changed[section]
                target[key] = not value if type(value) is bool else value + 1 if type(value) is int else "wrong"
                with self.subTest(section=section, key=key):
                    self.assertTrue(receipt_errors(changed))

    def test_source_hash_drift_and_coordinated_source_rebind_are_rejected(self):
        for path in SOURCES:
            changed = copy.deepcopy(self.receipt)
            changed["sources"][path]["sha256"] = "0" * 64
            with self.subTest(path=path):
                self.assertTrue(receipt_errors(changed))
        path = "targets/c5/main/app_main.c"
        changed_bytes = (ROOT / path).read_bytes() + b"\n"
        reader = lambda name: changed_bytes if name == path else (ROOT / name).read_bytes()
        self.assertIn(f"scoped input bytes differ: {path}", receipt_errors(self.receipt, reader))
        changed = copy.deepcopy(self.receipt)
        changed["sources"][path] = {"sha256": hashlib.sha256(changed_bytes).hexdigest(), "bytes": len(changed_bytes)}
        self.assertIn("sources: captured metadata drift", receipt_errors(changed, reader))

    def test_missing_data_wrong_containers_and_unknown_paths_fail_closed(self):
        for key in self.receipt:
            for action in ("missing", "wrong_type"):
                changed = copy.deepcopy(self.receipt)
                if action == "missing": changed.pop(key)
                else: changed[key] = [] if type(changed[key]) is dict else None
                with self.subTest(key=key, action=action):
                    self.assertTrue(receipt_errors(changed))
        for section in ("sources", "artifacts", "psram_compiled_objects", "historical_receipts_unchanged"):
            changed = copy.deepcopy(self.receipt)
            changed[section]["../../outside"] = {"sha256": "0" * 64, "bytes": 1}
            def reader(path):
                self.assertIn(path, SOURCES | HISTORY.keys())
                return (ROOT / path).read_bytes()
            with self.subTest(section=section):
                self.assertTrue(receipt_errors(changed, reader))

    def test_exact_artifact_sets_hashes_and_sizes_cannot_drift(self):
        for section in ("sources", "artifacts", "psram_compiled_objects", "historical_receipts_unchanged"):
            for path in self.receipt[section]:
                for key, value in (("sha256", "0" * 64), ("sha256", None), ("bytes", True), ("bytes", 0)):
                    changed = copy.deepcopy(self.receipt)
                    changed[section][path][key] = value
                    with self.subTest(section=section, path=path, key=key, value=value):
                        self.assertTrue(receipt_errors(changed))
                changed = copy.deepcopy(self.receipt)
                changed[section].pop(path)
                with self.subTest(section=section, missing=path):
                    self.assertTrue(receipt_errors(changed))

    def test_settings_size_and_json_boolean_integer_types_are_exact(self):
        cases = [("execution", EXECUTION), ("scope", SCOPE), ("application_size_gate", SIZE_GATE)]
        cases += [("settings", SETTINGS), ("configuration_evidence", {"component_count": 51, "esp_psram_in_build_components": True})]
        for section, values in cases:
            for key, expected in values.items():
                wrong = not expected if type(expected) is bool else expected + 1 if type(expected) is int else "wrong"
                for value in (None, 1 if type(expected) is bool else True, wrong):
                    changed = copy.deepcopy(self.receipt)
                    target = changed["configuration_evidence"]["settings"] if section == "settings" else changed[section]
                    target[key] = value
                    with self.subTest(section=section, key=key, value=value):
                        self.assertTrue(receipt_errors(changed))
        for key in SETTINGS:
            changed = copy.deepcopy(self.receipt)
            changed["configuration_evidence"]["settings"].pop(key)
            with self.subTest(missing=key): self.assertTrue(receipt_errors(changed))
        for value in (None, {}, {"sha256": "0" * 64, "bytes": 60085},
                      {"sha256": self.receipt["configuration_evidence"]["sdkconfig"]["sha256"], "bytes": True}):
            changed = copy.deepcopy(self.receipt)
            changed["configuration_evidence"]["sdkconfig"] = value
            with self.subTest(sdkconfig=value): self.assertTrue(receipt_errors(changed))

    def test_linked_init_diagnostics_and_private_paths_are_guarded(self):
        for change in ("missing_init", "duplicate_symbol", "unknown_claim", "warning", "prose", "private_posix", "private_windows"):
            changed = copy.deepcopy(self.receipt)
            if change == "missing_init": changed["linked_defined_symbols"].remove("esp_psram_init")
            elif change == "duplicate_symbol": changed["linked_defined_symbols"].append("esp_psram_init")
            elif change == "unknown_claim": changed["scope"]["runtime_qualified"] = True
            elif change == "warning": changed["diagnostics"]["compiler_warning_count"] = False
            elif change == "prose": changed["diagnostics"]["full_reproducibility_blocker"] = "qualified"
            else: changed["private_path"] = "/Users/example/build" if change == "private_posix" else r"C:\Users\example\build"
            with self.subTest(change=change):
                errors = receipt_errors(changed)
                self.assertTrue(errors)
                if change.startswith("private_"):
                    self.assertIn("private workstation path/environment exposed", errors)

    def test_three_old_receipts_cannot_be_changed_or_rebound(self):
        for path in HISTORY:
            data = (ROOT / path).read_bytes() + b"\n"
            reader = lambda name: data if name == path else (ROOT / name).read_bytes()
            changed = copy.deepcopy(self.receipt)
            changed["historical_receipts_unchanged"][path] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
            with self.subTest(path=path):
                self.assertIn(f"scoped input bytes differ: {path}", receipt_errors(self.receipt, reader))
                self.assertTrue(any("historical identity" in error for error in receipt_errors(changed, reader)))


if __name__ == "__main__":
    unittest.main()
