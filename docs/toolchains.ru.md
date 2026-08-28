# Система сборки шести firmware targets

[English](toolchains.md) · [На главную](../README.ru.md) ·
[Роадмап](roadmap.ru.md)

В текущем build plan R2 шесть независимых targets. Сохранённое завершённое
evidence R1 ниже остаётся regression history и не квалифицирует binaries R2.

## Текущий результат R2

| Подэтап | Статус | Результат |
|---|---|---|
| F2-R2.0 | Проведено ревью | hash-locked инвентаризация пяти targets R1 и точный план миграции шести targets в [`config/f2_r2_target_rebaseline.json`](../config/f2_r2_target_rebaseline.json) |
| F2-R2.1 | Проведено ревью | точная offline argv matrix 6 targets × 2 configurations в [`config/f2_r2_build_matrix.json`](../config/f2_r2_build_matrix.json): ESP-IDF `v6.0.2`, Pico SDK/picotool `2.3.0`, MSPM0 SDK `2.11.00.07`; 60 путей artifacts, 16 maps и 16 size gates; заявлено ноль R2 projects и executions |
| F2-R2.2 | Проведено ревью | шесть production-SDK roots в [`config/f2_r2_target_projects.json`](../config/f2_r2_target_projects.json): четыре сохранённые структуры и отдельные offline pin-free Pico SDK trees RF-RP и Hub-RP; разные entries/images/state; заявлено ноль BSP/configure/build/execution |
| F2-R2.3 | Проведено ревью | шесть детерминированных доменов BSP R2 сгенерированы и каждый привязан ровно к одному project без запуска R2 build |
| F2-R2.4 | Проведено ревью | атомарный [`config/f2_r2_build_qualification.json`](../config/f2_r2_build_qualification.json) фиксирует прохождение всех 12 configure/build jobs, 60 проверенных artifacts, 16 maps и 16 size gates без warnings; runtime и reproducibility остаются недоказанными |
| F2-R2.5 | Сейчас | выполнить два чистых прохода, побайтно сравнить каждый объявленный artifact и опубликовать двуязычный итог F2-R2 только после успешного сравнения |

Matrix закрепляет каждую команду configure/build/clean за отдельным root
`build/r2/targets/<target>/<configuration>`, требует SHA-verified archives,
точные source commits, Python 3.12 с hashed requirements, `SOURCE_DATE_EPOCH`,
offline ESP Component Manager и disconnected Pico FetchContent. S3 QEMU остаётся
gate F3-R2; у C5 нет официальной QEMU machine, Pico host не является эмуляцией
RP2350, а для MSPM0C1106 нет принятого официального simulator. Число прогонов
development-board и Leshy2 HIL остаётся нулём.

Существующее tree `generated/hardware` остаётся закреплённым артефактом R1 из
пяти доменов и не является build input R2. F2-R2.3 заменяет эту границу из
связанной hash аппаратной проекции шести доменов; ни один project не может
подменить её handwritten production pins.

Команда квалификации намеренно атомарна и работает только целиком:

```sh
.toolchains/python/idf6_py3.12_env/bin/python tools/build_f2_r2_targets.py qualify --dry-run
.toolchains/python/idf6_py3.12_env/bin/python tools/build_f2_r2_targets.py qualify --write-evidence
.toolchains/python/idf6_py3.12_env/bin/python tools/build_f2_r2_targets.py verify-evidence
```

Только вторая команда исполняет 12 jobs. Qualification record был записан
атомарно после прохождения всех 12 пар configure/build и всех объявленных
artifacts, maps и size gates. Для неё обязательны clean Git commit и пустые R2
build roots, поэтому stale objects не могут стать evidence. Record заявляет 12
target builds и ноль target runtime, emulator, development-board или physical
executions.

## Исторические результаты R1

### Результаты F2, прошедшие ревью

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
Поэтому target-emulator path есть только у S3. Его debug и release images уже
запущены; F3 не разрешает покупку отладочных плат.

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
archives для двух поддержанных hosts, шесть последовательных boot markers
(включая инициализацию и memory test 8-МиБ octal PSRAM), 30-секундный timeout и
fail-closed result schema в
[`config/f3_runtime_plan.json`](../config/f3_runtime_plan.json). Это прошедший
ревью план исполнения, а не заявление о состоявшемся emulator run; его
проверяет [`tools/check_f3_runtime_plan.py`](../tools/check_f3_runtime_plan.py).

F3.0.2 сопоставляет все пять images с самым сильным честным классом evidence в
[`config/f3_acceptance_matrix.json`](../config/f3_acceptance_matrix.json).
[`tools/run_f3_acceptance.py`](../tools/run_f3_acceptance.py) — единая
fail-closed проверка плана, исполнения и evidence; только её точный S3 QEMU
path может создать claim о target boot.

## Проверенное исполнение F3.1

Обе конфигурации S3 загрузились в точном hash-locked Espressif QEMU и прошли
одинаковые шесть последовательных UART markers: ROM, ESP-IDF bootloader,
обнаружение 8 МиБ octal PSRAM, её memory test, вход в `app_main()` и сообщение
готовности Leshy2 skeleton. Параметр QEMU `-m 8M` соответствует выбранному
модулю N16R8 вместо 32-МиБ значения official helper по умолчанию. Результаты:
[debug evidence](../config/f3_1_s3_debug_runtime_review.json) и
[release evidence](../config/f3_1_s3_release_runtime_review.json).

Пустой OTA-data sector выявил ограничение записи SPI flash в QEMU ещё до
`app_main()`. Поэтому runner создаёт детерминированный QEMU-only flash fixture,
где исходная valid OTA entry уже записана. Production ELF не меняется. Запись
OTA-data при первом boot, последующие flash-state mutations и rollback
transitions остаются физическими HIL gates; известные QEMU flash diagnostics
зафиксированы и не расширяют принятые claims.

## Проверенные сценарии F3.2

Актуальные S3 debug и release binaries прошли по девять последовательных QEMU
markers. После boot и проверки 8-МиБ PSRAM изолированное локальное состояние
исполняет три fail-closed path внутри настоящего Xtensa target binary: полный
five-domain self-test/commit, over-temperature retained first-cause в RAM и
ошибку self-test посреди bundle, возвращающую все build identifiers RAM-модели.
Те же portable cores прошли 24 host-сценария под AddressSanitizer и
UndefinedBehaviorSanitizer. См.
[сводный evidence](../config/f3_2_runtime_review.json).

Эти тесты намеренно не пишут production flash и не управляют физическими
пинами. Поэтому они не доказывают nonvolatile fault retention, проверку
signature/readback образа, bootloader rollback, отрисовку ошибки, timing
watchdog или `FAULT_KILL`; всё перечисленное остаётся явными physical gates.

## Проверенные границы F3.3

Новый двухпроходный clean build после изменения исходников в F3.2 воспроизвёл
все 52 artifacts. [Boundary evidence](../config/f3_3_boundary_review.json)
связывает manifest актуальных project inputs каждого домена с debug/release
image, linker map, linked-memory report, точным источником partitions и rollback
topology.

Самые крупные текущие application images: S3 — 182 688 байт, C5 — 172 224,
RP — 18 468, Pack — 3 168, Safety — 3 296. Все десять image gates проходят.
Пять статических A/B topologies заканчиваются в границах выбранной flash, все
linked memory reports помещаются. 8-МиБ external RAM S3 также проверена в
runtime; external RAM C5 и каждый реальный flash/boot rollback transition
остаются физическими HIL gates.
