from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class TargetReadmeTests(unittest.TestCase):
    def test_target_readmes_are_product_sites_not_review_ledgers(self):
        for readme_name in ("README.md", "README.ru.md"):
            readme = (REPO_ROOT / readme_name).read_text(encoding="utf-8")
            for ledger_prefix in ("DEC-", "REV-", "FND-", "IMP-"):
                self.assertNotIn(ledger_prefix, readme, readme_name)
            for stale_heading in ("## Development state", "## Состояние разработки"):
                self.assertNotIn(stale_heading, readme, readme_name)
            self.assertIn("docs/status/current-state", readme, readme_name)

    def test_target_readmes_keep_the_finished_safety_flow(self):
        required_tokens = {
            "README.md": (
                "flowchart TD",
                "STOP",
                "Controlled Zone",
                "3R/1T2R/2T1R/3T",
                "actual-TX",
                "100 ms",
            ),
            "README.ru.md": (
                "flowchart TD",
                "STOP",
                "Контролируемая зона",
                "3R/1T2R/2T1R/3T",
                "actual-TX",
                "100 мс",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            )
            for token in tokens:
                self.assertIn(token, normalized, f"{readme_name}: {token}")

    def test_target_readmes_keep_replaceable_cell_fail_closed_behavior(self):
        required_tokens = {
            "README.md": (
                "supervised 2s battery",
                "as one required pair",
                "blocks battery operation and charging",
                "cannot be overridden in software",
                "deeply discharged cell is refused",
                "no zero-volt/prequalification recovery command",
            ),
            "README.ru.md": (
                "контролируемая батарея 2s",
                "как одну обязательную пару",
                "блокируют работу от батареи и зарядку",
                "не могут быть обойдены программно",
                "глубоко разряженная банка отклоняется",
                "нет команды zero-volt/ prequalification recovery",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            ).lower()
            for token in tokens:
                self.assertIn(token.lower(), normalized, f"{readme_name}: {token}")

    def test_target_readmes_keep_sink_only_pd_and_recovery_behavior(self):
        required_tokens = {
            "README.md": (
                "USB-C power is sink-only",
                "15 V/2 A",
                "never enables 20 V",
                "inactive EEPROM region",
            ),
            "README.ru.md": (
                "USB-C только принимает питание",
                "15 В/2 А",
                "никогда не включает 20 В",
                "неактивный регион EEPROM",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            ).lower()
            for token in tokens:
                self.assertIn(token.lower(), normalized, f"{readme_name}: {token}")

    def test_target_readmes_keep_fixed_separate_rail_behavior(self):
        required_tokens = {
            "README.md": (
                "Always-on safety, 3.3-V compute, 4.0-V voice",
                "separate fixed rails",
                "powered down, discharged and verified quiet",
                "cannot select another rail voltage",
                "external-accessory power fault latches",
                "never runs an automatic power-retry loop",
            ),
            "README.ru.md": (
                "Always-on безопасность, вычислительные 3,3 В, голосовые 4,0 В",
                "раздельными фиксированными шинами",
                "отключаются, разряжаются и проверяются как тихие",
                "не может выбрать другое напряжение",
                "ошибка питания внешнего аксессуара защёлкивает",
                "не запускает automatic power-retry loop",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            ).lower()
            for token in tokens:
                self.assertIn(token.lower(), normalized, f"{readme_name}: {token}")


if __name__ == "__main__":
    unittest.main()
