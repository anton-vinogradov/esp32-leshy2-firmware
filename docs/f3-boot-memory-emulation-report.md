# F3 result — boot, memory and emulation

[Русский](f3-boot-memory-emulation-report.ru.md) · [Home](../README.md) ·
[Firmware roadmap](roadmap.md) ·
[Machine closure](../config/f3_4_review.json)

F3 is reviewed. The exact ESP32-S3 debug and release target binaries booted in
Espressif QEMU, initialized and tested the selected 8-MiB octal PSRAM, and
executed the portable self-test, retained-first-fault and failed-update RAM
paths. All five targets were rebuilt twice from clean directories: all 52
artifacts reproduced byte-for-byte and every current image/RAM/static rollback
gate passed.

This is not a physical-board claim. No real flash rollback, peripheral, radio,
watchdog or `FAULT_KILL` transition is promoted by F3.

## Result at a glance

| Evidence | Reviewed result |
|---|---|
| Exact target emulator | ESP32-S3 QEMU `esp_develop_9.2.2_20250817` |
| S3 boot runs | Debug + release; six ordered boot/PSRAM markers each |
| S3 scenario runs | Debug + release; nine ordered markers each |
| Portable fault suite | 24/24 scenarios under ASan/UBSan |
| Current target builds | 10 configurations; 52/52 byte-reproducible artifacts |
| Resource gates | 10/10 image and linked-memory gates pass |
| Rollback topology | 5/5 static A/B layouts fit; 0 physical transitions claimed |
| Hardware actions | No purchase, PCB layout or fabrication authorized |

## Current resource envelope

The table uses the larger debug/release application image for each target.
“Free before maximum” is the remaining policy budget, not the raw flash left in
the slot.

| Target | Largest image | Policy maximum | Free before maximum | Linked-memory result |
|---|---:|---:|---:|---|
| S3 | 182,736 B | 7,077,888 B | 6,895,152 B | DIRAM has 287,147 B free; 8-MiB PSRAM runtime-tested |
| C5 | 172,224 B | 3,538,944 B | 3,366,720 B | HP SRAM has 263,010 B free; external PSRAM awaits hardware |
| RP2354B | 18,484 B | 884,736 B | 866,252 B | main + scratch SRAM has 526,008 B free |
| Pack | 3,168 B | 22,528 B | 19,360 B | application SRAM has 7,880 B free |
| Safety | 3,296 B | 22,528 B | 19,232 B | application SRAM has 7,880 B free |

Exact debug/release records, hashes, partitions and linker regions are in the
[F3.3 boundary evidence](../config/f3_3_boundary_review.json).

## What ran, and what did not

| Target | Accepted in F3 | Explicit physical closure |
|---|---|---|
| S3 | Exact boot chain, `app_main`, UART, 8-MiB PSRAM test and three isolated RAM-model scenarios | Leshy2 H7/H8 + firmware F10: display, touch, microSD, audio, radio, GPIO timing, first OTA write and real rollback |
| C5 | Reproducible target artifacts, portable contracts, image/RAM/A-B fit | `ESP32-C5-DevKitC-1-N8R8`, then H7/H8: boot, PSRAM, Wi-Fi/BLE/802.15.4, IR, SDIO and rollback |
| RP | Reproducible Arm-secure artifacts, portable contracts, image/SRAM/A-B fit | SC1512-A4 carrier or H7 via SWD/UART: boot, TBYB, PIO/DMA, radio and Cap-Bus timing |
| Pack | Reproducible boot/application artifacts, safety model, flash/SRAM/A-B fit | `LP-MSPM0C1106`, then H7/H8: boot, ADC/I2C, admission timing and flash rollback |
| Safety | Reproducible boot/application artifacts, safety model, flash/SRAM/A-B fit | `LP-MSPM0C1106`, then H7/H8: watchdog, thermal ADC, `FAULT_KILL`, TX-lease timing and flash rollback |

The blank ESP OTA-data sector exposed a real limitation in the available QEMU
flash model. The reviewed runner uses a deterministic QEMU-only initial OTA
entry and leaves first-boot writes, later flash mutation and rollback entirely
outside the accepted claims. Production ELF files are not patched.

## Evidence chain

- [Execution capability matrix](../config/f3_execution_capability_matrix.json)
  identifies one exact virtual SoC and four honest physical target gates.
- [Runtime plan](../config/f3_runtime_plan.json) locks QEMU, PSRAM size, timeout,
  markers, diagnostics and the OTA fixture boundary.
- [F3.1 debug](../config/f3_1_s3_debug_runtime_review.json) and
  [release](../config/f3_1_s3_release_runtime_review.json) evidence prove boot.
- [F3.2 integrated evidence](../config/f3_2_runtime_review.json) proves target
  execution of the three RAM paths plus the sanitized host suite.
- [F3.3 boundary evidence](../config/f3_3_boundary_review.json) binds current
  build inputs, artifacts, linked memory, partitions and rollback topologies.
- [F3 closure](../config/f3_4_review.json) assigns every residual to a named
  dev-board/HIL gate.

## Exit and next boundary

Every F3 exit criterion is satisfied at its honest evidence level. Firmware
continues at `F4.0.0`, where transport support and the end-to-end IPC/scheduler
evidence plan are frozen before implementation. Hardware may consume this
report as the closed `H4.0.1` prerequisite and begin the joined read-only H4.1
review; orders, PCB placement and routing remain unauthorized.
