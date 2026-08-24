# Build system for five firmware images

[Русский](toolchains.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

This page collects the accepted results of the current F2 phase: first-party
toolchains, immutable environment locks, common commands and source ownership.

## Reviewed F2 results

| Step | Status | Result |
|---|---|---|
| F2.0.0 | Reviewed | five physical targets and their memory/rollback contracts |
| F2.0.1 | Reviewed | exact SDK, compiler, support, lifecycle and license matrix in [`config/toolchain_matrix.json`](../config/toolchain_matrix.json) |
| F2.0.2 | Reviewed | two host profiles, 26 archive hashes and Python dependency lock in [`environment/toolchains.lock.json`](../environment/toolchains.lock.json); checked by [`tools/verify_environment_lock.py`](../tools/verify_environment_lock.py) |
| F2.0.3 | Reviewed | 5-target × 2-configuration command and artifact contract in [`config/build_matrix.json`](../config/build_matrix.json); dispatched by [`tools/build_targets.py`](../tools/build_targets.py) |
| F2.1.0 | Reviewed | portable/generated/target-local ownership in [`config/source_layout.json`](../config/source_layout.json); checked by [`tools/check_source_layout.py`](../tools/check_source_layout.py) |
| F2.1.1 | Reviewed | language, warning, optimization and link rules in [`config/build_policy.json`](../config/build_policy.json); checked by [`tools/check_build_policy.py`](../tools/check_build_policy.py) |
| F2.1.2 | Reviewed | integrated boundary evidence in [`config/f2_1_review.json`](../config/f2_1_review.json); executed by [`tools/review_f2_1.py`](../tools/review_f2_1.py) |
| F2.2.0 | Reviewed | minimal offline S3 ESP-IDF project and strict project components in [`config/target_projects.json`](../config/target_projects.json); checked by [`tools/check_target_projects.py`](../tools/check_target_projects.py) |
| F2.2.1 | Reviewed | minimal offline C5 ESP-IDF project, dual-OTA inputs and strict components in [`config/target_projects.json`](../config/target_projects.json) |
| F2.2.2 | Reviewed | exact RP2354B Arm-secure project, 2-MiB custom board and partition input in [`config/target_projects.json`](../config/target_projects.json) |
| F2.2.3 | Reviewed | exact Pack MSPM0C1106 project, separate boot/application images and memory boundaries in [`config/target_projects.json`](../config/target_projects.json) |
| F2.2.4 | Reviewed | exact Safety MSPM0C1106 project, separate boot/application images and fail-closed entry in [`config/target_projects.json`](../config/target_projects.json) |
| F2.2.5 | Reviewed | integrated five-project evidence in [`config/f2_2_review.json`](../config/f2_2_review.json); executed by [`tools/review_f2_2.py`](../tools/review_f2_2.py) |
| F2.3.0 | Reviewed | immutable H2 source and deterministic pin model in [`config/bsp_generation_input.json`](../config/bsp_generation_input.json); checked by [`tools/validate_bsp_generation_input.py`](../tools/validate_bsp_generation_input.py) |
| F2.3.1 | Reviewed | 11 deterministic C/header outputs in [`generated/source_manifest.json`](../generated/source_manifest.json); writes/checks with [`tools/generate_hardware_bsp.py`](../tools/generate_hardware_bsp.py) |
| F2.3.2 | Reviewed | one-owner mapping in [`config/bsp_target_consumption.json`](../config/bsp_target_consumption.json); checked by [`tools/check_bsp_target_consumption.py`](../tools/check_bsp_target_consumption.py) |
| F2.3.3 | Reviewed | integrated H2/BSP evidence in [`config/f2_3_review.json`](../config/f2_3_review.json); executed by [`tools/review_f2_3.py`](../tools/review_f2_3.py) |
| F2.4.0.1 | Checked locally | exact ESP-IDF `7101770d`, Pico SDK `98a542c1` and TI MSPM0 SDK `20807db7` source revisions |
| F2.4.0.2 | Checked locally | exact ESP S3/C5 compiler, debugger, ULP, OpenOCD and ROM packages installed by the ESP-IDF tool manager |
| **F2.4.0.3** | **Current** | locked Python 3.12 environment and exact CMake/Ninja host tools |

No row in this table claims a target build. Those results appear only after
F2.4 executes both configurations for all five projects.

## SDK and compiler matrix

| Images | Production SDK | Compiler | Hardware support |
|---|---|---|---|
| S3 | ESP-IDF `v6.0.2` | `xtensa-esp-elf 15.2.0_20251204` | ESP32-S3 vendor commitment through at least 2033-01-01 |
| C5 | ESP-IDF `v6.0.2` | `riscv32-esp-elf 15.2.0_20251204` | ESP32-C5 vendor commitment through at least 2037-01-01 |
| RP | Pico SDK `2.3.0`, `rp2350-arm-s` | Arm GNU `15.2.Rel1` | RP2350/RP2354B production through at least January 2045 |
| Pack, Safety | TI MSPM0 SDK `2.11.00.07` | TI Arm Clang `4.0.5.LTS` | the SDK supports MSPM0C1106 and the exact device is ACTIVE |

The TI selection stays on the SDK-validated `4.0.x LTS` line but uses its latest
corrective release instead of the defect-bearing `4.0.0` base release. Pack and
Safety remain separate images and projects while sharing one verified
SDK/toolchain family.

## What is verified

- All three SDKs are current production/stable first-party releases.
- Every exact chip or module belongs to a supported target family.
- RP keeps the accepted Arm Cortex-M33 secure configuration; this does not
  silently switch the product to the RISC-V core.
- Host requirements, license families and published lifecycle are recorded.
- No selection depends on archived documents or a floating development branch.

## What is not claimed yet

F2.0.1 does not claim a successful target build. F2.0.2 has now pinned the URL
and SHA-256 of 26 host archives, both SDK revisions and the ESP-IDF Python
environment in [`environment/toolchains.lock.json`](../environment/toolchains.lock.json).
Current F2.0.3 defines common local/CI commands; actual debug/release builds
belong to F2.4.

The canonical TI archive endpoint requires an export-session cookie on macOS.
Local preflight therefore uses the same exact release from TI's official public
Git repository, tag `mspm0_sdk_2_11_00_07`, commit `20807db7`; compiler and
SysConfig archives remain hash-locked vendor downloads.

## Canonical commands

The same shell-free dispatcher is used locally and in CI. `TARGET` is one of
`s3`, `c5`, `rp`, `pack`, `safety` or `all`; `CONFIG` is `debug` or `release`.

```text
make matrix-check
make target-preflight TARGET=all CONFIG=debug
make target-configure TARGET=s3 CONFIG=debug
make target-build TARGET=s3 CONFIG=debug
make target-verify TARGET=s3 CONFIG=debug
make target-artifacts TARGET=s3 CONFIG=debug
make target-clean TARGET=s3 CONFIG=debug
```

The dispatcher never invokes a shell and the matrix permits no dependency
downloads during configure/build. Preflight fails before execution when a
project, exact SDK path, compiler path or Python 3.12 environment is absent.
F2.0.3 fixed this contract; F2.2 reviewed all five project structures, while
configure/build execution remains reserved for F2.4 after the F2.3 BSP import.

## Licenses

ESP-IDF is Apache-2.0, Pico SDK is BSD-3-Clause, and the MSPM0 SDK core is
BSD-3-Clause with a per-component manifest. Toolchains carry their own and
third-party notices. Exact texts and redistribution obligations enter the SBOM
before F11 release; this review establishes a viable open-development path but
does not replace the release license audit.
