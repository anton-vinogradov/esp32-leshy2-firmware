# Система сборки пяти прошивок

[English](toolchains.md) · [На главную](../README.ru.md) ·
[Роадмап](roadmap.ru.md)

Эта страница собирает принятые результаты завершённой фазы F2: официальные
toolchains, неизменяемые environment locks, общие команды и владение исходниками.

## Результаты F2, прошедшие ревью

| Подэтап | Статус | Результат |
|---|---|---|
| F2.0.0 | Проведено ревью | пять физических target и их memory/rollback contracts |
| F2.0.1 | Проведено ревью | точная матрица SDK, compiler, support, lifecycle и licenses в [`config/toolchain_matrix.json`](../config/toolchain_matrix.json) |
| F2.0.2 | Проведено ревью | два host-профиля, 26 hash архивов и Python dependency lock в [`environment/toolchains.lock.json`](../environment/toolchains.lock.json); проверяет [`tools/verify_environment_lock.py`](../tools/verify_environment_lock.py) |
| F2.0.3 | Проведено ревью | контракт команд и artifacts 5 targets × 2 configurations в [`config/build_matrix.json`](../config/build_matrix.json); исполняет [`tools/build_targets.py`](../tools/build_targets.py) |
| F2.1.0 | Проведено ревью | владение portable/generated/target-local исходниками в [`config/source_layout.json`](../config/source_layout.json); проверяет [`tools/check_source_layout.py`](../tools/check_source_layout.py) |
| F2.1.1 | Проведено ревью | language, warning, optimization и link rules в [`config/build_policy.json`](../config/build_policy.json); проверяет [`tools/check_build_policy.py`](../tools/check_build_policy.py) |
| F2.1.2 | Проведено ревью | сводный evidence в [`config/f2_1_review.json`](../config/f2_1_review.json); исполняет [`tools/review_f2_1.py`](../tools/review_f2_1.py) |
| F2.2.0 | Проведено ревью | минимальный offline S3 ESP-IDF project и строгие project components в [`config/target_projects.json`](../config/target_projects.json); проверяет [`tools/check_target_projects.py`](../tools/check_target_projects.py) |
| F2.2.1 | Проведено ревью | минимальный offline C5 ESP-IDF project, dual-OTA inputs и строгие components в [`config/target_projects.json`](../config/target_projects.json) |
| F2.2.2 | Проведено ревью | точный RP2354B Arm-secure project, custom board на 2 МиБ и partition input в [`config/target_projects.json`](../config/target_projects.json) |
| F2.2.3 | Проведено ревью | точный Pack MSPM0C1106 project, раздельные boot/application images и memory boundaries в [`config/target_projects.json`](../config/target_projects.json) |
| F2.2.4 | Проведено ревью | точный Safety MSPM0C1106 project, раздельные boot/application images и fail-closed entry в [`config/target_projects.json`](../config/target_projects.json) |
| F2.2.5 | Проведено ревью | сводный evidence пяти projects в [`config/f2_2_review.json`](../config/f2_2_review.json); исполняет [`tools/review_f2_2.py`](../tools/review_f2_2.py) |
| F2.3.0 | Проведено ревью | неизменяемый H2 source и детерминированная pin model в [`config/bsp_generation_input.json`](../config/bsp_generation_input.json); проверяет [`tools/validate_bsp_generation_input.py`](../tools/validate_bsp_generation_input.py) |
| F2.3.1 | Проведено ревью | 11 детерминированных C/header outputs в [`generated/source_manifest.json`](../generated/source_manifest.json); записывает/проверяет [`tools/generate_hardware_bsp.py`](../tools/generate_hardware_bsp.py) |
| F2.3.2 | Проведено ревью | one-owner mapping в [`config/bsp_target_consumption.json`](../config/bsp_target_consumption.json); проверяет [`tools/check_bsp_target_consumption.py`](../tools/check_bsp_target_consumption.py) |
| F2.3.3 | Проведено ревью | сводный H2/BSP evidence в [`config/f2_3_review.json`](../config/f2_3_review.json); исполняет [`tools/review_f2_3.py`](../tools/review_f2_3.py) |
| F2.4.0.1 | Проведено ревью | точные source revisions ESP-IDF `7101770d`, Pico SDK `98a542c1`, picotool `6f6458d7` и TI MSPM0 SDK `20807db7` |
| F2.4.0.2 | Проведено ревью | точные ESP S3/C5 compiler, debugger, ULP, OpenOCD и ROM packages установлены ESP-IDF tool manager |
| F2.4.0.3 | Проведено ревью | hash-locked Python 3.12, CMake `4.0.3` и Ninja `1.12.1`; [`config/f2_4_preflight_progress.json`](../config/f2_4_preflight_progress.json) |
| F2.4.0.4 | Проведено ревью | hash-verified native Arm GNU `15.2.Rel1` для RP2354B |
| F2.4.0.5 | Проведено ревью | hash-verified TI Arm Clang `4.0.5.LTS` и SysConfig `1.28.0.4712` для Pack/Safety |
| F2.4.0.6 | Проведено ревью | 30 точных проверок и debug/release preflight всех пяти targets; [`config/f2_4_preflight_review.json`](../config/f2_4_preflight_review.json) |
| F2.4.1 | Проведено ревью | S3 debug/release builds создали и проверили 10 artifacts; application images занимают 180 160 и 138 416 байт; [`config/f2_4_s3_build_review.json`](../config/f2_4_s3_build_review.json) |
| F2.4.2 | Проведено ревью | C5 debug/release builds создали и проверили 10 artifacts; application images занимают 172 224 и 125 616 байт; debug bootloader отслеживается при запасе 2 240 байт; [`config/f2_4_c5_build_review.json`](../config/f2_4_c5_build_review.json) |
| F2.4.3 | Проведено ревью | RP2354B debug/release builds создали и проверили 8 artifacts; binaries занимают 18 468 и 10 656 байт; [`config/f2_4_rp_build_review.json`](../config/f2_4_rp_build_review.json) |
| F2.4.4 | Проведено ревью | Pack debug/release builds создали и проверили 12 artifacts; application images занимают 3 168 байт, boot-manager images — 256 байт; [`config/f2_4_pack_build_review.json`](../config/f2_4_pack_build_review.json) |
| F2.4.5 | Проведено ревью | Safety debug/release builds создали и проверили 12 artifacts; application images занимают 3 296 байт, boot-manager images — 256 байт; [`config/f2_4_safety_build_review.json`](../config/f2_4_safety_build_review.json) |
| F2.4.6 | Проведено ревью | сводное ревью прошло для 5 targets, 10 конфигураций, 52 artifacts, 14 maps и 10 image gates; [`config/f2_4_build_review.json`](../config/f2_4_build_review.json), [`tools/review_f2_4_builds.py`](../tools/review_f2_4_builds.py) |
| F2.5 | Проведено ревью | два чистых прохода дали 52/52 побайтно идентичных artifacts; в 24 распространяемых образах нет утечек абсолютного workspace path; [`config/f2_5_reproducibility_review.json`](../config/f2_5_reproducibility_review.json) |

