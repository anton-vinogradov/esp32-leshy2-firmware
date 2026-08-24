import csv
import importlib.util
import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ProductSiteTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (REPO_ROOT / relative).read_text(encoding="utf-8")

    def test_public_site_is_small_and_bilingual(self):
        expected = {
            "README.md",
            "README.ru.md",
            "docs/architecture.md",
            "docs/architecture.ru.md",
            "docs/memory.md",
            "docs/memory.ru.md",
            "docs/roadmap.md",
            "docs/roadmap.ru.md",
            "docs/toolchains.md",
            "docs/toolchains.ru.md",
        }
        public_markdown = {
            str(path.relative_to(REPO_ROOT))
            for path in REPO_ROOT.glob("docs/**/*.md")
        } | {"README.md", "README.ru.md"}
        self.assertEqual(expected, public_markdown)

    def test_landing_pages_describe_capabilities_not_project_history(self):
        required = {
            "README.md": (
                "three nRF24", "`3R`", "`1T2R`", "`2T1R`", "`3T`",
                "spectrum waterfall", "Controlled Zone", "hardware `FAULT_KILL`",
                "signed", "owner",
            ),
            "README.ru.md": (
                "трёх nRF24", "`3R`", "`1T2R`", "`2T1R`", "`3T`",
                "спектральный водопад", "Контролируемая зона", "аппаратный `FAULT_KILL`",
                "подписаны", "владелец",
            ),
        }
        for name, tokens in required.items():
            page = self.read(name)
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")
            for forbidden in ("DEC-", "FND-", "REV-", "IMP-", "docs/status", "tree/main/docs/review"):
                self.assertNotIn(forbidden, page, name)

        self.assertIn("docs/roadmap.md", self.read("README.md"))
        self.assertIn("docs/roadmap.ru.md", self.read("README.ru.md"))
        landing_pages = {
            "README.md": ("Firmware roadmap and current position", "Firmware is at F2", "hardware H2"),
            "README.ru.md": ("Роадмап прошивки и текущая позиция", "Прошивка находится на F2", "hardware H2"),
        }
        for name, tokens in landing_pages.items():
            page = self.read(name)
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")
            for stage in range(12):
                self.assertIn(f"F{stage} ·", page, f"{name}: missing F{stage}")

    def test_firmware_roadmap_is_complete_and_honest(self):
        required = {
            "docs/roadmap.md": (
                "Current boundary: F2",
                "24 deterministic C scenarios",
                "not instruction-set, peripheral",
                "hardware H2",
                "hardware H7",
                "hardware H8",
            ),
            "docs/roadmap.ru.md": (
                "Текущая граница: F2",
                "24 детерминированных C-сценария",
                "не заменяет instruction-set",
                "hardware H2",
                "hardware H7",
                "hardware H8",
            ),
        }
        for name, tokens in required.items():
            page = self.read(name)
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")
            for stage in range(12):
                self.assertIn(f"F{stage}.", page, f"{name}: missing F{stage}")

    def test_current_firmware_substep_is_visible_and_synchronized(self):
        pages = ("README.md", "README.ru.md", "docs/roadmap.md", "docs/roadmap.ru.md")
        markers = {}
        for name in pages:
            page = self.read(name)
            found = re.findall(r"<!-- current-substep: (F\d+(?:\.\d+)+) -->", page)
            self.assertEqual(1, len(found), name)
            markers[name] = found[0]
            self.assertIn(f"`{found[0]}`", page, name)
            self.assertEqual(1, page.count(f"▶️ **`{found[0]}`"), name)
            self.assertIn("commit", page, name)

        self.assertEqual({"F2.4.0"}, set(markers.values()))
        state = json.loads(self.read("config/firmware_roadmap_state.json"))
        self.assertEqual("F2", state["phase"])
        self.assertEqual(next(iter(set(markers.values()))), state["current_substep"])
        self.assertIn("F2.0.1", state["reviewed"])
        self.assertFalse(state["claims"]["target_builds_run"])
        for name in ("README.md", "README.ru.md"):
            page = self.read(name)
            for substep in ("F2.0.0", "F2.0.1", "F2.0.2", "F2.0.3", "F2.1.0", "F2.3", "F2.5"):
                self.assertIn(f"`{substep}`", page, f"{name}: {substep}")

    def test_five_target_toolchain_matrix_is_exact_and_honest(self):
        matrix = json.loads(self.read("config/toolchain_matrix.json"))
        self.assertEqual("F2.0.1", matrix["stage"])
        self.assertEqual("reviewed", matrix["status"])
        self.assertEqual(5, len(matrix["targets"]))
        self.assertEqual(
            {"s3", "c5", "rp", "pack", "safety"},
            {target["domain"] for target in matrix["targets"]},
        )

        families = matrix["families"]
        self.assertEqual("v6.0.2", families["esp_idf"]["sdk"]["version"])
        self.assertEqual(
            "15.2.0_20251204",
            families["esp_idf"]["targets"]["s3"]["compiler_version"],
        )
        self.assertEqual(
            "15.2.0_20251204",
            families["esp_idf"]["targets"]["c5"]["compiler_version"],
        )
        self.assertEqual("2.3.0", families["pico_sdk"]["sdk"]["version"])
        self.assertEqual("rp2350-arm-s", families["pico_sdk"]["target"]["platform"])
        self.assertEqual(
            "15.2.Rel1", families["pico_sdk"]["target"]["compiler_version"]
        )
        self.assertEqual(
            "2.11.00.07", families["ti_mspm0_sdk"]["sdk"]["version"]
        )
        self.assertEqual(
            "4.0.5.LTS", families["ti_mspm0_sdk"]["compiler"]["version"]
        )
        self.assertEqual("1.28.x", families["ti_mspm0_sdk"]["host"]["sysconfig"])
        self.assertIn(
            "target configure or build", matrix["evidence_scope"]["not_yet_verified"]
        )

        for name in ("docs/toolchains.md", "docs/toolchains.ru.md"):
            page = self.read(name)
            for token in (
                "v6.0.2",
                "15.2.0_20251204",
                "2.3.0",
                "rp2350-arm-s",
                "15.2.Rel1",
                "2.11.00.07",
                "4.0.5.LTS",
                "F2.0.2",
                "F2.0.3",
            ):
                self.assertIn(token, page, f"{name}: {token}")
            for artifact in (
                "config/toolchain_matrix.json",
                "environment/toolchains.lock.json",
                "config/build_matrix.json",
                "config/source_layout.json",
                "tools/check_source_layout.py",
                "config/build_policy.json",
                "tools/check_build_policy.py",
                "config/f2_1_review.json",
                "tools/review_f2_1.py",
                "config/target_projects.json",
                "tools/check_target_projects.py",
                "config/f2_2_review.json",
                "tools/review_f2_2.py",
                "config/bsp_generation_input.json",
                "tools/validate_bsp_generation_input.py",
                "generated/source_manifest.json",
                "tools/generate_hardware_bsp.py",
                "config/bsp_target_consumption.json",
                "tools/check_bsp_target_consumption.py",
                "config/f2_3_review.json",
                "tools/review_f2_3.py",
            ):
                self.assertIn(artifact, page, f"{name}: {artifact}")
            for completed in ("F2.0.0", "F2.0.1", "F2.0.2", "F2.0.3", "F2.1.0"):
                self.assertIn(completed, page, f"{name}: {completed}")
            for substep in ("F2.1.1", "F2.1.2", "F2.2.0", "F2.2.1", "F2.2.2", "F2.2.3", "F2.2.4", "F2.2.5", "F2.3.0", "F2.3.1", "F2.3.2", "F2.3.3", "F2.4.0"):
                self.assertIn(substep, page, f"{name}: {substep}")

        lock = json.loads(self.read("environment/toolchains.lock.json"))
        self.assertEqual("F2.0.2", lock["stage"])
        self.assertEqual("reviewed", lock["status"])
        self.assertFalse(lock["policy"]["floating_versions_allowed"])
        self.assertEqual(
            {"linux_x86_64", "macos_arm64"}, set(lock["host_profiles"])
        )
        self.assertEqual(2, len(lock["source_revisions"]))
        self.assertEqual(26, len(lock["archives"]))
        self.assertTrue(
            all(len(archive["sha256"]) == 64 for archive in lock["archives"])
        )

    def test_runtime_architecture_has_five_physical_controllers(self):
        for name in ("docs/architecture.md", "docs/architecture.ru.md"):
            page = self.read(name).replace("‑", "-")
            for token in (
                "ESP32-S3-WROOM-1U-N16R8",
                "ESP32-C5-WROOM-1U-N8R8",
                "SC1512-A4",
                "MSPM0C1106SDGS20R",
                "TPS3435CAKAGDDFR",
                "1-bit SDIO",
                "SPI3",
            ):
                self.assertIn(token, page, f"{name}: {token}")

    def test_runtime_contract_preserves_non_interference(self):
        expected = {
            "docs/architecture.md": (
                "One top-level signal group is active at a time",
                "all three radios operate concurrently",
                "`BROADCAST_RX`",
                "`NONE` means every signal interface is quiet",
                "quiet state",
                "bounded quanta",
                "100 ms",
            ),
            "docs/architecture.ru.md": (
                "активна одна верхнеуровневая сигнальная группа",
                "три радио одновременно работают",
                "`BROADCAST_RX`",
                "`NONE` означает, что все сигнальные интерфейсы",
                "quiet-state",
                "ограниченные кванты",
                "100 мс",
            ),
        }
        for name, tokens in expected.items():
            page = " ".join(self.read(name).split())
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")

    def test_ui_controls_storage_audio_and_expansion_are_public(self):
        for name in ("README.md", "README.ru.md"):
            page = self.read(name)
            for token in ("D-pad", "`OK`", "`BACK`", "`OPT`", "`F1`", "`F2`", "microSD", "CTIA", "TRS"):
                self.assertIn(token, page, f"{name}: {token}")
        for name in ("docs/architecture.md", "docs/architecture.ru.md"):
            page = self.read(name).replace("‑", "-")
            for token in ("U214", "M5 Unit", "audio", "PTT", "RUN/KILL", "microSD", "SJ-43504-SMT-TR", "TCA9534APWR", "0x39", "slow_io.P02"):
                self.assertIn(token, page, f"{name}: {token}")

    def test_unattended_fault_contract_is_public(self):
        expected = {
            "docs/architecture.md": (
                "1.6-second timeout watchdog", "three NTC channels", "fault-viewer",
                "KILL`→`RUN", "automatic restart is never permitted",
            ),
            "docs/architecture.ru.md": (
                "timeout-watchdog", "три NTC", "fault viewer",
                "KILL`→`RUN", "автоматический restart запрещён",
            ),
        }
        for name, tokens in expected.items():
            page = " ".join(self.read(name).split())
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")

    def test_unattended_operation_policy_is_machine_readable_and_fail_closed(self):
        policy = json.loads(self.read("config/unattended_operation.json"))
        self.assertEqual("LESHY2-UNATTENDED-1", policy["contract_id"])
        self.assertEqual("none", policy["source_policy"]["runtime_claim"])
        self.assertEqual(
            {"minimum": 0, "maximum": 35},
            {
                key: policy["ambient_engineering_target_c"][key]
                for key in ("minimum", "maximum")
            },
        )

        setting = policy["full_self_test_setting"]
        self.assertEqual("EVERY_48_H", setting["default"])
        values = {value["id"]: value for value in setting["values"]}
        self.assertEqual(86400, values["EVERY_24_H"]["active_session_seconds"])
        self.assertEqual(172800, values["EVERY_48_H"]["active_session_seconds"])
        self.assertIsNone(values["STARTUP_ONLY"]["active_session_seconds"])
        self.assertFalse(values["STARTUP_ONLY"]["periodic_proof"])
        self.assertEqual("local physical UI only", setting["change_authority"])
        self.assertIn("KILL-to-RUN", setting["activation"])
        self.assertEqual("FAULT_PLANE_PROOF_DUE", setting["deadline_fault"])
        self.assertEqual(4, len(policy["non_configurable_safety"]))

    def test_update_model_preserves_owner_control(self):
        expected = {
            "docs/architecture.md": (
                "signed manifest", "inactive images", "last-known-good image",
                "locally enrolled owner root", "not enabled by default",
            ),
            "docs/architecture.ru.md": (
                "подписанный manifest", "inactive images", "предыдущему комплекту",
                "локально добавленный owner root", "по умолчанию не включаются",
            ),
        }
        for name, tokens in expected.items():
            page = self.read(name)
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")

    def test_large_s3_image_keeps_dual_slot_rollback(self):
        for name in ("docs/memory.md", "docs/memory.ru.md"):
            page = self.read(name)
            for token in (
                "ESP32-S3-WROOM-1U-N16R8", "0x700000", "ota_0", "ota_1",
                "0x6C0000", "ECC", "microSD", "rollback",
            ):
                self.assertIn(token, page, f"{name}: {token}")
            self.assertRegex(page, r"7[.,]5")

    def test_s3_production_defaults_make_ecc_non_optional(self):
        defaults = {
            line.strip()
            for line in self.read("config/sdkconfig.defaults.esp32s3").splitlines()
            if line.strip() and not line.startswith("#")
        }
        for required in (
            "CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y",
            "CONFIG_PARTITION_TABLE_CUSTOM=y",
            'CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="config/partitions_16m.csv"',
            "CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE=y",
            "CONFIG_SPIRAM=y",
            "CONFIG_SPIRAM_MODE_OCT=y",
            "CONFIG_SPIRAM_SPEED_80M=y",
            "CONFIG_SPIRAM_BOOT_INIT=y",
            "CONFIG_SPIRAM_ECC_ENABLE=y",
        ):
            self.assertIn(required, defaults)

        for name in ("docs/memory.md", "docs/memory.ru.md"):
            page = self.read(name)
            for token in ("CONFIG_SPIRAM_ECC_ENABLE=y", "0x780000", "self-test"):
                self.assertIn(token, page, f"{name}: {token}")

    def test_16m_partition_source_has_two_seven_mib_ota_slots(self):
        table_path = REPO_ROOT / "config/partitions_16m.csv"
        with table_path.open(encoding="utf-8", newline="") as source:
            rows = {
                row[0].strip(): {
                    "type": row[1].strip(),
                    "subtype": row[2].strip(),
                    "offset": int(row[3].strip(), 0),
                    "size": int(row[4].strip(), 0),
                    "flags": row[5].strip() if len(row) > 5 else "",
                }
                for row in csv.reader(
                    line for line in source if not line.lstrip().startswith("#")
                )
                if row
            }

        for slot, offset in (("ota_0", 0x030000), ("ota_1", 0x730000)):
            self.assertEqual("app", rows[slot]["type"])
            self.assertEqual(slot, rows[slot]["subtype"])
            self.assertEqual(offset, rows[slot]["offset"])
            self.assertEqual(0x700000, rows[slot]["size"])

        ordered = sorted(rows.values(), key=lambda row: row["offset"])
        for previous, current in zip(ordered, ordered[1:]):
            self.assertLessEqual(
                previous["offset"] + previous["size"], current["offset"]
            )
        self.assertEqual(0x1000000, ordered[-1]["offset"] + ordered[-1]["size"])
        self.assertEqual("encrypted", rows["nvs_keys"]["flags"])

    def test_c5_memory_inputs_keep_two_3_5_mib_ota_slots(self):
        defaults = {
            line.strip()
            for line in self.read("config/sdkconfig.defaults.esp32c5").splitlines()
            if line.strip() and not line.startswith("#")
        }
        for required in (
            "CONFIG_ESPTOOLPY_FLASHSIZE_8MB=y",
            "CONFIG_PARTITION_TABLE_CUSTOM=y",
            'CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="config/partitions_8m_c5.csv"',
            "CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE=y",
            "CONFIG_SPIRAM=y",
            "CONFIG_SPIRAM_BOOT_INIT=y",
        ):
            self.assertIn(required, defaults)

        with (REPO_ROOT / "config/partitions_8m_c5.csv").open(
            encoding="utf-8", newline=""
        ) as source:
            rows = {
                row[0].strip(): {
                    "offset": int(row[3].strip(), 0),
                    "size": int(row[4].strip(), 0),
                }
                for row in csv.reader(
                    line for line in source if not line.lstrip().startswith("#")
                )
                if row
            }
        for slot, offset in (("ota_0", 0x030000), ("ota_1", 0x3B0000)):
            self.assertEqual(offset, rows[slot]["offset"])
            self.assertEqual(0x380000, rows[slot]["size"])
        ordered = sorted(rows.values(), key=lambda row: row["offset"])
        for previous, current in zip(ordered, ordered[1:]):
            self.assertLessEqual(
                previous["offset"] + previous["size"], current["offset"]
            )
        self.assertEqual(0x800000, ordered[-1]["offset"] + ordered[-1]["size"])

        limits = json.loads(self.read("config/c5_image_limits.json"))
        self.assertEqual(0x380000, limits["slot_bytes"])
        self.assertEqual(0x300000, limits["warning_bytes"])
        self.assertEqual(0x360000, limits["maximum_image_bytes"])
        self.assertEqual(0x20000, limits["required_slot_margin_bytes"])

    def test_rp2354b_native_ab_tbyb_geometry_is_machine_readable(self):
        table = json.loads(self.read("config/rp2354b_partitions.json"))
        self.assertEqual([1, 0], table["version"])
        parts = table["partitions"]
        self.assertEqual(6, len(parts))
        self.assertEqual(0x2000, parts[0]["start"])
        self.assertEqual(["a", 0], parts[1]["link"])
        self.assertEqual(["owner", 0], parts[2]["link"])
        self.assertEqual(["a", 2], parts[3]["link"])
        self.assertEqual(["0x4c325250"], parts[2]["families"])
        self.assertEqual(parts[2]["families"], parts[3]["families"])

        def kib(value: str) -> int:
            self.assertTrue(value.endswith("K"))
            return int(value[:-1])

        self.assertEqual(2040, sum(kib(part["size"]) for part in parts))
        self.assertEqual(896, kib(parts[0]["size"]))
        self.assertEqual(896, kib(parts[1]["size"]))
        self.assertEqual(["0x4c32464c"], parts[4]["families"])
        self.assertEqual(["0x4c325256"], parts[5]["families"])
        limits = json.loads(self.read("config/rp2354b_image_limits.json"))
        self.assertEqual(0xE0000, limits["slot_bytes"])
        self.assertEqual(0xC0000, limits["warning_bytes"])
        self.assertEqual(0xD8000, limits["maximum_image_bytes"])
        self.assertEqual(0x8000, limits["required_slot_margin_bytes"])

        for name in ("docs/memory.md", "docs/memory.ru.md"):
            page = self.read(name)
            for token in (
                "IMAGE_DEF", "TBYB",
                "16.7" if name == "docs/memory.md" else "16,7",
                "explicit_buy()",
            ):
                self.assertIn(token, page, f"{name}: {token}")

    def test_two_c1106_images_have_exact_independent_ab_maps(self):
        memory = json.loads(self.read("config/mspm0c1106_memory.json"))
        self.assertEqual(0x10000, memory["flash_bytes"])
        self.assertEqual(0x2000, memory["sram_bytes"])
        self.assertEqual(0x5800, memory["slot_bytes"])
        self.assertEqual(0x5000, memory["warning_bytes"])
        self.assertEqual(0x5800, memory["maximum_image_bytes"])
        regions = memory["regions"]
        self.assertEqual(0, regions[0]["offset"])
        for previous, current in zip(regions, regions[1:]):
            self.assertEqual(previous["offset"] + previous["size"], current["offset"])
        self.assertEqual(0x10000, regions[-1]["offset"] + regions[-1]["size"])

        for name in ("docs/memory.md", "docs/memory.ru.md"):
            page = self.read(name)
            for token in (
                "MSPM0C1106SDGS20R", "0x4000", "0x5800", "0x9800", "0xF000",
                "UART1", "SWDIO/SWCLK",
            ):
                self.assertIn(token, page, f"{name}: {token}")

    def test_all_in_one_update_policy_is_open_and_fail_closed(self):
        policy = json.loads(self.read("config/update_policy.json"))
        self.assertIn("one Leshy2 bundle", policy["package"])
        self.assertEqual(
            {"release", "locally_enrolled_owner"},
            set(policy["signature_contract"]["accepted_roots"]),
        )
        self.assertIn("ECDSA P-256", policy["signature_contract"]["algorithm"])
        self.assertEqual(12000, policy["global_activation_deadline_ms"])
        self.assertIn("16.7-second", policy["deadline_basis"])
        self.assertFalse(
            policy["open_recovery"]["irreversible_secure_boot_or_debug_lock_default"]
        )
        self.assertTrue(
            policy["open_recovery"]["physical_owner_recovery_may_replace_keys_and_all_images"]
        )
        self.assertIn("physical RUN is in KILL", policy["preconditions"])
        self.assertIn("all TX evidence is quiet", policy["preconditions"])

    def test_interdomain_header_and_transports_are_exact(self):
        contract = json.loads(self.read("config/interdomain_protocol.json"))
        self.assertEqual("paper_reviewed", contract["review_status"])
        self.assertEqual("L2IP", contract["protocol"]["name"])
        self.assertEqual("0x3248534C", contract["protocol"]["magic_u32_le"])
        sources = {item["id"]: item for item in contract["sources"]}
        self.assertEqual(
            {
                "ESP32_C5_SDIO_DRIVER",
                "ESP32_C5_SDIO_SILICON",
                "RP2350_SPI_DMA",
                "M5_U214_PINMAP",
                "TCA9535_EVIDENCE_MASK",
                "SN74LVC1G07_EXT_EVIDENCE",
                "LESHY_LORA_CAP_01",
            },
            set(sources),
        )
        for source in sources.values():
            self.assertTrue(source["url"].startswith("https://"))

        header = contract["high_speed_header"]
        self.assertEqual(32, header["bytes"])
        cursor = 0
        for field in header["fields"]:
            self.assertEqual(cursor, field["offset"], field["name"])
            cursor += field["bytes"]
        self.assertEqual(header["bytes"], cursor)

        transports = {item["id"]: item for item in contract["transports"]}
        self.assertEqual({"S3_C5", "S3_RP", "S3_PACK", "S3_SAFETY"}, set(transports))
        for link in ("S3_C5", "S3_RP"):
            self.assertEqual(512, transports[link]["maximum_transfer_bytes"])
            self.assertEqual(480, transports[link]["maximum_payload_bytes"])
            self.assertGreaterEqual(
                transports[link]["qualified_payload_bytes_per_second_min"],
                1_500_000,
            )
        self.assertIn("revision v1.0-or-later", transports["S3_C5"]["physical"])
        self.assertIn("0x2A", transports["S3_PACK"]["physical"])
        self.assertIn("0x2B", transports["S3_SAFETY"]["physical"])

    def test_hardware_integration_contract_matches_firmware(self):
        boundary = json.loads(self.read("config/hardware_integration_contract.json"))
        bsp = json.loads(self.read("config/hardware_bsp_contract.json"))
        protocol = json.loads(self.read("config/interdomain_protocol.json"))
        self.assertEqual("LESHY2-HWFW-1", boundary["contract_id"])
        self.assertEqual(2, boundary["schema"])
        self.assertEqual("h2_0_3_reviewed", boundary["review_status"])
        self.assertEqual("LESHY2-H2-HWFW-1", bsp["export_id"])
        self.assertEqual("reviewed_hwfw_export", bsp["status"])
        self.assertEqual(boundary, bsp["integration_contract"])
        self.assertFalse(bsp["bsp"]["temporary_pin_assignments_allowed"])
        self.assertEqual(125, bsp["bsp"]["total_allocated_contacts"])
        self.assertEqual(
            {"S3": 33, "C5": 14, "RP": 48, "PACK": 13, "SAFETY": 17},
            {
                domain["domain"]: domain["allocated_contact_count"]
                for domain in bsp["bsp"]["domains"]
            },
        )
        service = boundary["physical_service"]
        self.assertEqual(3, len(service["external_usb"]))
        self.assertEqual(6, len(service["external_side_controls"]))
        self.assertEqual(3, len(service["internal_fallback_headers"]))
        self.assertEqual(
            boundary["protocol"],
            {
                "name": protocol["protocol"]["name"],
                "major": protocol["protocol"]["major"],
                "minor": protocol["protocol"]["minor"],
            },
        )

        transports = {row["id"]: row for row in protocol["transports"]}
        for row in boundary["transports"]:
            firmware = transports[row["id"]]
            for key in (
                "raw_bytes_per_second",
                "qualified_payload_bytes_per_second_min",
                "control_round_trip_ms_max",
                "alert_to_read_us_max",
            ):
                if key in row:
                    self.assertEqual(row[key], firmware[key], (row["id"], key))
            endpoints = [endpoint for pair in row["pins"].values() for endpoint in pair]
            self.assertEqual(len(endpoints), len(set(endpoints)), row["id"])

        groups = {row["name"]: row for row in protocol["signal_groups"]}
        for row in boundary["signal_groups"]:
            self.assertEqual(row["owner"], groups[row["firmware"]]["owner"])
            self.assertEqual(
                row["tx_evidence_bits"], groups[row["firmware"]]["evidence_bits"]
            )

        headset = boundary["audio_headset"]
        self.assertEqual("Same Sky SJ-43504-SMT-TR", headset["jack"]["mpn"])
        self.assertEqual("CTIA/AHJ", headset["jack"]["wiring"])
        self.assertEqual("slow_io.P02", headset["detect"]["endpoint"])
        self.assertEqual("input_only", headset["detect"]["direction"])
        self.assertIn("never configures P02 as an output", headset["detect"]["rule"])
        self.assertEqual("TCA9534APWR", headset["microphone_select"]["controller"])
        self.assertEqual("0x39", headset["microphone_select"]["i2c_address_7bit"])
        self.assertEqual(7, len(headset["microphone_select"]["reserve_endpoints"]))
        states = {row["state"]: row for row in headset["state_policy"]}
        self.assertEqual(
            {"ABSENT", "INSERTED_HEADSET", "INSERTED_INTERNAL_MIC", "UNKNOWN_OR_IO_FAULT"},
            set(states),
        )
        self.assertEqual("forced_off", states["UNKNOWN_OR_IO_FAULT"]["speaker"])

        timing_keys = {
            "heartbeat_period": "heartbeat_period_ms",
            "heartbeat_gap_max": "heartbeat_gap_ms_max",
            "tx_lease_lifetime_max": "tx_lease_lifetime_ms_max",
            "tx_lease_renew_period_max": "tx_lease_renew_period_ms_max",
            "unexpected_evidence_fault_max": "unexpected_evidence_fault_ms_max",
            "post_revoke_evidence_clear_grace": "post_revoke_evidence_clear_grace_ms",
            "safety_loop_period_max": "safety_loop_period_ms_max",
            "external_watchdog_timeout": "external_watchdog_timeout_ms",
            "external_watchdog_service_period_max": "external_watchdog_service_period_ms_max",
        }
        for boundary_key, firmware_key in timing_keys.items():
            self.assertEqual(
                boundary["safety_timing_ms"][boundary_key],
                protocol["safety_timing"][firmware_key],
            )

        profiles = {
            row["assembly"]: row for row in protocol["lora_cap_profiles"]["profiles"]
        }
        for row in boundary["lora_cap_profiles"]:
            self.assertEqual(row["module"], profiles[row["assembly"]]["module"])
            self.assertEqual(
                row["allowed_frequency_mhz"],
                profiles[row["assembly"]]["allowed_frequency_mhz"],
            )

    def test_interdomain_message_registry_is_unambiguous_and_proven(self):
        contract = json.loads(self.read("config/interdomain_protocol.json"))
        messages = contract["messages"]
        self.assertEqual(len(messages), len({item["id"] for item in messages}))
        self.assertEqual(len(messages), len({item["name"] for item in messages}))
        names = {item["name"] for item in messages}
        for item in messages:
            if "result_for" in item:
                self.assertIn(item["result_for"], names)
        for required in (
            "STATE_REQUEST", "STATE_RESULT", "QUIET_REQUEST", "QUIET_PROOF",
            "LEASE_SET", "LEASE_REVOKE", "STREAM_DATA", "CREDIT",
            "UPDATE_BEGIN", "UPDATE_CHUNK", "UPDATE_VERIFY",
            "UPDATE_ACTIVATE_PENDING", "BOOT_REPORT", "UPDATE_COMMIT",
            "UPDATE_ROLLBACK",
        ):
            self.assertIn(required, names)

        priorities = {item["id"]: item for item in contract["scheduling"]["priorities"]}
        self.assertFalse(priorities[0]["may_drop"])
        self.assertFalse(priorities[1]["may_drop"])
        self.assertTrue(priorities[3]["may_drop"])
        self.assertEqual("receiver credits; zero credit stops bulk without occupying a control queue", priorities[4]["flow_control"])

    def test_safety_mailbox_timing_closes_before_the_external_watchdog(self):
        contract = json.loads(self.read("config/interdomain_protocol.json"))
        mailbox = contract["i2c_mailbox"]
        self.assertEqual(32, mailbox["command_bytes"])
        self.assertEqual(64, mailbox["status_bytes"])
        self.assertEqual(128, mailbox["update_window_bytes"])
        self.assertEqual(108, mailbox["update_data_bytes"])

        timing = contract["safety_timing"]
        self.assertLess(timing["heartbeat_period_ms"], timing["heartbeat_gap_ms_max"])
        self.assertLessEqual(
            timing["tx_lease_renew_period_ms_max"],
            timing["tx_lease_lifetime_ms_max"],
        )
        self.assertLess(
            timing["heartbeat_gap_ms_max"],
            timing["external_watchdog_timeout_ms"],
        )
        self.assertLess(
            timing["external_watchdog_service_period_ms_max"],
            timing["external_watchdog_timeout_ms"],
        )
        self.assertTrue(timing["heartbeat_sequence_must_advance"])

    def test_every_enabled_tx_group_has_independent_evidence(self):
        contract = json.loads(self.read("config/interdomain_protocol.json"))
        groups = {item["name"]: item for item in contract["signal_groups"]}
        for name in ("S3_RF", "C5_RF", "NRF24", "CC1101", "VOICE", "IR", "LORA_CAP"):
            self.assertTrue(groups[name]["evidence_bits"], name)
        self.assertEqual([2, 3, 4], groups["NRF24"]["evidence_bits"])
        self.assertEqual(7, groups["LORA_CAP"]["id"])
        self.assertEqual([8], groups["LORA_CAP"]["evidence_bits"])
        self.assertIn("stock U214 receive and GNSS only", groups["LORA_CAP"]["tx_policy"])
        self.assertIn("LESHY2-LORA-CAP-01-EU868", groups["LORA_CAP"]["tx_policy"])
        self.assertEqual([], groups["M5_UNIT"]["evidence_bits"])
        self.assertIn("requires", groups["M5_UNIT"]["tx_policy"])
        self.assertEqual(9, groups["BROADCAST_RX"]["id"])
        self.assertEqual([], groups["BROADCAST_RX"]["evidence_bits"])
        self.assertIn("receive-only Si4732", groups["BROADCAST_RX"]["tx_policy"])
        evidence = contract["evidence_register"]
        self.assertEqual("TCA9535PWR", evidence["device"])
        self.assertEqual("0x20", evidence["i2c_7bit_address"])
        self.assertEqual(16, evidence["width_bits"])
        self.assertEqual(9, evidence["used_bits"])

    def test_exact_lora_cap_profiles_preserve_regional_and_evidence_bounds(self):
        contract = json.loads(self.read("config/interdomain_protocol.json"))
        cap = contract["lora_cap_profiles"]
        self.assertEqual("24AA02UIDT-I/OT", cap["identity_device"])
        self.assertFalse(cap["identity_is_authorization"])
        self.assertEqual(
            {"minimum": 10, "nominal": 14.6, "maximum": 18},
            cap["evidence_pulse_ms"],
        )
        profiles = {row["assembly"]: row for row in cap["profiles"]}
        self.assertEqual(
            {
                "LESHY2-LORA-CAP-01-EU868",
                "LESHY2-LORA-CAP-01-US915",
            },
            set(profiles),
        )
        self.assertEqual([848, 888], profiles["LESHY2-LORA-CAP-01-EU868"]["allowed_frequency_mhz"])
        self.assertEqual([900, 940], profiles["LESHY2-LORA-CAP-01-US915"]["allowed_frequency_mhz"])
        for profile in profiles.values():
            for gate in (
                "signed exact profile",
                "qualified UID binding",
                "active LORA_CAP lease",
                "live evidence bit 8",
            ):
                self.assertIn(gate, profile["tx_requires"])

    def test_public_architecture_explains_the_wire_contract(self):
        expected = {
            "docs/architecture.md": (
                "L2IP v1", "32-byte header", "512-byte", "0x2A", "0x2B",
                "50 ms", "100 ms", "ESP32-C5 revision v1.0",
            ),
            "docs/architecture.ru.md": (
                "L2IP v1", "32-байтный заголовок", "512-байт", "0x2A", "0x2B",
                "50 мс", "100 мс", "ESP32-C5 revision v1.0",
            ),
        }
        for name, tokens in expected.items():
            page = self.read(name)
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")

    def test_generic_image_checker_covers_every_physical_target(self):
        checker_path = REPO_ROOT / "tools/check_image_size.py"
        spec = importlib.util.spec_from_file_location("check_image_size", checker_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        self.assertEqual({"s3", "c5", "rp2354b", "pack", "safety"}, set(checker.TARGET_LIMITS))
        for target in checker.TARGET_LIMITS:
            limits = checker.load_limits(target)
            self.assertEqual("ok", checker.classify(int(limits["warning_bytes"]), limits))
            self.assertEqual(
                "warning", checker.classify(int(limits["warning_bytes"]) + 1, limits)
            )
            self.assertEqual(
                "reject", checker.classify(int(limits["maximum_image_bytes"]) + 1, limits)
            )

    def test_s3_image_size_checker_preserves_rollback_margin(self):
        limits = json.loads(self.read("config/s3_image_limits.json"))
        self.assertEqual(0x700000, limits["slot_bytes"])
        self.assertEqual(0x600000, limits["warning_bytes"])
        self.assertEqual(0x6C0000, limits["maximum_image_bytes"])
        self.assertEqual(
            limits["required_slot_margin_bytes"],
            limits["slot_bytes"] - limits["maximum_image_bytes"],
        )

        checker_path = REPO_ROOT / "tools/check_s3_image_size.py"
        spec = importlib.util.spec_from_file_location("check_s3_image_size", checker_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        self.assertEqual("ok", checker.classify(0x600000, limits))
        self.assertEqual("warning", checker.classify(0x600001, limits))
        self.assertEqual("warning", checker.classify(0x6C0000, limits))
        self.assertEqual("reject", checker.classify(0x6C0001, limits))

    def test_mermaid_diagram_is_bounded_and_has_no_combined_physical_owner(self):
        for name in ("README.md", "README.ru.md"):
            diagrams = re.findall(r"```mermaid\n(.*?)```", self.read(name), re.DOTALL)
            self.assertEqual(1, len(diagrams), name)
            diagram = diagrams[0]
            self.assertIn("flowchart TB", diagram, name)
            self.assertLess(len(diagram), 2000, name)
            for node in ("S3[", "C5[", "RP[", "PACK[", "SAFE[", "WDG["):
                self.assertEqual(1, diagram.count(node), f"{name}: {node}")

    def test_cross_repository_links_point_to_product_pages(self):
        for name in ("README.md", "README.ru.md", "docs/architecture.md", "docs/architecture.ru.md", "docs/memory.md", "docs/memory.ru.md"):
            page = self.read(name)
            self.assertIn("github.com/anton-vinogradov/esp32-leshy2", page, name)
            self.assertNotIn("/docs/review", page, name)

    def test_all_local_public_links_exist(self):
        for name in ("README.md", "README.ru.md", "docs/architecture.md", "docs/architecture.ru.md", "docs/memory.md", "docs/memory.ru.md", "docs/roadmap.md", "docs/roadmap.ru.md", "docs/toolchains.md", "docs/toolchains.ru.md"):
            page_path = REPO_ROOT / name
            page = page_path.read_text(encoding="utf-8")
            for target in re.findall(r"!?\[[^]]*\]\(([^)]+)\)", page):
                if target.startswith(("http://", "https://", "#")):
                    continue
                resolved = (page_path.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(resolved.exists(), f"{name}: missing {target}")

    def test_project_history_is_archived_outside_public_docs(self):
        archive = REPO_ROOT / "drafts/project-history-2026-08-19"
        self.assertTrue((archive / "architecture/ARC-0002-g2f-3i-runtime-input.md").is_file())
        self.assertTrue((archive / "status/current-state.md").is_file())
        self.assertTrue((archive / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
