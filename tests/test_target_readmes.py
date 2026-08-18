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

    def test_exact_i5_audio_runtime_contract_does_not_regress(self):
        required_tokens = {
            "README.md": (
                "hardware bypass",
                "local microphone",
                "host-side VOX never imply PTT",
                "I²C readback at `0x19`",
                "Headphone insertion immediately disables",
                "address `0x11` or `0x63`",
                "independently authorized AON-gated PTT",
                "low-or-released, never high",
            ),
            "README.ru.md": (
                "аппаратный bypass",
                "локальный микрофон",
                "host-side VOX никогда не означают PTT",
                "I²C-readback на `0x19`",
                "Подключение наушников немедленно выключает",
                "адресе `0x11` либо `0x63`",
                "независимо разрешённого AON-gated PTT",
                "low-or-release",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            )
            for token in tokens:
                self.assertIn(token, normalized, f"{readme_name}: {token}")

        arc2 = " ".join(
            (REPO_ROOT / "docs/architecture/ARC-0002-g2f-3i-runtime-input.md")
            .read_text(encoding="utf-8")
            .split()
        )
        for token in (
            "DEC-0090/AUDIO-0003",
            "main slow plane is `23/0/1`",
            "P03/P04 are CC1101 rail-off band truth bits",
            "P05 remains free",
            "ES8311 `0x19`",
            "both public strap outcomes `0x11` and `0x63`",
            "P00 chooses either the selected RX source or exact local electret microphone",
            "VOX analysis never implies or requests PTT",
            "Module PTT has a physical RX pull-up",
            "H/L is driven low or released",
            "UPDATE is fixture-only",
        ):
            self.assertIn(token, arc2)

    def test_exact_i6_nrf_runtime_contract_does_not_regress(self):
        required_tokens = {
            "README.md": (
                "Three nRF24 paths retain independent PTX/PRX",
                "waits at least `100 ms`",
                "validates every radio",
                "all six digital directions",
                "three independent forward-power detectors",
            ),
            "README.ru.md": (
                "Три nRF24 сохраняют независимые PTX/PRX",
                "не менее `100 ms`",
                "проверяет каждый радиомодуль",
                "оба направления всех интерфейсов",
                "трёх независимых детекторов прямой мощности",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            )
            for token in tokens:
                self.assertIn(token, normalized, f"{readme_name}: {token}")

        arc2 = " ".join(
            (REPO_ROOT / "docs/architecture/ARC-0002-g2f-3i-runtime-input.md")
            .read_text(encoding="utf-8")
            .split()
        )
        for token in (
            "DEC-0091/N24E-0001",
            "waits at least 100 ms",
            "validates all three identities",
            "CE0/1/2 go low and CSN0/1/2 high",
            "DC2337J5010AHF`→`AD8314ACPZ-RL7",
            "channels 0, 100 and 125",
            "10-Mbit/s isolated SPI",
            "QOD/no-backpower",
            "Strong inbound RF may conservatively delay shutdown",
        ):
            self.assertIn(token, arc2)

    def test_exact_i6_native_runtime_contract_does_not_regress(self):
        required_tokens = {
            "README.md": (
                "Native S3 2.4-GHz and C5 2.4/5-GHz transmission",
                "separate directional actual-TX observations",
                "calibrated feed loss",
                "Strong inbound RF",
                "cannot authorize TX",
            ),
            "README.ru.md": (
                "Передача native S3 2,4 ГГц и C5 2,4/5 ГГц",
                "разные направленные actual-TX observations",
                "калиброванной потерей тракта",
                "Сильный входящий RF",
                "не может разрешить передачу",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            )
            for token in tokens:
                self.assertIn(token, normalized, f"{readme_name}: {token}")

        arc2 = " ".join(
            (REPO_ROOT / "docs/architecture/ARC-0002-g2f-3i-runtime-input.md")
            .read_text(encoding="utf-8")
            .split()
        )
        for token in (
            "DEC-0092/NAT-0001",
            "`s3_native_24`",
            "`c5_native`",
            "C5 uses ANT1 only",
            "ANT2 is not a profile",
            "module→jumper→PCB mate→coupler→chassis feed",
            "disables the affected TX profile",
            "cannot create, extend or validate a transmit lease",
            "cannot wait for a display refresh",
        ):
            self.assertIn(token, arc2)

    def test_exact_i6_cc1101_runtime_contract_does_not_regress(self):
        required_tokens = {
            "README.md": (
                "CC1101 exposes separate 315-MHz, 433-MHz and combined 868/915-MHz",
                "Two `BGS13SN8E6327XTSA1` switches isolate",
                "code `00` is safe isolation",
                "band changes only with CC power off",
                "Final-line `AD8314ACPZ-RL7` evidence",
                "never grants transmission",
            ),
            "README.ru.md": (
                "CC1101 даёт раздельные аппаратные endpoints 315 МГц, 433 МГц",
                "Два `BGS13SN8E6327XTSA1` изолируют",
                "код `00` означает безопасную изоляцию",
                "Диапазон меняется только при снятом питании CC",
                "Final-line evidence на `AD8314ACPZ-RL7`",
                "никогда не разрешает передачу",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            )
            for token in tokens:
                self.assertIn(token, normalized, f"{readme_name}: {token}")

        arc2 = " ".join(
            (REPO_ROOT / "docs/architecture/ARC-0002-g2f-3i-runtime-input.md")
            .read_text(encoding="utf-8")
            .split()
        )
        for token in (
            "DEC-0093/CCRF-0001",
            "`cc_315` uses V1/V2=`10` and RF1",
            "`cc_433` uses `01` and RF2",
            "`cc_868_915` uses `11` and RF3",
            "V1/V2=`00` is isolation",
            "S3 is the sole writer of TCA6424A P03/P04",
            "`BAND_PRESELECTED` only after RP reports `CC_OFF/EVIDENCE_QUIET`",
            "No powered-state P03/P04 write is valid",
            "GJM1555C1HR47BB01D`→`AD8314ACPZ-RL7",
            "`unexpected_rf`, never authorization",
            "CC315/433/868/915 cold band entry",
        ):
            self.assertIn(token, arc2)

    def test_exact_i6_sa518_rf_runtime_contract_does_not_regress(self):
        required_tokens = {
            "README.md": (
                "SA518 voice exposes separate VHF and UHF profiles",
                "one direct protected 50-Ohm external feed",
                "binds channel, H/L power, region",
                "Final-line `AD8314ACPZ-RL7` evidence",
                "missing evidence revokes PTT",
                "never creates or extends a lease",
            ),
            "README.ru.md": (
                "SA518 voice даёт раздельные VHF и UHF profiles",
                "один direct protected 50-Ом внешний тракт",
                "связывает channel, H/L power, region",
                "Final-line evidence на `AD8314ACPZ-RL7`",
                "missing evidence снимает PTT",
                "никогда не создаёт и не продлевает lease",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            )
            for token in tokens:
                self.assertIn(token, normalized, f"{readme_name}: {token}")

        arc2 = " ".join(
            (REPO_ROOT / "docs/architecture/ARC-0002-g2f-3i-runtime-input.md")
            .read_text(encoding="utf-8")
            .split()
        )
        for token in (
            "DEC-0094/VRF-0001",
            "physical ANT contact 7",
            "exact 5.1-kOhm/52.3-Ohm attenuation",
            "until then P05 remains free",
            "`voice_vhf` or `voice_uhf`",
            "arms the evidence hold before the protected 4-V rail",
            "`external_rf_present`",
            "RC0402FR-075K1L` + `RC0402FR-0752R3L",
            "measured conducted failure reopens",
        ):
            self.assertIn(token, arc2)

    def test_exact_i6_ir_runtime_contract_does_not_regress(self):
        required_tokens = {
            "README.md": (
                "IR learning captures the robust active-low 38-kHz envelope",
                "`TSOP95238TT`",
                "`TSMP95000TT`",
                "`VSMY14940` emitter is dark by reset and hard STOP",
                "`VEMD1060X01` plus `TLV9061IDBVR` observes real emitted light",
                "ambient light can only delay quiet and never authorizes it",
            ),
            "README.ru.md": (
                "IR-learning одновременно получает устойчивую active-low огибающую 38 кГц",
                "`TSOP95238TT`",
                "`TSMP95000TT`",
                "излучатель `VSMY14940` тёмный при reset и hard STOP",
                "`VEMD1060X01` и `TLV9061IDBVR` наблюдают реальный свет",
                "внешняя засветка может только задержать quiet и никогда не даёт разрешение",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            )
            for token in tokens:
                self.assertIn(token, normalized, f"{readme_name}: {token}")

        arc2 = " ".join(
            (REPO_ROOT / "docs/architecture/ARC-0002-g2f-3i-runtime-input.md")
            .read_text(encoding="utf-8")
            .split()
        )
        for token in (
            "DEC-0095/IRF-0001",
            "GPIO0/RMT RX0",
            "GPIO1/RMT RX1",
            "carrier provenance to `measured`",
            "GPIO4 `IR_FRONTEND_PWR_EN`",
            "`RC1206FR-0733RL`/`DMN2056U-7`",
            "GPIO24 is active-low physical optical evidence",
            "evidence never creates or extends permission",
            "`IR_QUIET` therefore means discharged RX power",
            "IEC 62471",
        ):
            self.assertIn(token, arc2)

    def test_exact_i6_si4732_dual_input_runtime_contract_does_not_regress(self):
        required_tokens = {
            "README.md": (
                "`Si4732-A10-GSR` keeps four receive modes on two immutable ports",
                "FM/SW uses the protected FMI path",
                "non-50-Ohm short loop-pod path",
                "2.3–25-MHz SW region",
                "no RF switch or transmitter",
                "arbitrary long coax is not a qualified AM/LW accessory",
            ),
            "README.ru.md": (
                "`Si4732-A10-GSR` сохраняет четыре RX-режима на двух неизменных портах",
                "FM/SW работает через защищённый FMI",
                "не-50-Ом порт короткого loop-пода",
                "SW 2,3–25 МГц",
                "нет RF switch или передатчика",
                "произвольный длинный коаксиал",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            )
            for token in tokens:
                self.assertIn(token, normalized, f"{readme_name}: {token}")

        arc2 = " ".join(
            (REPO_ROOT / "docs/architecture/ARC-0002-g2f-3i-runtime-input.md")
            .read_text(encoding="utf-8")
            .split()
        )
        for token in (
            "DEC-0096/RXF-0001",
            "physical contact 6 `FMI`",
            "Physical contact 8 `AMI`",
            "Contact 7 is the short local RF return",
            "SW-on-AMI example is Si4734/35-only",
            "No RF switch or TX path exists",
            "`rx_fm` | `rx_fmsw_fmi` | 64–108 MHz",
            "`rx_sw` | `rx_fmsw_fmi` | 2.3–26.1 MHz",
            "`rx_am` | `rx_amlw_ami` | 520–1710 kHz",
            "`rx_lw` | `rx_amlw_ami` | 153–279 kHz",
            "electrically `non_50_ohm_loop_pod`",
            "recording/scan metadata stays `unqualified`",
            "profile failure never enters TX-arm logic",
            "acquire `SG-BROADCAST`",
            "cannot claim ESD integrity, antenna presence, loop inductance",
            "failed coexistence result invalidates the affected profile evidence",
        ):
            self.assertIn(token, arc2)

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
