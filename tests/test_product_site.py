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

    def test_runtime_architecture_has_five_physical_controllers(self):
        for name in ("docs/architecture.md", "docs/architecture.ru.md"):
            page = self.read(name).replace("‑", "-")
            for token in (
                "ESP32-S3-WROOM-1U-N16R2",
                "ESP32-C5-WROOM-1U-N8R8",
                "SC1512-A4",
                "MSPM0C1104SDGS20R",
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
                "quiet state",
                "bounded quanta",
                "100 ms",
            ),
            "docs/architecture.ru.md": (
                "активна одна верхнеуровневая сигнальная группа",
                "три радио одновременно работают",
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
            for token in ("D-pad", "`OK`", "`BACK`", "`OPT`", "`F1`", "`F2`", "microSD"):
                self.assertIn(token, page, f"{name}: {token}")
        for name in ("docs/architecture.md", "docs/architecture.ru.md"):
            page = self.read(name).replace("‑", "-")
            for token in ("U214", "M5 Unit", "audio", "PTT", "RUN/KILL", "microSD"):
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

    def test_update_model_preserves_owner_control(self):
        expected = {
            "docs/architecture.md": ("signed target-bound images", "inactive slots", "rolls back", "Owner keys"),
            "docs/architecture.ru.md": ("подписанные target-bound images", "inactive slot", "rollback", "Ключи владельца"),
        }
        for name, tokens in expected.items():
            page = self.read(name)
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")

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
        for name in ("README.md", "README.ru.md", "docs/architecture.md", "docs/architecture.ru.md"):
            page = self.read(name)
            self.assertIn("github.com/anton-vinogradov/esp32-leshy2", page, name)
            self.assertNotIn("/docs/review", page, name)

    def test_all_local_public_links_exist(self):
        for name in ("README.md", "README.ru.md", "docs/architecture.md", "docs/architecture.ru.md"):
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
