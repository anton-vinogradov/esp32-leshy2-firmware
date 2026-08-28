# Build system for six firmware targets

[Русский](toolchains.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

The current R2 build plan has six independent targets. The retained completed
R1 evidence below remains regression history and does not qualify R2 binaries.

## Current R2 result

| Step | Status | Result |
|---|---|---|
| F2-R2.0 | Reviewed | hash-locked five-target R1 inventory and exact six-target migration plan in [`config/f2_r2_target_rebaseline.json`](../config/f2_r2_target_rebaseline.json) |
| F2-R2.1 | Reviewed | exact 6-target × 2-configuration offline argv matrix in [`config/f2_r2_build_matrix.json`](../config/f2_r2_build_matrix.json): ESP-IDF `v6.0.2`, Pico SDK/picotool `2.3.0`, MSPM0 SDK `2.11.00.07`; 60 artifact paths, 16 maps and 16 size gates; zero R2 projects or executions claimed |
| F2-R2.2 | Reviewed | six production-SDK roots in [`config/f2_r2_target_projects.json`](../config/f2_r2_target_projects.json): four retained structures plus separate offline, pin-free RF-RP and Hub-RP Pico SDK trees; distinct entries/images/state; zero BSP/configure/build/execution claims |
| F2-R2.3 | Current | generate six deterministic R2 BSP domains and bind each to exactly one project without running an R2 build |

The matrix locks every configure/build/clean command to a separate
`build/r2/targets/<target>/<configuration>` root, requires SHA-verified archives,
exact source commits, Python 3.12 with hashed requirements,
`SOURCE_DATE_EPOCH`, offline ESP Component Manager and disconnected Pico
FetchContent. S3 QEMU remains an F3-R2 gate; C5 has no official QEMU machine,
Pico host is not RP2350 emulation, and MSPM0C1106 has no accepted official
simulator. Development-board and Leshy2 HIL runs remain zero.

The existing `generated/hardware` tree is still the locked five-domain R1
artifact and is not an R2 build input. F2-R2.3 replaces that boundary from the
hash-bound six-domain hardware projection; no project may substitute handwritten
production pins.

## Historical R1 results

### Reviewed F2 results

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
| F2.4.0.1 | Reviewed | exact ESP-IDF `7101770d`, Pico SDK `98a542c1`, picotool `6f6458d7` and TI MSPM0 SDK `20807db7` source revisions |
| F2.4.0.2 | Reviewed | exact ESP S3/C5 compiler, debugger, ULP, OpenOCD and ROM packages installed by the ESP-IDF tool manager |
| F2.4.0.3 | Reviewed | hash-locked Python 3.12 plus CMake `4.0.3` and Ninja `1.12.1`; [`config/f2_4_preflight_progress.json`](../config/f2_4_preflight_progress.json) |
| F2.4.0.4 | Reviewed | hash-verified native Arm GNU `15.2.Rel1` for RP2354B |
| F2.4.0.5 | Reviewed | hash-verified TI Arm Clang `4.0.5.LTS` and SysConfig `1.28.0.4712` for Pack/Safety |
| F2.4.0.6 | Reviewed | 30 exact checks and debug/release preflight for all five targets; [`config/f2_4_preflight_review.json`](../config/f2_4_preflight_review.json) |
| F2.4.1 | Reviewed | S3 debug/release builds produced and verified 10 artifacts; application images are 180,160 and 138,416 bytes; [`config/f2_4_s3_build_review.json`](../config/f2_4_s3_build_review.json) |
| F2.4.2 | Reviewed | C5 debug/release builds produced and verified 10 artifacts; application images are 172,224 and 125,616 bytes; debug bootloader margin is watched at 2,240 bytes; [`config/f2_4_c5_build_review.json`](../config/f2_4_c5_build_review.json) |
| F2.4.3 | Reviewed | RP2354B debug/release builds produced and verified 8 artifacts; binaries are 18,468 and 10,656 bytes; [`config/f2_4_rp_build_review.json`](../config/f2_4_rp_build_review.json) |
| F2.4.4 | Reviewed | Pack debug/release builds produced and verified 12 artifacts; application images are 3,168 bytes and boot-manager images are 256 bytes; [`config/f2_4_pack_build_review.json`](../config/f2_4_pack_build_review.json) |
| F2.4.5 | Reviewed | Safety debug/release builds produced and verified 12 artifacts; application images are 3,296 bytes and boot-manager images are 256 bytes; [`config/f2_4_safety_build_review.json`](../config/f2_4_safety_build_review.json) |
| F2.4.6 | Reviewed | integrated review passed for 5 targets, 10 configurations, 52 artifacts, 14 maps and 10 image gates; [`config/f2_4_build_review.json`](../config/f2_4_build_review.json), [`tools/review_f2_4_builds.py`](../tools/review_f2_4_builds.py) |
| F2.5 | Reviewed | two clean passes produced 52/52 byte-identical artifacts; 24 distributable images have zero absolute workspace-path leaks; [`config/f2_5_reproducibility_review.json`](../config/f2_5_reproducibility_review.json) |

The F2.4.1–F2.4.6 rows claim target builds and their integrated artifact review.
Runtime boot remains unproven until the later emulator and hardware phases.

## SDK and compiler matrix

| Images | Production SDK | Compiler | Hardware support |
|---|---|---|---|
| S3 | ESP-IDF `v6.0.2` | `xtensa-esp-elf 15.2.0_20251204` | ESP32-S3 vendor commitment through at least 2033-01-01 |
| C5 | ESP-IDF `v6.0.2` | `riscv32-esp-elf 15.2.0_20251204` | ESP32-C5 vendor commitment through at least 2037-01-01 |
| RP | Pico SDK/picotool `2.3.0`, `rp2350-arm-s` | Arm GNU `15.2.Rel1` | RP2350/RP2354B production through at least January 2045 |
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

F2 proves offline, reproducible debug/release builds and static image limits.
It does not claim runtime boot, instruction/peripheral execution or a working
physical board. Those claims belong to F3 and later dev-board/HIL gates.

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
make locked-target-configure TARGET=s3 CONFIG=debug
make locked-target-build TARGET=s3 CONFIG=debug
make locked-target-clean TARGET=s3 CONFIG=debug
make locked-target-verify TARGET=s3 CONFIG=debug
make capture-target-build TARGET=s3
make f2-5-reproducibility-review
```

The dispatcher never invokes a shell and the matrix permits no dependency
downloads during configure/build. Preflight fails before execution when a
project, exact SDK Git revision, hash lock, compiler/tool version, MSPM0C1106
input or Python 3.12 environment is absent or mismatched.
The locked commands apply the reviewed local environment automatically. The
capture command records relative artifact paths, byte counts, SHA-256 values,
the image gate and a project-input manifest without copying build outputs into
Git. All five targets have passed this path. F2.4.6 now checks their evidence
together; ESP bootloader margins are captured beside the application gate.
F2.5 records two complete clean passes and a hash for every artifact.

## Licenses

ESP-IDF is Apache-2.0, Pico SDK is BSD-3-Clause, and the MSPM0 SDK core is
BSD-3-Clause with a per-component manifest. Toolchains carry their own and
third-party notices. Exact texts and redistribution obligations enter the SBOM
before F11 release; this review establishes a viable open-development path but
does not replace the release license audit.

## Runtime execution coverage

F3 distinguishes a real target-binary boot from a portable host model. A host
recompile or a generic CPU emulator is useful evidence, but it is not evidence
that the production SoC booted.

| Image | Strongest accepted F3 path | What it may prove | Physical closure |
|---|---|---|---|
| S3 | exact Espressif `qemu-system-xtensa -M esp32s3` | boot chain, `app_main`, UART log and CPU/memory control flow | display, touch, storage, audio, radio and GPIO timing at H7/H8 |
| C5 | portable contract/fault model plus static target artifacts | software contracts, image and partition bounds | exact C5 dev board, then Leshy2 H7/H8 |
| RP | portable contract/fault model plus static target artifacts | software contracts, image and partition bounds | RP2354B carrier or Leshy2 through SWD/UART |
| Pack | portable safety/fault model plus static target artifacts | safety state machine and image boundaries | `LP-MSPM0C1106`, then Leshy2 H7/H8 |
| Safety | portable safety/fault model plus static target artifacts | safety state machine and image boundaries | `LP-MSPM0C1106`, then Leshy2 H7/H8 |

The locked ESP-IDF registry exposes QEMU targets for ESP32, ESP32-C3 and
ESP32-S3, but not ESP32-C5. Pico SDK's `host` platform explicitly defines a
no-hardware build. No accepted exact virtual SoC was found for RP2354B or
MSPM0C1106. Therefore only S3 has a target-emulator path. Its debug and release
images have now run; no development-board purchase is authorized by F3.

The exact evidence boundary is machine-readable in
[`config/f3_execution_capability_matrix.json`](../config/f3_execution_capability_matrix.json)
and fail-closed checked by
[`tools/check_f3_execution_capability.py`](../tools/check_f3_execution_capability.py).
Primary references are Espressif's [ESP32-S3 QEMU guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/tools/qemu.html)
and [QEMU feature matrix](https://github.com/espressif/esp-toolchain-docs/blob/main/qemu/README.md),
the [ESP32-C5-DevKitC-1 guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c5/esp32-c5-devkitc-1/user_guide.html),
Raspberry Pi's [Debug Probe documentation](https://www.raspberrypi.com/documentation/microcontrollers/debug-probe.html)
and TI's [`LP-MSPM0C1106` page](https://www.ti.com/tool/LP-MSPM0C1106).

F3.0.1 also fixes two S3 run recipes (debug and release), the exact QEMU
archives for both supported hosts, six ordered boot markers (including the
8-MiB octal-PSRAM initialization and memory test), a 30-second
timeout and the fail-closed result schema in
[`config/f3_runtime_plan.json`](../config/f3_runtime_plan.json). This is a
reviewed execution plan, not an emulator-run claim; it is checked by
[`tools/check_f3_runtime_plan.py`](../tools/check_f3_runtime_plan.py).

F3.0.2 maps all five images to the strongest honest evidence class in
[`config/f3_acceptance_matrix.json`](../config/f3_acceptance_matrix.json).
[`tools/run_f3_acceptance.py`](../tools/run_f3_acceptance.py) is the single
fail-closed plan, execution and evidence checker; only its exact S3 QEMU path
may produce a target-boot claim.

## Reviewed F3.1 execution

Both S3 configurations booted through the exact hash-locked Espressif QEMU and
passed the same six ordered UART markers: ROM, ESP-IDF bootloader, discovery of
8 MiB octal PSRAM, its memory test, entry into `app_main()` and the Leshy2
skeleton-ready message. QEMU is explicitly limited with `-m 8M`, matching the
selected N16R8 module instead of its 32-MiB helper default. Results are recorded
in the [debug evidence](../config/f3_1_s3_debug_runtime_review.json) and
[release evidence](../config/f3_1_s3_release_runtime_review.json).

A blank OTA-data sector exposed a QEMU SPI-flash write limitation before
`app_main()`. The runner therefore creates a deterministic QEMU-only flash
fixture with the initial valid OTA entry already present. It does not alter the
production ELF. First-boot OTA-data writes, later flash-state mutations and
rollback transitions remain physical HIL gates; the recorded known QEMU flash
diagnostics do not expand the accepted claims.

## Reviewed F3.2 scenarios

The current S3 debug and release binaries each passed nine ordered QEMU
markers. After the boot and 8-MiB PSRAM checks, isolated local state exercises
three fail-closed paths on the real Xtensa target binary: a complete five-domain
self-test/commit, an over-temperature retained first-cause RAM record, and a
mid-bundle self-test failure that restores every RAM-model build identifier.
The same portable cores passed 24 host scenarios with AddressSanitizer and
UndefinedBehaviorSanitizer. See the
[integrated evidence](../config/f3_2_runtime_review.json).

These tests deliberately do not write production flash or drive physical pins.
They therefore do not prove nonvolatile fault retention, image signature/readback,
bootloader rollback, display rendering, watchdog timing or `FAULT_KILL`; those
remain explicit physical gates.

## Reviewed F3.3 boundaries

A new two-pass clean build after the F3.2 source change reproduced all 52
artifacts. The [boundary evidence](../config/f3_3_boundary_review.json) binds
each current project-input manifest to its debug/release image, linker map,
linked-memory report, exact partition source and rollback topology.

The largest current application image in each domain is 182,688 bytes for S3,
172,224 for C5, 18,468 for RP, 3,168 for Pack and 3,296 for Safety. All ten
image gates pass. All five static A/B topologies end within their selected flash
device, and every linked memory report fits. S3's 8-MiB external RAM is also
runtime-tested; C5 external RAM and every real flash/boot rollback transition
remain physical HIL gates.
