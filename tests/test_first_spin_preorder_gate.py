import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FirstSpinPreorderGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gate = json.loads(
            (ROOT / "config/first_spin_preorder_gate.json").read_text(encoding="utf-8")
        )

    def test_gate_is_fail_closed_and_targets_exactly_one_device(self):
        self.assertEqual("F-PO-R2", self.gate["gate_id"])
        self.assertEqual("planned_locked", self.gate["status"])
        boundary = self.gate["procurement_boundary"]
        self.assertEqual(1, boundary["assembled_device_quantity"])
        self.assertFalse(boundary["full_product_f6_f8_required_before_order"])
        self.assertIn("optional", boundary["factory_powered_function_test"])
        self.assertEqual("blocked", self.gate["order_authorization"]["status"])

    def test_every_required_first_spin_evidence_is_explicit_and_open(self):
        evidence = {row["id"]: row for row in self.gate["evidence_gates"]}
        self.assertEqual(
            {
                "FPO1_FINAL_HARDWARE_AUTHORITY",
                "FPO2_SIX_DIAGNOSTIC_IMAGES",
                "FPO3_S3_QEMU_DIAGNOSTIC",
                "FPO4_HOST_FAKE_HAL",
                "FPO5_TARGET_DEVELOPMENT_BOARDS",
                "FPO6_FLASH_RECOVERY_BUNDLE",
                "FPO7_OWNER_BRINGUP_SCRIPT",
            },
            set(evidence),
        )
        self.assertTrue(all(row["status"] != "reviewed" for row in evidence.values()))
        self.assertIn("H2/H6", evidence["FPO1_FINAL_HARDWARE_AUTHORITY"]["pass_rule"])
        self.assertIn("all six domains", evidence["FPO6_FLASH_RECOVERY_BUNDLE"]["pass_rule"])

    def test_f5_diagnostic_slice_is_a_hard_fail_closed_dependency(self):
        dependencies = {row["id"]: row for row in self.gate["hard_dependencies"]}
        self.assertIn("H6_R2_ROUTED_RELEASE_CANDIDATE", dependencies)
        self.assertNotIn("H6_R2_RELEASED_LAYOUT", dependencies)
        h6 = dependencies["H6_R2_ROUTED_RELEASE_CANDIDATE"]
        self.assertEqual("blocked", h6["status"])
        self.assertIn("immutable order release after F-PO closes", h6["required"])

        self.assertIn("F5_FIRST_SPIN_DIAGNOSTIC_DRIVERS", dependencies)
        f5 = dependencies["F5_FIRST_SPIN_DIAGNOSTIC_DRIVERS"]
        self.assertEqual("blocked", f5["status"])
        for token in ("every endpoint fitted", "fake-HAL", "smoke evidence"):
            self.assertIn(token, f5["required"])
        self.assertIn("complete product behavior is not required", f5["required"])

        evidence = {row["id"]: row["pass_rule"] for row in self.gate["evidence_gates"]}
        self.assertIn("every endpoint fitted", evidence["FPO2_SIX_DIAGNOSTIC_IMAGES"])
        self.assertIn("every endpoint fitted", evidence["FPO4_HOST_FAKE_HAL"])
        self.assertIn("every available target-development-board path", evidence["FPO5_TARGET_DEVELOPMENT_BOARDS"])

        roadmap = json.loads(
            (ROOT / "config/firmware_roadmap_state.json").read_text(encoding="utf-8")
        )["current_claims"]
        self.assertTrue(roadmap["first_spin_f5_diagnostic_slice_required"])
        self.assertFalse(roadmap["first_spin_f5_diagnostic_slice_reviewed"])
        self.assertFalse(roadmap["first_spin_every_fitted_endpoint_fake_hal_reviewed"])
        self.assertFalse(roadmap["first_spin_available_target_smoke_reviewed"])

    def test_docs_publish_same_order_boundary(self):
        pages = {
            "README.md": ("F-PO", "exactly one", "optional", "first full power-on", "every fitted endpoint"),
            "README.ru.md": ("F-PO", "ровно одного", "необязателен", "первое полное включение", "каждого установленного endpoint"),
            "docs/roadmap.md": ("F-PO", "exactly one", "FPO1", "FPO7", "every fitted endpoint"),
            "docs/roadmap.ru.md": ("F-PO", "ровно одного", "FPO1", "FPO7", "каждого установленного endpoint"),
        }
        for path, tokens in pages.items():
            text = (ROOT / path).read_text(encoding="utf-8")
            for token in tokens:
                self.assertIn(token, text, f"{path}: missing {token}")

    def test_emulation_boundary_remains_honest(self):
        boundary = self.gate["evidence_boundary"]
        self.assertTrue(any("S3 CPU" in row for row in boundary["preorder_can_prove"]))
        physical = " ".join(boundary["first_physical_prototype_still_proves"])
        for token in ("soldering", "signal integrity", "display flex", "RF matching"):
            self.assertIn(token, physical)


if __name__ == "__main__":
    unittest.main()