Строки F2.4.1–F2.4.6 заявляют target builds и их сводное artifact review.
Runtime boot остаётся недоказанным до следующих emulator- и hardware-фаз.

## Матрица SDK и компиляторов

| Образы | Production SDK | Компилятор | Аппаратная поддержка |
|---|---|---|---|
| S3 | ESP-IDF `v6.0.2` | `xtensa-esp-elf 15.2.0_20251204` | ESP32-S3 заявлен производителем минимум до 01.01.2033 |
| C5 | ESP-IDF `v6.0.2` | `riscv32-esp-elf 15.2.0_20251204` | ESP32-C5 заявлен производителем минимум до 01.01.2037 |
| RP | Pico SDK/picotool `2.3.0`, `rp2350-arm-s` | Arm GNU `15.2.Rel1` | RP2350/RP2354B заявлен в производстве минимум до 01.2045 |
| Pack, Safety | TI MSPM0 SDK `2.11.00.07` | TI Arm Clang `4.0.5.LTS` | точный MSPM0C1106 поддержан SDK; компонент имеет статус ACTIVE |

Для TI сохранена проверенная SDK ветка `4.0.x LTS`, но взят её последний
корректирующий выпуск вместо базового `4.0.0` с известными дефектами. Оба
MSPM0-образа имеют отдельные проекты, но используют одну проверенную
SDK/toolchain family.

## Что уже подтверждено

- Все три SDK — текущие production/stable releases из первоисточников.
- Каждый точный чип или модуль присутствует в поддерживаемой target family.
- RP остаётся в ранее принятой Arm Cortex-M33 secure-конфигурации; перехода на
  RISC-V не произошло.
- Зафиксированы host requirements, license families и публичный lifecycle.
- Версии больше не выбираются из архивных документов или плавающей ветки.

## Что ещё не утверждается

F2 доказывает offline-воспроизводимые debug/release builds и статические
image limits. Она не заявляет runtime boot, instruction/peripheral execution
или работоспособность физической платы. Эти доказательства принадлежат F3 и
последующим dev-board/HIL gates.

Канонический TI archive endpoint на macOS требует export-session cookie.
Поэтому local preflight использует тот же точный release из официального
публичного Git-репозитория TI: tag `mspm0_sdk_2_11_00_07`, commit `20807db7`;
архивы compiler и SysConfig остаются hash-locked загрузками производителя.

## Канонические команды

Локально и в CI используется один shell-free dispatcher. `TARGET` — `s3`,
`c5`, `rp`, `pack`, `safety` или `all`; `CONFIG` — `debug` или `release`.

