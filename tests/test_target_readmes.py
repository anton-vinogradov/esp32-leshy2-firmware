from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class TargetReadmeTests(unittest.TestCase):
    def test_target_readmes_are_product_sites_not_review_ledgers(self):
        for readme_name in ("README.md", "README.ru.md"):
            readme = (REPO_ROOT / readme_name).read_text(encoding="utf-8")
            for ledger_prefix in ("DEC-", "REV-", "FND-", "IMP-"):
                self.assertNotIn(ledger_prefix, readme, readme_name)
            self.assertNotIn("SN74LVC1G06", readme, readme_name)
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

    def test_target_readmes_keep_complete_local_controls(self):
        required_tokens = {
            "README.md": (
                "D-pad directions plus OK, BACK, OPT, F1, F2",
                "rotary encoder with push",
                "dedicated hold-to-talk PTT",
                "hardware STOP",
                "recessed RE-ARM",
                "interrupt-started 4×3 scan",
                "TCA9534APWR",
                "PCNT0 on GPIO39/GPIO47",
                "direct RP GPIO21 input",
                "Every ordinary position, including F1 and F2",
                "Panasonic AEQ10410",
                "pressing it or losing its connection stops",
                "do not replace any of them",
                "Sitronix ST77922",
                "I²C address `0x38`",
                "active-low IRQ",
                "SN74LVC1G07DCKR",
            ),
            "README.ru.md": (
                "направления D-pad и OK, BACK, OPT, F1, F2",
                "энкодер с нажатием",
                "отдельный PTT с удержанием",
                "аппаратный STOP",
                "утопленный RE-ARM",
                "сканирование 4×3",
                "TCA9534APWR",
                "PCNT0 на GPIO39/GPIO47",
                "прямой вход RP GPIO21",
                "Каждая обычная позиция, включая F1 и F2",
                "Panasonic AEQ10410",
                "нажатие, и потеря соединения",
                "не заменяют эти органы управления",
                "Sitronix ST77922",
                "I²C-адрес `0x38`",
                "active-low IRQ",
                "SN74LVC1G07DCKR",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            )
            for token in tokens:
                self.assertIn(token, normalized, f"{readme_name}: {token}")

    def test_consolidated_i4_runtime_contract_does_not_regress(self):
        for readme_name in ("README.md", "README.ru.md"):
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            )
            for token in (
                "TCA6424ARGJR",
                "`0x22`",
                "`0x2A`",
                "safe/degraded",
                "STOP/evidence",
            ):
                self.assertIn(token, normalized, f"{readme_name}: {token}")

        arc2 = " ".join((REPO_ROOT / "docs/architecture/ARC-0002-g2f-3i-runtime-input.md").read_text(encoding="utf-8").split())
        arc3 = " ".join((REPO_ROOT / "docs/architecture/ARC-0003-local-controls-runtime-contract.md").read_text(encoding="utf-8").split())
        for token in (
            "DEC-0089/IOX-0001",
            "TCA6424A address `0x22`",
            "pack target address `0x2A`",
            "low in RUN/high when latched",
            "full `3V3_MAIN` cycle",
        ):
            self.assertIn(token, arc2)
        for token in (
            "main `TCA6424ARGJR` responds at exact 7-bit address `0x22`",
            "pack admission responds at fixed firmware target `0x2A`",
            "P22 observes the AON STOP latch as low=RUN/high=latched STOP",
            "P23 observes S3 RF evidence as active low",
            "fixture-only `SLOW_IO_RESET_N`",
        ):
            self.assertIn(token, arc3)

    def test_target_readmes_keep_replaceable_cell_fail_closed_behavior(self):
        required_tokens = {
            "README.md": (
                "supervised 2s battery",
                "as one required pair",
                "blocks battery operation and charging",
                "cannot be overridden in software",
                "deeply discharged cell is refused",
                "no zero-volt/prequalification recovery command",
                "0.57-0.88 A for no more than 50 ms",
                "one non-retriggerable hardware channel",
                "at least 350 ms",
                "rejects a timer pulse shorter than 25 ms",
                "never presented as full-load qualification",
                "XTAR 18650 4000mAh",
                "28.8 Wh",
                "initially `0…45 °C`",
                "polarized `Keystone 1048P`",
                "raw flat-top cells are unsupported",
                "cannot infer cell authenticity from two contacts",
            ),
            "README.ru.md": (
                "контролируемая батарея 2s",
                "как одну обязательную пару",
                "блокируют работу от батареи и зарядку",
                "не могут быть обойдены программно",
                "глубоко разряженная банка отклоняется",
                "нет команды zero-volt/ prequalification recovery",
                "0,57-0,88 А не дольше 50 мс",
                "один non-retriggerable аппаратный канал",
                "минимум на 350 мс",
                "бракует импульс таймера короче 25 мс",
                "не выдаётся за полную проверку под нагрузкой",
                "XTAR 18650 4000mAh",
                "28,8 Вт·ч",
                "исходно `0…45 °C`",
                "поляризованном `Keystone 1048P`",
                "raw flat-top не поддерживаются",
                "не определяет подлинность банки по двум контактам",
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
                "hardware SafeMode",
                "protected VBUS path and charging remain off",
                "inactive EEPROM region",
                "Full-Speed data (12 Mbit/s)",
                "short-to-VBUS/ESD protection",
                "port fault closes the USB session",
                "Alt Mode is not supported",
            ),
            "README.ru.md": (
                "USB-C только принимает питание",
                "15 В/2 А",
                "никогда не включает 20 В",
                "аппаратный SafeMode",
                "Защищённый тракт VBUS и заряд остаются выключены",
                "неактивный регион EEPROM",
                "Full-Speed data S3 (12 Мбит/с)",
                "short-to-VBUS/ESD",
                "Ошибка порта закрывает USB session",
                "Alt Mode не поддерживается",
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
                "power-good evidence is qualified by its hardware enable",
                "intentionally disabled rail is normal",
                "bounded startup window fails closed",
                "current limit is active immediately during startup",
                "bounded `2.0 A` post-start transient",
                "never treating the transient timer as startup or continuous current budget",
                "only 85% of the negotiated input power as usable",
                "Missing power evidence, input-current limiting",
                "3.07-V supervisor threshold",
                "delayed hardware POR",
                "firmware cannot bypass startup",
                "independent overvoltage, current and short-circuit cutoff",
                "protected-side power-good evidence",
                "latched main trip needs a complete source-removal cycle",
                "bounded hardware recovery attempts",
            ),
            "README.ru.md": (
                "Always-on безопасность, вычислительные 3,3 В, голосовые 4,0 В",
                "раздельными фиксированными шинами",
                "отключаются, разряжаются и проверяются как тихие",
                "не может выбрать другое напряжение",
                "ошибка питания внешнего аксессуара защёлкивает",
                "не запускает automatic power-retry loop",
                "power-good голосовой шины и аксессуара аппаратно квалифицируется",
                "намеренно выключенная шина штатна",
                "за ограниченное стартовое окно, закрывается с ошибкой",
                "ограничение тока аксессуара действует немедленно при запуске",
                "ограниченный импульс `2,0 А` только после запуска",
                "transient timer не считается бюджетом запуска или постоянного тока",
                "доступными только 85% согласованной входной мощности",
                "При отсутствии достоверных данных о мощности",
                "порог supervisor 3,07 В",
                "delayed hardware POR",
                "firmware не может обойти стартовый порядок",
                "независимую отсечку перенапряжения, тока и короткого замыкания",
                "power-good защищённой стороны",
                "ошибки main требуется полное снятие источника",
                "ограниченные аппаратные попытки восстановления",
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
