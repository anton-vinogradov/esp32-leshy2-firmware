# Firmware memory, update and recovery

[Home](../README.md) · [Русский](memory.ru.md) · [Runtime architecture](architecture.md) · [Hardware memory wiring](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/memory.md)

Each physical controller owns its image, inactive slot, boot health and recovery
path. The user still installs one product bundle: a shared manifest prevents a
new image for one domain from activating beside incompatible peers.

## Capacity at a glance

| Image | Exact device | Volatile memory | Executable storage | Rollback allocation |
|---|---|---:|---:|---:|
| S3 | `ESP32-S3-WROOM-1U-N16R8` | 8 MiB octal PSRAM with ECC | 16 MiB flash | two 7-MiB OTA slots; image limit 6.75 MiB |
| C5 | `ESP32-C5-WROOM-1U-N8R8` | 8 MiB PSRAM | 8 MiB flash | two 3.5-MiB OTA slots; image limit 3.375 MiB |
| RP | `SC1512-A4` (`RP2354B`) | 520 KiB on-chip SRAM | 2 MiB stacked flash | native 896-KiB A/B pair; image limit 864 KiB |
| Pack | `MSPM0C1106SDGS20R` | 8 KiB SRAM | 64 KiB flash | protected 16 KiB + 22 KiB A + 22 KiB B + 4 KiB state |
| Safety | second `MSPM0C1106SDGS20R` | 8 KiB SRAM | 64 KiB flash | the same independent 16/22/22/4-KiB map |

[`tools/check_image_size.py`](../tools/check_image_size.py) consumes each
target's JSON limit and returns `ok`, `warning` or `reject`. A feature cannot
silently consume its second slot.

## One signed bundle

[`config/update_policy.json`](../config/update_policy.json) is the machine
contract. The bundle manifest binds every image hash to the Leshy2 product,
hardware revision range, physical target, build ID and protocol compatibility.
Normal installation accepts a release root or a locally enrolled owner root.
The selected common package signature is ECDSA P-256 over SHA-256; release is
blocked until the complete verifier fits and passes fault injection on C1106.

Update requires physical `RUN=KILL`, no actual-TX evidence and qualified stable
power. The updater first writes and reads back every inactive image. Pack,
Safety, C5 and RP then boot pending without discarding their old images. S3
boots last and must observe the expected build ID and local self-test from all
four peers within the bounded RP2350 TBYB window. Only then does it issue the
global commit. A crash, timeout, wrong target, bad signature, incompatible
protocol or missing confirmation returns every pending domain to its previous
image.

This protects the normal update path without closing the device. The baseline
does not burn irreversible secure-boot, anti-rollback or debug locks. A person
with physical flash/debug access can deliberately replace firmware and keys;
that is the owner's recovery boundary, not a remote update path.

## S3: 16-MiB flash and ECC PSRAM

Both application slots are 7 MiB. CI warns above 6 MiB and rejects an image
above `0x6C0000`, retaining 256 KiB per slot for growth, alignment and signed
metadata.

| Partition | Offset | Size | Purpose |
|---|---:|---:|---|
| bootloader + table | `0x000000` | through `0x009000` | ROM/second-stage boot and partition table |
| `nvs` | `0x009000` | `0x006000` | bounded configuration and calibration |
| `otadata` | `0x00F000` | `0x002000` | redundant active/pending/rollback state |
| `phy_init` | `0x011000` | `0x001000` | radio calibration seed |
| `coredump` | `0x012000` | `0x010000` | bounded crash record |
| `nvs_keys` | `0x022000` | `0x003000` | encrypted-NVS key material when enabled |
| boot reserve | `0x025000` | `0x00B000` | boot/security growth; never product assets |
| `ota_0` | `0x030000` | `0x700000` | running or last-known-good S3 image |
| `ota_1` | `0x730000` | `0x700000` | inactive/pending S3 image |
| `rescue_fs` | `0xE30000` | `0x100000` | minimal fault-viewer resources |
| `eventlog` | `0xF30000` | `0x080000` | bounded diagnostic ring |
| future reserve | `0xFB0000` | `0x050000` | migration space |

The sources are [`config/partitions_16m.csv`](../config/partitions_16m.csv),
[`config/s3_image_limits.json`](../config/s3_image_limits.json) and
[`config/sdkconfig.defaults.esp32s3`](../config/sdkconfig.defaults.esp32s3).
Production enables ESP-IDF rollback and PSRAM ECC through
`CONFIG_SPIRAM_ECC_ENABLE=y`. Startup must prove ECC,
read/write a test block and expose at least 7.5 MiB (`0x780000` bytes) of usable PSRAM before
normal UI or radio work begins.

Internal SRAM is reserved first for ISR code/data, DMA buffers, stacks and
inter-domain links. ECC PSRAM holds bounded UI scenes, waterfall history,
decoder workspaces and audio queues. Captures, recordings, maps, dictionaries
and replaceable UI packs are versioned microSD data rather than executable
image content.

