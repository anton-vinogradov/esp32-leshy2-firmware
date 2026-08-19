# Firmware memory contract

[Home](../README.md) · [Русский](memory.ru.md) · [Runtime architecture](architecture.md) · [Hardware memory wiring](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/memory.md)

The S3 image targets the exact `ESP32-S3-WROOM-1U-N16R8`: 16 MB flash and
8 MB octal PSRAM. PSRAM ECC is mandatory in production, leaving at least
7.5 MB usable while retaining the module's −40…+85 °C operating envelope.

This is fixed in
[`config/sdkconfig.defaults.esp32s3`](../config/sdkconfig.defaults.esp32s3): a
production build must contain `CONFIG_SPIRAM_ECC_ENABLE=y`, octal mode, boot
initialization and an 80-MHz PSRAM clock. CI treats these values as build inputs
and rejects an image if any one is absent or overridden.

## 16-MB flash layout

Both executable slots are 7 MiB, so a failed update never destroys the last
known-good image. CI warns above 6 MiB and rejects an application image above
`0x6C0000` (6.75 MiB), retaining 256 KiB of per-slot margin for image growth,
alignment and signing metadata.

CI does not duplicate these limits by hand:
[`config/s3_image_limits.json`](../config/s3_image_limits.json) is consumed by
[`tools/check_s3_image_size.py`](../tools/check_s3_image_size.py). A new feature
cannot silently shrink the second OTA slot.

| Partition | Offset | Size | Purpose |
|---|---:|---:|---|
| bootloader + table | `0x000000` | through `0x009000` | ROM-loaded signed boot path and partition table |
| `nvs` | `0x009000` | `0x006000` | bounded configuration and calibration |
| `otadata` | `0x00F000` | `0x002000` | redundant active/pending/rollback state |
| `phy_init` | `0x011000` | `0x001000` | radio calibration seed |
| `coredump` | `0x012000` | `0x010000` | bounded crash record |
| `nvs_keys` | `0x022000` | `0x003000` | encrypted-NVS key material when enabled |
| boot reserve | `0x025000` | `0x00B000` | boot/security growth; never used for product assets |
| `ota_0` | `0x030000` | `0x700000` | running or last-known-good S3 image |
| `ota_1` | `0x730000` | `0x700000` | inactive update/rollback S3 image |
| `rescue_fs` | `0xE30000` | `0x100000` | minimal fault-viewer fonts, schema and recovery resources |
| `eventlog` | `0xF30000` | `0x080000` | bounded retained diagnostic ring |
| future reserve | `0xFB0000` | `0x050000` | migration space; not silently consumed |

[`config/partitions_16m.csv`](../config/partitions_16m.csv) is the machine source
for this table; the documentation is not a second competing layout.

An update is written only to the inactive slot, verified against its target and
owner/release key, booted as pending and committed only after bounded health
checks. Failure, watchdog reset or incompatible inter-domain protocol rolls
back. Native USB, UART0 and the keyed service header remain independent of both
OTA slots.

## Why the executable image is bounded

S3 does not contain the firmware for the three nRF24 radios, CC1101, SA518,
U214 or IR: those real-time radio functions execute on RP and C5. The S3 image
contains the application, UI, display/storage/audio, BLE/Wi-Fi and inter-domain
protocols. Fonts beyond the minimal fault viewer, recordings, maps,
dictionaries, captures and replaceable UI packs are versioned microSD data,
not executable code.

The 6-MiB threshold is therefore an early measurement gate, not a guessed final
size. At that point CI retains a map/size report and first requires removal of
accidentally linked assets and duplicate libraries. Only measured production
code that remains too large after that work can reopen the flash layout for a
separate architecture review; rollback capacity is never taken silently.

## Runtime RAM

- Internal SRAM is reserved first for ISR code/data, DMA-capable buffers,
  scheduler state, inter-domain links and stacks that must remain available
  while PSRAM is busy.
- ECC-protected PSRAM holds the UI scene, dirty rectangles, waterfall history,
  decoded-event working sets, audio queues and caches.
- Every large pool has a declared maximum and allocation failure path; radio,
  safety and fault-viewer operation never depends on opportunistic cache space.
- RF captures, recordings, maps, dictionaries and replaceable UI asset packs
  live on microSD. They are versioned data, not linked into either executable.

Before UI or radio startup, a self-test confirms that ECC is enabled, at least
`0x780000` bytes of PSRAM are usable, and a bounded scratch block passes a
write/read test. Failure cannot enter normal operation: S3 retains the diagnostic
cause and enters its restricted fault/recovery path.

Prototype acceptance includes the production configuration, startup self-test,
a measured usable-PSRAM floor of 7.5 MB,
full-duplex audio plus display/storage/radio-event stress, forced allocation
failure, both-slot rollback and recovery with erased or corrupt application
slots.
