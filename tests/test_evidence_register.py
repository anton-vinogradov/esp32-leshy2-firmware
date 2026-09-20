import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools import check_evidence_register as check


class EvidenceRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = check._crossings()
        cls.data = {key: cls.c.load(cls.c.ROOT / path) for key, path in cls.c.INPUTS.items()}
        cls.reviews = cls.c.semantics.reviewed_maps(
            [cls.c.load(path) for path in cls.c.semantics.MAPS], cls.data["material"]["groups"])
        cls.protocol = cls.c.load(check.PROTOCOL)
        cls.policy = cls.c.load(check.POLICY)

    def validate(self, data=None, protocol=None, policy=None, reviews=None):
        return check._validate(data if data is not None else self.data,
                               reviews if reviews is not None else self.reviews,
                               protocol if protocol is not None else self.protocol,
                               policy if policy is not None else self.policy)

    def test_current_fresh_binding_keeps_all_runtime_authority_open(self):
        result = check.build()
        self.assertEqual(("pass", []), (result["status"], result["errors"]))
        self.assertTrue(result["input_provenance_verified"])
        self.assertEqual(16, len(result["actual_mapping"]))
        for field in ("qualified", "full_EV_qualified", "runtime_driver_implemented", "gpio_modes_proven", "pull_modes_proven"):
            self.assertIs(result[field], False)
        self.assertEqual({str(p) for p in check.source_paths()}, set(result["source_sha256"]))
        mapping = {r["contact"]: r for r in result["actual_mapping"]}
        self.assertEqual((15, 12), (mapping["P17"]["raw_bit"], mapping["P17"]["logical_bit"]))
        self.assertEqual((10, None), (mapping["P12"]["raw_bit"], mapping["P12"]["logical_bit"]))

    def test_every_native_port_net_is_checked(self):
        for contact, _, _, _ in check.CONTACTS:
            with self.subTest(contact=contact):
                data = copy.deepcopy(self.data)
                row = next(r for r in data["nets"]["rows"] if r["instance"] == "evidence_mask" and r["contact"] == contact)
                row["net"] = "WRONG_NET"
                with self.assertRaises(ValueError):
                    self.validate(data=data)

    def test_missing_duplicate_and_extra_native_contacts_fail(self):
        for mutation in ("missing", "duplicate", "extra"):
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(self.data)
                row = next(r for r in data["nets"]["rows"] if r["instance"] == "evidence_mask" and r["contact"] == "P17")
                if mutation == "missing":
                    data["nets"]["rows"].remove(row)
                else:
                    extra = copy.deepcopy(row)
                    if mutation == "extra":
                        extra.update(contact="P18", endpoint="evidence_mask.P18")
                    data["nets"]["rows"].append(extra)
                with self.assertRaises((ValueError, KeyError)):
                    self.validate(data=data)

    def test_identity_physical_pad_and_review_mutations_fail(self):
        for mutation in ("reference", "device", "footprint", "pad", "physical", "type"):
            with self.subTest(mutation=mutation):
                data, reviews = copy.deepcopy(self.data), copy.deepcopy(self.reviews)
                part = next(r for r in data["instances"]["rows"] if r["instance"] == "evidence_mask")
                if mutation in {"reference", "footprint"}:
                    part[mutation] = "WRONG"
                elif mutation == "device":
                    part["device_id"] = "WRONG"
                elif mutation == "pad":
                    group = next(g for g in data["material"]["groups"] if g["device_id"] == "ti_tca9535_pwr")
                    next(r for r in group["contacts"] if r["contact"] == "P17")["pads"] = ["19"]
                elif mutation == "physical":
                    next(r for r in data["nets"]["rows"] if r["instance"] == "evidence_mask" and r["contact"] == "P17")["physical"] = "19"
                else:
                    reviews["ti_tca9535_pwr"]["pins"]["20"]["type"] = "input"
                with self.assertRaises((ValueError, KeyError)):
                    self.validate(data=data, reviews=reviews)

    def test_contract_mapping_drift_and_numeric_type_confusion_fail(self):
        mutations = {
            "old physical P12": lambda p: p["physical_binding"]["contacts"][-1].update(contact="P12"),
            "logical ABI": lambda p: p["physical_binding"]["contacts"][-1].update(logical_bit=15),
            "duplicate": lambda p: p["physical_binding"]["contacts"].append(p["physical_binding"]["contacts"][0]),
            "missing": lambda p: p["physical_binding"]["contacts"].pop(),
            "raw bool": lambda p: p["physical_binding"]["contacts"][1].update(raw_bit=True),
            "logical float": lambda p: p["physical_binding"]["contacts"][1].update(logical_bit=1.0),
            "claimed runtime": lambda p: p["physical_binding"].update(runtime_driver_implemented=True),
            "false number": lambda p: p["physical_binding"].update(gpio_modes_proven=0),
            "wrong input mask": lambda p: p["physical_binding"].update(required_input_mask="0xffff"),
            "raw ABI": lambda p: p.update(bit_numbering="raw_port"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                protocol = copy.deepcopy(self.protocol)
                mutate(protocol["evidence_register"])
                with self.assertRaises(ValueError):
                    self.validate(protocol=protocol)

    def test_policy_and_group_abi_remain_separate_from_raw_map(self):
        for field, value in (("input", "P12"), ("raw_bit", 12), ("bit", 15), ("polarity", "active_high")):
            policy = copy.deepcopy(self.policy)
            policy["nfc_reader"]["evidence"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate(policy=policy)
        protocol = copy.deepcopy(self.protocol)
        next(g for g in protocol["signal_groups"] if g["name"] == "U219_NFC")["evidence_bits"] = [15]
        with self.assertRaises(ValueError):
            self.validate(protocol=protocol)
        protocol = copy.deepcopy(self.protocol)
        protocol["signal_groups"].append(copy.deepcopy(protocol["signal_groups"][0]))
        with self.assertRaises(ValueError):
            self.validate(protocol=protocol)

    def test_stale_missing_and_duplicate_provenance_fail(self):
        original = self.c.load
        for mutation in ("stale", "missing", "extra"):
            data = copy.deepcopy(self.data["nets"])
            first = next(iter(data["sources"]))
            if mutation == "stale":
                data["sources"][first]["sha256"] = "0" * 64
            elif mutation == "missing":
                del data["sources"][first]
            else:
                data["sources"]["extra"] = copy.deepcopy(data["sources"][first])
            def load(path):
                return data if Path(path) == self.c.ROOT / self.c.INPUTS["nets"] else original(path)
            with self.subTest(mutation=mutation), mock.patch.object(self.c, "load", side_effect=load):
                result = check.build()
                self.assertEqual("fail", result["status"])
                self.assertFalse(result["input_provenance_verified"])

    def test_source_changes_during_build_fail(self):
        before = check._snapshot()
        with mock.patch.object(check, "_snapshot", side_effect=[before, {**before, "changed": "0" * 64}]):
            result = check.build()
        self.assertEqual("fail", result["status"])
        self.assertIn("changed during check", result["errors"][0])

    def test_missing_sibling_is_unqualified_not_pass(self):
        with mock.patch.object(check, "HW_ROOT", Path("/nonexistent-leshy2-hardware")):
            result = check.build()
        self.assertEqual("unqualified", result["status"])
        self.assertFalse(result["qualified"])

    def test_symlinked_or_foreign_consumed_source_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            link = Path(temporary) / "protocol.json"
            link.symlink_to(check.PROTOCOL)
            with mock.patch.object(check, "PROTOCOL", link):
                result = check.build()
                self.assertEqual("fail", result["status"])
                self.assertIn("symlinked", result["errors"][0])
            with mock.patch.object(check, "PROTOCOL", Path(temporary).resolve() / "absent.json"):
                self.assertEqual("fail", check.build()["status"])


if __name__ == "__main__":
    unittest.main()