## C5: 8-MiB dual OTA

The C5 keeps native Wi-Fi/802.15.4 and IR code local. Each OTA slot is 3.5 MiB;
CI warns above 3 MiB and rejects above `0x360000`, leaving 128 KiB inside each
slot.

| Partition | Offset | Size | Purpose |
|---|---:|---:|---|
| bootloader + table | `0x000000` | through `0x009000` | C5 ROM/second-stage boot and table |
| `nvs` | `0x009000` | `0x006000` | bounded radio configuration |
| `otadata` | `0x00F000` | `0x002000` | redundant ESP-IDF pending/rollback state |
| `phy_init` | `0x011000` | `0x001000` | RF calibration seed |
| `coredump` | `0x012000` | `0x010000` | bounded crash record |
| `nvs_keys` | `0x022000` | `0x003000` | encrypted-NVS keys when enabled |
| boot reserve | `0x025000` | `0x00B000` | boot and migration reserve |
| `ota_0` | `0x030000` | `0x380000` | running or last-known-good C5 image |
| `ota_1` | `0x3B0000` | `0x380000` | inactive/pending C5 image |
| `eventlog` | `0x730000` | `0x050000` | bounded C5 diagnostics |
| future reserve | `0x780000` | `0x080000` | migration space |

The sources are [`config/partitions_8m_c5.csv`](../config/partitions_8m_c5.csv),
[`config/c5_image_limits.json`](../config/c5_image_limits.json) and
[`config/sdkconfig.defaults.esp32c5`](../config/sdkconfig.defaults.esp32c5).
ESP-IDF rollback remains mandatory. Unlike S3, C5 PSRAM is not presented as
ECC-protected; deadline-critical buffers and state remain in internal RAM.

## RP2354B: native A/B and Try Before You Buy

The first 8 KiB are the two default RP2350 partition-table boot slots. The
remaining 2040 KiB are described by
[`config/rp2354b_partitions.json`](../config/rp2354b_partitions.json), directly
usable as input to `picotool partition create`.

| Region | Offset | Size | Purpose |
|---|---:|---:|---|
| partition-table slots | `0x000000` | `0x002000` | two 4-KiB RP2350 boot slots |
| RP image A | `0x002000` | `0x0E0000` | bootable image A |
| RP image B | `0x0E2000` | `0x0E0000` | linked bootable image B |
| owned data A | `0x1C2000` | `0x010000` | data versioned with image A |
| owned data B | `0x1D2000` | `0x010000` | linked data for image B |
| fault log | `0x1E2000` | `0x018000` | bounded retained diagnostics |
| service reserve | `0x1FA000` | `0x006000` | partition/schema migration |

Every candidate contains an IMAGE_DEF hash and TBYB flag. After a flash-update
boot, RP2350 ROM starts it under the fixed 16.7-second watchdog. New S3 sends
the commit only after all domains identify and self-test; RP then calls
`explicit_buy()`. Without that call the ROM returns to the previous partition.
The size source is
[`config/rp2354b_image_limits.json`](../config/rp2354b_image_limits.json).

## Pack and Safety: independent 64-KiB maps

Both C1106 controllers use the same geometry but different target IDs and
images. A package for one can never be accepted by the other.

| Region | Offset | Size | Purpose |
|---|---:|---:|---|
| protected boot manager | `0x0000` | `0x4000` | ROM-invoked flash BSL, signature/target check and slot selection |
| application A | `0x4000` | `0x5800` | running or last-known-good image plus manifest/signature |
| application B | `0x9800` | `0x5800` | inactive/pending image plus manifest/signature |
| duplicated boot state | `0xF000` | `0x1000` | version, compatibility, pending state and bounded fault metadata |

CI warns when a linked application exceeds 20 KiB and rejects a packaged slot
above 22 KiB. The exact source is
[`config/mspm0c1106_memory.json`](../config/mspm0c1106_memory.json). The boot
manager reads back the inactive slot, verifies it locally, starts it pending
under watchdog and commits only after its own self-test plus the global S3
commit. Blank flash, recovery and update failure keep pack release and all TX
permits fail-closed.

## Physical recovery

- S3: product USB plus UART0/RESET/BOOT.
- C5: data-only USB plus UART0/RESET/BOOT.
- RP2354B: data-only USB plus SWD/RUN/USB_BOOT.
- each C1106: NRST, SWDIO/SWCLK, UART1 and isolated fixture power.

Service USB never powers the product. Recovery can erase firmware and replace
owner keys, but it cannot synthesize `RUN`, service the independent TPS3435 or
clear the hardware `FAULT_KILL` latch.

Release qualification covers power loss during every erase/write/state
transition, wrong-target and corrupt signatures, incompatible protocols,
pending timeouts, both-slot corruption, forced allocation failure and physical
recovery from erased devices.
