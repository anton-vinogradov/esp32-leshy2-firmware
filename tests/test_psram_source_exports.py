"""PSRAM guards must work from versioned inputs, not ignored local defaults."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.test_s3_psram_probe_receipt import MANDATORY_SOURCES as S3_SOURCES


ROOT = Path(__file__).resolve().parents[1]
C5_SOURCES = {
    path.replace("s3", "c5").replace("partitions_16m.csv", "partitions_8m_c5.csv")
    for path in S3_SOURCES if "/leshy2_s3_c5/" not in path
}
SCOPED_SOURCES = S3_SOURCES | C5_SOURCES


def missing_index_inputs(index_paths):
    return sorted(SCOPED_SOURCES - set(index_paths))


class PsramSourceExportTests(unittest.TestCase):
    def test_guard_inputs_are_indexed_and_work_from_clean_index_export(self):
        # The Git index represents the commit candidate and works before/after
        # commit. Never populate this export by copying the working tree.
        listed = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        indexed = listed.decode().rstrip("\x00").split("\x00")
        self.assertEqual([], missing_index_inputs(indexed),
                         "Required PSRAM build inputs are not versioned; stage canonical defaults first")
        with tempfile.TemporaryDirectory() as temporary:
            exported = Path(temporary) / "clean-source"
            exported.mkdir()
            result = subprocess.run(
                ["git", "checkout-index", "--prefix=" + str(exported) + "/", "--", *sorted(SCOPED_SOURCES)],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            for path in SCOPED_SOURCES:
                self.assertTrue((exported / path).is_file(), path)
                self.assertEqual((ROOT / path).read_bytes(), (exported / path).read_bytes(),
                                 f"{path}: working tree differs from exported index; stage the reviewed input")
            for target, flash_mb, speed, mode in (("s3", 16, 80, "OCT"), ("c5", 8, 40, "QUAD")):
                with self.subTest(target=target):
                    project = exported / "targets" / target
                    defaults = (project / "sdkconfig.defaults").read_text()
                    # Synthetic effective Kconfig for a host-only guard test;
                    # this does not configure ESP-IDF or build a target.
                    values = dict(line.split("=", 1) for line in defaults.splitlines()
                                  if line.startswith("CONFIG_"))
                    values.update({"CONFIG_IDF_TARGET": f'"esp32{target}"',
                                   "CONFIG_ESPTOOLPY_FLASHSIZE": f'"{flash_mb}MB"',
                                   "CONFIG_SPIRAM_BOOT_HW_INIT": "y",
                                   f"CONFIG_SPIRAM_MODE_{mode}": "y",
                                   f"CONFIG_SPIRAM_SPEED_{speed}M": "y",
                                   "CONFIG_SPIRAM_SPEED": str(speed)})
                    config = Path(temporary) / f"{target}-resolved-sdkconfig"
                    config.write_text("\n".join(f"{key}={value}" for key, value in values.items()) + "\n")
                    result = subprocess.run([sys.executable, str(project / "verify_memory_config.py"),
                                             "--sdkconfig", str(config), "--components", "main", "esp_psram"],
                                            cwd=exported, capture_output=True, text=True)
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertIn("runtime checks remain open", result.stdout)

    def test_missing_c5_canonical_input_is_detected_even_if_local_file_exists(self):
        path = "config/sdkconfig.defaults.esp32c5"
        self.assertTrue((ROOT / path).is_file())
        self.assertEqual([path], missing_index_inputs(SCOPED_SOURCES - {path}))

    def test_s3_receipt_includes_the_exported_canonical_input(self):
        receipt = json.loads((ROOT / "config/f2_r2_s3_psram_probe.json").read_text())
        self.assertEqual(S3_SOURCES, set(receipt["sources"]))
        self.assertIn("config/sdkconfig.defaults.esp32s3", receipt["sources"])
        self.assertIn("config/sdkconfig.defaults.esp32c5", C5_SOURCES)


if __name__ == "__main__":
    unittest.main()