```text
make matrix-check
make target-preflight TARGET=all CONFIG=debug
make target-configure TARGET=s3 CONFIG=debug
make target-build TARGET=s3 CONFIG=debug
make target-verify TARGET=s3 CONFIG=debug
make target-artifacts TARGET=s3 CONFIG=debug
make target-clean TARGET=s3 CONFIG=debug
make locked-target-configure TARGET=s3 CONFIG=debug
make locked-target-build TARGET=s3 CONFIG=debug
make locked-target-clean TARGET=s3 CONFIG=debug
make locked-target-verify TARGET=s3 CONFIG=debug
make capture-target-build TARGET=s3
make f2-5-reproducibility-review
```

Dispatcher не запускает shell, а matrix не разрешает скачивать зависимости во
время configure/build. Preflight завершается до исполнения, если не совпадает
точный SDK Git revision, hash-lock, версия compiler/tool, вход MSPM0C1106 или
Python 3.12 environment. Locked-команды автоматически применяют проверенную
локальную среду. Команда
capture записывает относительные пути artifacts, размеры, SHA-256, image gate и
manifest project inputs, не добавляя build outputs в Git. Все пять targets
прошли этот путь; F2.4.6 теперь сводит их evidence. Запас ESP bootloader
фиксируется рядом с application gate. F2.5 фиксирует два полных чистых прохода
и hash каждого artifact.

## Лицензии

ESP-IDF распространяется по Apache-2.0, Pico SDK — BSD-3-Clause, основная часть
TI MSPM0 SDK — BSD-3-Clause с отдельным manifest компонентов. Компиляторы
содержат собственные и сторонние notices. До release F11 их точные тексты и
redistribution obligations попадут в SBOM; текущая проверка подтверждает, что
выбранные инструменты допустимы для открытой разработки, но не заменяет release
license audit.

## Покрытие исполнения

F3 различает настоящую загрузку target binary и переносимую host-модель.
Пересборка под host или generic CPU emulator дают полезные доказательства, но
не доказывают загрузку production SoC.

| Образ | Самый сильный принятый путь F3 | Что он может доказать | Физическое закрытие |
|---|---|---|---|
| S3 | точный Espressif `qemu-system-xtensa -M esp32s3` | boot chain, вход в `app_main`, UART log и CPU/memory control flow | дисплей, touch, storage, audio, radio и GPIO timing на H7/H8 |
| C5 | переносимая contract/fault-модель плюс статические target artifacts | программные контракты, границы image и partitions | точная C5 dev board, затем Leshy2 H7/H8 |
| RP | переносимая contract/fault-модель плюс статические target artifacts | программные контракты, границы image и partitions | RP2354B carrier или Leshy2 через SWD/UART |
| Pack | переносимая safety/fault-модель плюс статические target artifacts | safety state machine и границы image | `LP-MSPM0C1106`, затем Leshy2 H7/H8 |
| Safety | переносимая safety/fault-модель плюс статические target artifacts | safety state machine и границы image | `LP-MSPM0C1106`, затем Leshy2 H7/H8 |

Зафиксированный ESP-IDF публикует QEMU targets для ESP32, ESP32-C3 и
ESP32-S3, но не ESP32-C5. Host-платформа Pico SDK прямо задаёт no-hardware
build. Принятой точной virtual SoC для RP2354B или MSPM0C1106 не найдено.
Поэтому target-emulator path есть только у S3; пока не выполнен ни один запуск,
а F3.0.0 не разрешает покупку отладочных плат.

Точная граница доказательств записана в
[`config/f3_execution_capability_matrix.json`](../config/f3_execution_capability_matrix.json)
и fail-closed проверяется
[`tools/check_f3_execution_capability.py`](../tools/check_f3_execution_capability.py).
Первоисточники: Espressif [ESP32-S3 QEMU guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/tools/qemu.html)
и [QEMU feature matrix](https://github.com/espressif/esp-toolchain-docs/blob/main/qemu/README.md),
[ESP32-C5-DevKitC-1 guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c5/esp32-c5-devkitc-1/user_guide.html),
Raspberry Pi [Debug Probe documentation](https://www.raspberrypi.com/documentation/microcontrollers/debug-probe.html)
и TI [`LP-MSPM0C1106`](https://www.ti.com/tool/LP-MSPM0C1106).

F3.0.1 также фиксирует два S3 run recipes (debug и release), точные QEMU
archives для двух поддержанных hosts, четыре последовательных boot markers,
30-секундный timeout и fail-closed result schema в
[`config/f3_runtime_plan.json`](../config/f3_runtime_plan.json). Это прошедший
ревью план исполнения, а не заявление о состоявшемся emulator run; его
проверяет [`tools/check_f3_runtime_plan.py`](../tools/check_f3_runtime_plan.py).
