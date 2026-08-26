import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class F4AdapterContractTests(unittest.TestCase):
    def test_review_is_current_and_fail_closed(self):
        subprocess.run(
            [sys.executable, "tools/check_f4_adapter_contract.py"],
            cwd=REPO_ROOT,
            check=True,
        )
        contract = json.loads(
            (REPO_ROOT / "config/f4_0_1_adapter_contract.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("reviewed", contract["status"])
        self.assertEqual("F4.0.2", contract["next"])
        self.assertEqual(
            set(contract["common_lifecycle"]["states"]) - {"READY"},
            set(contract["common_lifecycle"]["side_effect_closed_states"]),
        )
        self.assertEqual(0, contract["high_speed_adapters"]["bulk_credit"]["initial_after_reset"])
        self.assertEqual(0, contract["counts"]["physical_transport_runs"])
        self.assertTrue(all(value is False for value in contract["authorization"].values()))

    def test_normalized_component_hash_ignores_zip_timestamps(self):
        sys.path.insert(0, str(REPO_ROOT / "tools"))
        try:
            from check_f4_adapter_contract import canonical_component_payload
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first.zip"
            second = Path(temporary) / "second.zip"
            for path, timestamp in ((first, (2024, 1, 1, 0, 0, 0)), (second, (2025, 2, 2, 2, 2, 2))):
                with zipfile.ZipFile(path, "w") as archive:
                    for name, content in (("component/a", b"A"), ("component/b", b"B")):
                        info = zipfile.ZipInfo(name, timestamp)
                        archive.writestr(info, content)
            self.assertEqual(
                canonical_component_payload(first),
                canonical_component_payload(second),
            )


if __name__ == "__main__":
    unittest.main()
