import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class F2R2BspTest(unittest.TestCase):
    def test_generation_and_one_owner_consumption(self):
        result = subprocess.run(
            [sys.executable, "tools/check_f2_r2_bsp.py"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("6 deterministic H2-R2.1.5 domains and 173 exact rows", result.stdout)
        self.assertIn("0 target configure/build runs", result.stdout)

    def test_manifest_preserves_mapping_completeness(self):
        manifest = json.loads(
            (ROOT / "generated/r2/source_manifest.json").read_text(encoding="utf-8")
        )
        by_id = {row["id"]: row for row in manifest["domains"]}
        self.assertEqual(("exact_pins", 33), (by_id["s3"]["mapping"], by_id["s3"]["pins"]))
        self.assertEqual(("exact_pins", 14), (by_id["c5"]["mapping"], by_id["c5"]["pins"]))
        self.assertEqual(("exact_pins", 48), (by_id["rf_rp"]["mapping"], by_id["rf_rp"]["pins"]))
        self.assertEqual(("exact_pins", 48), (by_id["hub_rp"]["mapping"], by_id["hub_rp"]["pins"]))
        self.assertEqual(("exact_pins", 13), (by_id["pack"]["mapping"], by_id["pack"]["pins"]))
        self.assertEqual(("exact_pins", 17), (by_id["safety"]["mapping"], by_id["safety"]["pins"]))
        for target_id in by_id:
            self.assertRegex(by_id[target_id]["pin_contract_sha256"], r"^[0-9a-f]{64}$")

    def test_generation_is_byte_reproducible(self):
        result = subprocess.run(
            [sys.executable, "tools/generate_f2_r2_bsp.py", "--check"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)


if __name__ == "__main__":
    unittest.main()
