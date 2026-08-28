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

    def current_candidate(self):
        h0 = copy.deepcopy(self.h0)
        h0["pre_h2_gates"] = []
        h0["physical_h1"]["status"] = "reviewed"
        h0["physical_h1"]["current_h1_blockers"] = []
        h0["physical_h1"]["pre_r2_h2_gates"] = []
        bsp = copy.deepcopy(self.bsp)
        integration = copy.deepcopy(self.integration)
        bsp["authority"] = {"baseline": "R2", "allowed_as_r2_authority": True}
        integration["authority"] = {"baseline": "R2", "allowed_as_r2_authority": True}
        domains = []
        for row in h0["domains"]:
            domain = {"id": row["id"], "mpn": row["mpn"]}
            exact = next(
                contract for contract in h0["domain_contracts"]
                if contract["id"] == row["id"]
            )
            domain["pin_map"] = copy.deepcopy(exact["pin_map"])
            domains.append(domain)
        bsp["bsp"]["domains"] = domains
        integration["controllers"] = copy.deepcopy(domains)
        reconciliation = self.checker.expected_reconciliation(h0)
        bsp["r2_reconciliation"] = copy.deepcopy(reconciliation)
        integration["r2_reconciliation"] = copy.deepcopy(reconciliation)
        bsp["integration_contract"] = copy.deepcopy(integration)
        return h0, bsp, integration

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

    def test_future_export_requires_exact_current_boundary_and_zero_gates(self):
        h0, bsp, integration = self.current_candidate()
        self.assertTrue(self.checker.export_ready_for_r2(h0, bsp, integration))

        mutations = {
            "S3 MPN": lambda h0, bsp, integration: bsp["bsp"]["domains"][0].update(mpn="WRONG"),
            "C5 MPN": lambda h0, bsp, integration: bsp["bsp"]["domains"][1].update(mpn="WRONG"),
            "Pack MPN": lambda h0, bsp, integration: bsp["bsp"]["domains"][4].update(mpn="WRONG"),
            "Safety MPN": lambda h0, bsp, integration: bsp["bsp"]["domains"][5].update(mpn="WRONG"),
            "S3 map": lambda h0, bsp, integration: bsp["bsp"]["domains"][0]["pin_map"].pop(),
            "C5 map": lambda h0, bsp, integration: bsp["bsp"]["domains"][1]["pin_map"].pop(),
            "hub map": lambda h0, bsp, integration: bsp["bsp"]["domains"][3]["pin_map"].pop(),
            "RF map": lambda h0, bsp, integration: bsp["r2_reconciliation"]["rear_pin_map"].pop(),
            "integration S3 map": lambda h0, bsp, integration: integration["controllers"][0]["pin_map"].pop(),
            "integration C5 MPN": lambda h0, bsp, integration: integration["controllers"][1].update(mpn="WRONG"),
            "integration hub map": lambda h0, bsp, integration: integration["controllers"][3]["pin_map"].pop(),
            "Pack map": lambda h0, bsp, integration: bsp["bsp"]["domains"][4]["pin_map"].pop(),
            "Safety map": lambda h0, bsp, integration: integration["controllers"][5]["pin_map"].pop(),
            "C5 mux": lambda h0, bsp, integration: bsp["r2_reconciliation"]["c5_sdio_service_mux"].clear(),
            "source hash": lambda h0, bsp, integration: bsp["r2_reconciliation"]["hardware_sources"].clear(),
            "M1": lambda h0, bsp, integration: bsp["r2_reconciliation"]["interboard"]["pin_map"].pop(),
            "open gate": lambda h0, bsp, integration: h0["pre_h2_gates"].append("open"),
            "physical H1 in progress": lambda h0, bsp, integration: h0["physical_h1"].update(status="in_progress"),
            "physical H1 blocker": lambda h0, bsp, integration: h0["physical_h1"]["current_h1_blockers"].append("open"),
            "physical pre-H2 gate": lambda h0, bsp, integration: h0["physical_h1"]["pre_r2_h2_gates"].append("open"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                candidate_h0, candidate_bsp, candidate_integration = self.current_candidate()
                mutate(candidate_h0, candidate_bsp, candidate_integration)
                self.assertFalse(
                    self.checker.export_ready_for_r2(
                        candidate_h0, candidate_bsp, candidate_integration
                    )
                )

    def test_integration_controllers_must_match_all_six_exact_domains(self):
        h0, bsp, integration = self.current_candidate()
        integration["controllers"][0]["pin_map"].pop()
        integration["controllers"][1]["mpn"] = "WRONG"
        bsp["integration_contract"] = copy.deepcopy(integration)
        self.assertFalse(self.checker.export_ready_for_r2(h0, bsp, integration))

    def test_exact_future_export_can_open_the_full_gate(self):
        h0, bsp, integration = self.current_candidate()
        gate = copy.deepcopy(self.gate)
        gate["status"] = "reviewed_six_domain_h2_export"
        gate["r2_h2_synchronized"] = True
        gate["claims"]["six_domain_h2_export_available"] = True
        gate["claims"]["r2_h2_ecad_and_firmware_synchronized"] = True
        self.assertEqual([], self.checker.check(gate, h0, bsp, integration))


if __name__ == "__main__":
    unittest.main()
