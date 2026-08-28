import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "tools/check_r2_h2_sync_gate.py"
IMPORTER_PATH = ROOT / "tools/import_hardware_contract.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class R2H2SyncGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_module("check_r2_h2_sync_gate", CHECKER_PATH)
        cls.importer = load_module("import_hardware_contract", IMPORTER_PATH)
        cls.gate = json.loads((ROOT / "config/r2_h2_sync_gate.json").read_text())
        cls.h0 = json.loads((ROOT / "config/h0_r2_hardware_contract.json").read_text())
        cls.bsp = json.loads((ROOT / "config/hardware_bsp_contract.json").read_text())
        cls.integration = json.loads(
            (ROOT / "config/hardware_integration_contract.json").read_text()
        )

    def test_current_single_rp_h2_import_keeps_the_gate_closed(self):
        result = subprocess.run(
            [sys.executable, str(CHECKER_PATH)],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("R2/H2 sync gate CLOSED", result.stdout)
        self.assertFalse(self.gate["r2_h2_synchronized"])
        self.assertEqual([], self.checker.check(self.gate, self.h0, self.bsp, self.integration))

    def test_historical_markers_survive_every_import_write(self):
        raw = copy.deepcopy(self.bsp)
        raw.pop("authority")
        raw["integration_contract"].pop("authority")
        imported_bsp, imported_integration = self.importer.historical_outputs(raw)
        self.assertEqual(self.checker.HISTORICAL_BSP_AUTHORITY, imported_bsp["authority"])
        self.assertEqual(
            self.checker.HISTORICAL_INTEGRATION_AUTHORITY,
            imported_integration["authority"],
        )
        self.assertEqual(imported_integration, imported_bsp["integration_contract"])

    def test_false_synchronization_claim_is_rejected(self):
        gate = copy.deepcopy(self.gate)
        gate["r2_h2_synchronized"] = True
        gate["claims"]["six_domain_h2_export_available"] = True
        gate["claims"]["r2_h2_ecad_and_firmware_synchronized"] = True
        errors = self.checker.check(gate, self.h0, self.bsp, self.integration)
        self.assertIn(
            "R2/H2 synchronization claim does not match the candidate H2 export",
            errors,
        )

    def test_future_export_requires_six_domains_two_rps_and_exact_h0_m1(self):
        bsp = copy.deepcopy(self.bsp)
        integration = copy.deepcopy(self.integration)
        bsp["authority"] = {"baseline": "R2", "allowed_as_r2_authority": True}
        integration["authority"] = {"baseline": "R2", "allowed_as_r2_authority": True}
        domains = [
            {"id": row["id"], "mpn": row["mpn"]}
            for row in self.h0["domains"]
        ]
        bsp["bsp"]["domains"] = domains
        integration["controllers"] = copy.deepcopy(domains)
        bsp["integration_contract"] = copy.deepcopy(integration)
        bsp["r2_reconciliation"] = {
            "source_contract": "config/h0_r2_hardware_contract.json",
            "hardware_source_sha256": self.h0["hardware_source_sha256"],
            "domain_ids": self.checker.DOMAIN_IDS,
            "rp_domains": self.checker.RP_DOMAINS,
            "interboard": self.checker.expected_m1(self.h0),
        }
        self.assertTrue(self.checker.export_ready_for_r2(self.h0, bsp, integration))
        bsp["r2_reconciliation"]["interboard"]["pin_map"] = []
        self.assertFalse(self.checker.export_ready_for_r2(self.h0, bsp, integration))


if __name__ == "__main__":
    unittest.main()
