# Система сборки пяти прошивок

[English](toolchains.md) · [На главную](../README.ru.md) ·
[Роадмап](roadmap.ru.md)

Эта страница собирает принятые результаты текущей фазы F2: официальные
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
| **F2.4.0** | **Сейчас** | точный local locked-toolchain preflight пяти targets |

Ни одна строка этой таблицы не заявляет target build. Такие результаты появятся
только после выполнения F2.4 в обеих конфигурациях для всех пяти проектов.

## Матрица SDK и компиляторов

| Образы | Production SDK | Компилятор | Аппаратная поддержка |
|---|---|---|---|
| S3 | ESP-IDF `v6.0.2` | `xtensa-esp-elf 15.2.0_20251204` | ESP32-S3 заявлен производителем минимум до 01.01.2033 |
| C5 | ESP-IDF `v6.0.2` | `riscv32-esp-elf 15.2.0_20251204` | ESP32-C5 заявлен производителем минимум до 01.01.2037 |
| RP | Pico SDK `2.3.0`, `rp2350-arm-s` | Arm GNU `15.2.Rel1` | RP2350/RP2354B заявлен в производстве минимум до 01.2045 |
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

F2.0.1 не означает, что образы уже собирались. F2.0.2 уже закрепила URL и
SHA-256 26 архивов для host, обе SDK revisions и ESP-IDF Python environment в
[`environment/toolchains.lock.json`](../environment/toolchains.lock.json).
Текущая F2.0.3 определяет единые local/CI-команды, а фактические debug/release
builds относятся к F2.4.

TI SDK требует export approval при скачивании. Это ограничение записано заранее
и не обходится; оно не является разрешением на загрузку или установку.

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
```

Dispatcher не запускает shell, а matrix не разрешает скачивать зависимости во
время configure/build. Preflight завершается до исполнения, если отсутствует
проект, точный путь к SDK/компилятору или Python 3.12 environment. F2.0.3
зафиксировала этот контракт; F2.2 проверила структуры всех пяти проектов, а
configure/build остаются на F2.4 после импорта BSP на F2.3.

## Лицензии

ESP-IDF распространяется по Apache-2.0, Pico SDK — BSD-3-Clause, основная часть
TI MSPM0 SDK — BSD-3-Clause с отдельным manifest компонентов. Компиляторы
содержат собственные и сторонние notices. До release F11 их точные тексты и
redistribution obligations попадут в SBOM; текущая проверка подтверждает, что
выбранные инструменты допустимы для открытой разработки, но не заменяет release
license audit.
