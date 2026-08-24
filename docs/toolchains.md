# Build environment for five firmware images

[Русский](toolchains.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

This page presents the accepted F2.0.1 result: the first-party SDK family used
to build each of the five Leshy2 images. Exact machine-checkable records live in
[`config/toolchain_matrix.json`](../config/toolchain_matrix.json).

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

The TI SDK download requires export approval. The constraint is recorded and
will not be bypassed; this page does not authorize a download or installation.

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
F2.0.3 fixed this contract; projects remain absent at current F2.1.0 until
F2.1/F2.2 create them, so no target-build result is claimed.

## Licenses

ESP-IDF is Apache-2.0, Pico SDK is BSD-3-Clause, and the MSPM0 SDK core is
BSD-3-Clause with a per-component manifest. Toolchains carry their own and
third-party notices. Exact texts and redistribution obligations enter the SBOM
before F11 release; this review establishes a viable open-development path but
does not replace the release license audit.
