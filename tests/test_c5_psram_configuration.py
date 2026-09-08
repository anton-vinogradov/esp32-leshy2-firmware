"""C5-only host regressions; no target configure/build or local SDK required."""

import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "targets/c5/verify_memory_config.py"
spec = importlib.util.spec_from_file_location("c5_memory_config", SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class C5PsramConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.canonical = guard.parse_config(guard.CONTRACT_DEFAULTS.read_text())
        self.defaults = guard.parse_config((guard.PROJECT / "sdkconfig.defaults").read_text())
        self.config = dict(self.defaults)
        self.config.update({
            "CONFIG_IDF_TARGET": '"esp32c5"',
            "CONFIG_SPIRAM_BOOT_HW_INIT": "y",
            "CONFIG_SPIRAM_MODE_QUAD": "y",
            "CONFIG_SPIRAM_SPEED_40M": "y",
            "CONFIG_SPIRAM_SPEED": "40",
            "CONFIG_ESPTOOLPY_FLASHSIZE": '"8MB"',
        })
        self.components = ["main", "esp_psram", "esp_system"]

    def errors(self):
        return guard.configuration_errors(self.config, self.components, self.canonical, self.defaults)

    def test_current_contract_fixture_is_accepted(self):
        self.assertEqual([], self.errors())

    def test_explicit_component_dependency_is_unconditional(self):
        text = (guard.PROJECT / "main/CMakeLists.txt").read_text()
        declaration = re.search(r"idf_component_register\((.*?)\)", text, re.S)[1]
        without_comments = re.sub(r"#[^\n]*", "", declaration)
        self.assertIn("esp_psram", without_comments.split("PRIV_REQUIRES", 1)[1].split())
        self.assertNotRegex(text[:text.index("idf_component_register")], r"(?i)if\s*\(")

    def test_guard_runs_after_project_on_actual_sdkconfig_and_components(self):
        text = (guard.PROJECT / "CMakeLists.txt").read_text()
        self.assertLess(text.index("project(leshy2_c5)"), text.index("verify_memory_config.py"))
        for token in ("LESHY2_C5_SDKCONFIG SDKCONFIG", "LESHY2_C5_COMPONENTS BUILD_COMPONENTS",
                      "LESHY2_C5_PYTHON PYTHON", '--sdkconfig "${LESHY2_C5_SDKCONFIG}"',
                      "--components ${LESHY2_C5_COMPONENTS}", "message(FATAL_ERROR"):
            self.assertIn(token, text)

    def test_missing_component_rejected_even_with_enabled_flags(self):
        self.components.remove("esp_psram")
        self.assertIn("esp_psram is absent", "\n".join(self.errors()))

    def test_old_unknown_spiram_configuration_is_rejected(self):
        self.config = {key: value for key, value in self.config.items() if not key.startswith("CONFIG_SPIRAM")}
        self.assertIn("CONFIG_SPIRAM must be y", "\n".join(self.errors()))

    def test_each_required_flag_missing_or_disabled_is_rejected(self):
        for key in guard.REQUIRED_TRUE:
            for value in (None, "n"):
                with self.subTest(key=key, value=value):
                    original = self.config.pop(key)
                    if value is not None:
                        self.config[key] = value
                    self.assertIn(key, "\n".join(self.errors()))
                    self.config[key] = original

    def test_contract_or_target_defaults_cannot_silently_drop_malloc(self):
        for values in (self.canonical, self.defaults):
            with self.subTest(values=values):
                values["CONFIG_SPIRAM_USE_MALLOC"] = "n"
                self.assertIn("CONFIG_SPIRAM_USE_MALLOC", "\n".join(self.errors()))
                values["CONFIG_SPIRAM_USE_MALLOC"] = "y"

    def test_ignore_notfound_and_wrong_memory_interface_are_rejected(self):
        for key in guard.REQUIRED_FALSE:
            with self.subTest(key=key):
                self.config[key] = "y"
                self.assertIn(key, "\n".join(self.errors()))
                self.config.pop(key)

    def test_wrong_target_numeric_speed_flash_and_hw_init_are_rejected(self):
        for key, value in (("CONFIG_IDF_TARGET", '"esp32s3"'),
                           ("CONFIG_SPIRAM_SPEED", "120"),
                           ("CONFIG_SPIRAM_MODE_QUAD", "n"),
                           ("CONFIG_SPIRAM_SPEED_40M", "n"),
                           ("CONFIG_ESPTOOLPY_FLASHSIZE", '"16MB"'),
                           ("CONFIG_SPIRAM_BOOT_HW_INIT", "n")):
            with self.subTest(key=key):
                original = self.config[key]
                self.config[key] = value
                self.assertIn(key, "\n".join(self.errors()))
                self.config[key] = original

    def test_n8r8_bsp_leaves_in_package_psram_cs_gpio15_reserved(self):
        # Espressif C5 module datasheet v1.3, Table 1-2 and p15 note 3:
        # N8R8 module pad 19 GPIO15/SPICS1 belongs to its in-package PSRAM.
        contract = json.loads((ROOT / "config/f0_r2_target_identity_contract.json").read_text())
        c5 = next(row for row in contract["targets"] if row["id"] == "c5")
        self.assertEqual("ESP32-C5-WROOM-1U-N8R8", c5["mpn"])
        bsp = (ROOT / "generated/r2/hardware/src/c5_bsp.c").read_text()
        gpios = [int(value) for value in re.findall(r"\.gpio = INT16_C\((\d+)\)", bsp)]
        self.assertEqual(14, len(gpios))
        self.assertNotIn(15, gpios)

    def test_partition_paths_resolve_from_their_own_roots(self):
        self.assertNotEqual(self.canonical["CONFIG_PARTITION_TABLE_CUSTOM_FILENAME"],
                            self.defaults["CONFIG_PARTITION_TABLE_CUSTOM_FILENAME"])
        self.assertEqual([], self.errors())
        self.config["CONFIG_PARTITION_TABLE_CUSTOM_FILENAME"] = '"config/partitions_8m_c5.csv"'
        self.assertIn("custom partition", "\n".join(self.errors()))

    def test_parser_handles_generated_disabled_comments(self):
        self.assertEqual({"CONFIG_SPIRAM": "y", "CONFIG_SPIRAM_IGNORE_NOTFOUND": "n"},
                         guard.parse_config("# Generated\nCONFIG_SPIRAM=y\n# CONFIG_SPIRAM_IGNORE_NOTFOUND is not set\n"))

    def test_duplicate_and_malformed_lines_fail_closed(self):
        for text in ("CONFIG_SPIRAM=y\nCONFIG_SPIRAM=n", "CONFIG_SPIRAM=y\n# CONFIG_SPIRAM is not set", "bad config"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                guard.parse_config(text)

    def test_cli_uses_supplied_resolved_file_not_defaults(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "sdkconfig"
            for valid in (True, False):
                with self.subTest(valid=valid):
                    values = self.config if valid else self.defaults
                    path.write_text("\n".join(f"{key}={value}" for key, value in values.items()) + "\n")
                    result = subprocess.run([sys.executable, str(SCRIPT), "--sdkconfig", str(path),
                                             "--components", *self.components], capture_output=True, text=True)
                    self.assertEqual(0 if valid else 1, result.returncode, result.stdout + result.stderr)
                    if valid:
                        self.assertIn("runtime checks remain open", result.stdout)

    def test_cli_missing_file_is_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run([sys.executable, str(SCRIPT), "--sdkconfig", str(Path(temporary) / "absent"),
                                     "--components", "esp_psram"], capture_output=True, text=True)
            self.assertEqual(1, result.returncode)


if __name__ == "__main__":
    unittest.main()
