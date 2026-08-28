# Leshy2 firmware architecture

[Home](../README.md) · [Русский](architecture.ru.md) · [Hardware](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/hardware.md)

## Current R2 runtime boundary

The machine projection in
[`config/h0_r2_hardware_contract.json`](../config/h0_r2_hardware_contract.json)
is generated from the reviewed hardware H0-R2 source and binds its SHA-256.
It is the current firmware input; the R1 contract below is regression evidence.

| Image | Physical owner | Current R2 responsibility |
|---|---|---|
| S3 | `ESP32-S3-WROOM-1U-N16R8` | application, direct UI/touch/encoder/USB, direct 32-MHz i8080-8 display TX and independent analog-FPV camera RX |
| C5 | `ESP32-C5-WROOM-1U-N8R8` | native 2.4/5-GHz Wi-Fi, IEEE 802.15.4 and IR |
| RF RP · rear | `SC1512-A4` | CC1101, VHF/UHF voice, FM/AM/SW/LW/Airband, audio, FPV, M5 and U214/LoRa Cap |
| Hub RP · front | second `SC1512-A4` | S3/C5/rear-RP fan-out, microSD and three complete concurrent nRF24 paths |
| Pack | `MSPM0C1106SDGS20R` | cell admission and protected shutdown |
| Safety | second `MSPM0C1106SDGS20R` | watchdog, thermal supervision, TX evidence/leases and `FAULT_KILL` |

```mermaid
flowchart TD
  S3["S3 · direct UI/display/video"] <-->|"40-MHz quad-SPI + alert"| HUB["front Hub RP · fan-out/storage/nRF24"]
  HUB <-->|"20-MHz 4-bit SDIO"| C5["C5 · native radio/IR"]
  HUB <-->|"20-MHz SPI + alert"| RF["rear RF RP · RF/audio/expansion"]
  HUB <-->|"400-kHz fail-closed I²C"| PACK["Pack MSPM0"]
  HUB <-->|"400-kHz fail-closed I²C"| SAFE["Safety MSPM0"]
```

The S3-Hub link carries control and selected data, never display pixels or
analog-video frames. Hub-local microSD and three nRF24 islands do not contend
with the display; rear audio uses bounded full-duplex transport below 0.4 MB/s.
Button edges terminate on the S3-local
`TCA9539PWR`; encoder A/B remain direct PCNT inputs. The first visible response
target remains 20 ms under qualified concurrent load.

The display and camera use the separate LCD TX and camera RX units concurrently.
The H1-R2.25 physical orientation points the display flex toward the antenna edge;
the S3 display/touch driver therefore applies one 180-degree transform to both
ST77922 memory addressing and touch coordinates.
The exact M1 map defines all 80 contacts: 25 live signals, 14 main-power, 2 AON,
25 returns and 14 NC reserves. M1 is electrical/alignment-only; enclosure stops,
anti-shear datums and PCB capture carry impact and bending loads.

`BROADCAST_RX` is rear-RP-owned and mutually exclusive with other top-level signal
groups. Airband AM maps 118–137 MHz to Si4732's 6–25-MHz FMI range using a
fixed 112-MHz low-side LO. Rear RP GP35 is fail-low `AIR_RX_EN`; GP36 selects direct
FM/SW or converted Airband and resets to direct FM/SW. Included behavior is AM
voice, 25/8.33-kHz plans, scan/banks, recording, activity history and downstream
ACARS 2400 decode. Airband TX, VDL2, wideband spectrum capture and certified
VOR/ILS are not claimed.

Pack state and the Safety heartbeat/lease/fault mailboxes use dedicated front-Hub
GP43/44 I²C. Safety still owns watchdog service and asynchronous `FAULT_KILL`;
an IPC hop cannot create permission or suppress a local fault. The complete
[F0-R2 contract foundation is reviewed](f0-product-contracts-report.md);
the [F1-R2 portable behavior is also reviewed](f1-portable-cores-report.md).
F2-R2 now rebaselines the six target projects and generated BSP boundary.

<details>
<summary><strong>Retained R1 architecture — not the current physical topology</strong></summary>

## Historical R1 runtime domains

| Image | Physical owner | Local responsibilities | Independent recovery |
|---|---|---|---|
| S3 | `ESP32-S3-WROOM-1U-N16R8` | Application, menu, display, microSD, audio, BLE/Wi-Fi | Product USB, UART0, RESET, BOOT |
| C5 | `ESP32-C5-WROOM-1U-N8R8` | Native 2.4/5 GHz, IEEE 802.15.4, IR | Data-only USB, UART0, RESET, BOOT |
| RP | `SC1512-A4` (RP2354B) | nRF24 ×3, CC1101, SA818S-V/U selection, Cap Bus | Data-only USB, SWD, RUN, USB_BOOT |
| Pack | `MSPM0C1106SDGS20R` | Two-cell admission and local fail-closed power state | NRST, SWD, UART1 and isolated fixture power |
| Safety | second `MSPM0C1106SDGS20R` | Heartbeats, TX leases, three thermal zones, physical TX evidence and retained fault record | NRST, SWD, UART1 and isolated fixture power |

S3 coordinates the user scenario but does not replace local owners. C5 and RP
meet radio deadlines locally, revoke TX when a lease disappears and report
actual path state. The pack controller exposes only bounded read-only state and
fault information to S3; S3 cannot command it to accept an unsafe cell pair.
The safety controller is independent of the pack controller, owns the private
TX-evidence bus and is the only device allowed to service the external
`TPS3435CAKAGDDFR` 1.6-second timeout watchdog.

## Inter-processor messages

`L2IP v1` gives the two high-rate links one typed application contract. Its
32-byte header carries source, target, message and correlation IDs, protocol
version, payload length, receipt-relative deadline and separate CRC-32C values
for header and payload. State-changing requests are duplicate-safe. Completion
means a typed result proving the reached local state, never just a successful
bus transfer or queue insertion.

| Link | Physical transport | Wire unit | Required behaviour |
|---|---|---|---|
| S3↔C5 | dedicated 1-bit SDIO at 20 MHz | up to one 512-byte packet | ≥1.5 MB/s payload, ≤2 ms control RTT, ≤70% admitted occupancy |
| S3↔RP | dedicated 20-MHz SPI3 plus `RP_ALERT_N` | one full-duplex 512-byte DMA cell | ≥1.5 MB/s payload, ≤250 µs alert-to-read and ≤2 ms control RTT |
| S3↔Pack | `SYS_I2C` target `0x2A` | 32-byte command, 64-byte read-only status | S3 cannot command battery admission; update writes require physical KILL |
| S3↔Safety | `SYS_I2C` target `0x2B` | 32-byte command, 64-byte read-only status | only session heartbeat, one bounded group lease and KILL-only update are writable |

The C5 link uses Espressif's FIFO/register/interrupt slave transport. The exact
module lot must contain **ESP32-C5 revision v1.0 or later**: Espressif documents
SDIO as unsupported on revision v0.1. The selected four wires keep GPIO13/14
available for native recovery USB. The RP link uses the RP2354B SPI1 slave DMA;
S3 clocks a side-effect-free `NOP` whenever only upstream data is pending.
[Espressif SDIO slave](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-reference/peripherals/sdio_slave.html) ·
[C5 hardware requirement](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/schematic-checklist.html) ·
[RP SPI/DMA API](https://www.raspberrypi.com/documentation/pico-sdk/hardware.html)

Safety, control, interactive, telemetry and bulk queues have decreasing
priority. Bulk is credit-controlled and cannot borrow safety/control buffers;
stale waterfall telemetry may be dropped with an explicit sequence gap. A
link reset, corrupt frame, incompatible schema or expired deadline revokes the
local TX lease. C5 and RP therefore stop locally even if S3 can no longer send
a stop command.

S3 publishes a safety heartbeat every 50 ms; a 200-ms gap is a fault. A TX
lease lasts at most 100 ms and is renewed no slower than every 40 ms. The
safety loop runs within 5 ms and unexpected physical evidence is faulted
within 10 ms. Only a healthy safety loop services the independent 1.6-second
watchdog. Exact layouts, message IDs, mailbox fields, update messages and test
vectors are machine-readable in
[`config/interdomain_protocol.json`](../config/interdomain_protocol.json).
The cross-repository controller, transport, pin, signal-group, safety-timing
and LoRa-profile boundary is frozen in
[`config/hardware_integration_contract.json`](../config/hardware_integration_contract.json).

## Scheduling and quiet states

One top-level signal group is active at a time. The nRF24 group itself is the
exception: all three radios operate concurrently in every required RX/TX mix.
Broadcast reception is represented explicitly as the receive-only
`BROADCAST_RX` group; it never hides under `NONE` merely because it has no TX
evidence bit. `NONE` means every signal interface is quiet.
A group transition is transactional:

1. stop accepting new work and finish the bounded current transfer;
2. revoke TX and wait for absence of actual-TX evidence;
3. disable the old group's interface, power and output drivers;
4. verify discharge and quiet state;
5. power the new group, verify identity and only then grant a lease.

Display i8080 DMA, microSD sessions and inter-processor links use bounded quanta.
They do not hold CPU or bus resources long enough to miss a radio deadline.

## User interface

- The main model is a menu, status bar and tool workspace.
- The waterfall appends one new row or column and scrolls the visible region;
  menus and indicators update only dirty rectangles.
- The first local response appears within 100 ms even during radio, audio or
  storage activity.
- The encoder uses hardware PCNT; the key matrix is interrupt-driven rather
  than continuously polled.
- `PTT` is a separate held voice-TX request. The maintained `RUN/KILL` switch
  is asynchronous and always dominates. Only a physical `KILL`→`RUN` edge can
  clear a releasable fault; software cannot repeat or synthesize it.

## Radio and IR

Each radio service exposes scan/receive, constrained transmit, identity,
profile configuration, actual-TX evidence, fault and quiet state. The regional
profile defines available bands and conservative power; maximum power is never
the default.

The three nRF24 radios have independent queues, SPI resources, IRQs and
evidence. Their group scheduler coordinates them without turning mixed mode
into a sequential simulation. The IR service concurrently receives a
demodulated 38-kHz stream and measures a 30–60-kHz carrier; transmit requires
hardware `RUN_PERMIT` qualification and optical evidence.

## Storage, audio and expansion

- microSD power exists only for an active session. Clean eject drains writes
  and unmounts first; unexpected removal marks the missing tail as incomplete.
- The audio graph explicitly selects microphone or radio RX for capture and
  speaker or a CTIA headset for playback. The `SJ-43504-SMT-TR` tip switch
  reaches detect-only `slow_io.P02`: high means absent, while low or an
  unreadable state immediately silences the speaker. Firmware never drives
  this line.
- Dedicated `TCA9534APWR` P0 at collision-free I²C address `0x39` selects the
  headset microphone low or the internal microphone high. Its input/reset
  state is physically pulled to the internal microphone. Stable insertion
  defaults to the headset microphone; a user may retain the internal
  microphone for an ordinary TRS headphone plug. Removal restores the reset
  default before speaker playback can resume. P1–P7 are pulled, interrupt-
  capable local reserves rather than floating pins.
- A dedicated `TCA9534A` at `0x3A` selects VHF or UHF. Hardware one-hot PD and
  three `TMUX1136` paths keep UART, PTT/AUDIO_ON and AFOUT/MIC_IN on the same
  selected SA818S module. PTT is never inferred from audio samples or
  microphone choice; `SA818S-CE` may replace only UHF after qualification and
  then firmware disables 470–480 MHz.
- The Cap Bus and M5 Unit use independent `OFF → STARTING → IDENTIFY → ACTIVE →
  STOPPING` states and a latch-off fault. An unknown module profile never gains
  power or dangerous commands automatically.
- The built-in S3, C5, nRF24, CC1101, voice and IR transmit paths have physical
  evidence. The stock U214 remains receive/GNSS-only because contact 5 is
  `5V_OUT`, not RF proof. Exact signed `LESHY2-LORA-CAP-01-EU868` and
  `LESHY2-LORA-CAP-01-US915` profiles use `NiceRF LoRa1262-868/915`, a
  `24AA02UIDT-I/OT` identity anchor and the same contact as open-drain
  `EXT_TX_EVIDENCE_N`. Their TX lease exists only after the regional frequency
  profile, UID binding, final external RF feed and 10–18-ms bit-8 pulse have
  passed qualification. Identity never substitutes for authorization or live
  evidence. Generic M5 Unit TX still requires its own physical evidence profile.
- A phone acts only as local text input and data exchange; it cannot confirm a
  Controlled-Zone action.

## Safety and update

A potentially dangerous function requires the appropriate UI level, an
authorized target/profile, preview, separate arming and a time-bounded lease.
Evidence confirms execution but never creates permission.

### Unattended safety and fault display

- No battery-autonomy or uptime-hours claim is made. Extended operation uses a
  qualified USB-PD source; 24 and 48 hours are F10 validation durations.
- `Settings > Safety > Full self-test` selects every 24 hours, every 48 hours
  by default, or warned startup-only proof. `Check now` remains available.
- Only the local physical UI may stage this setting, and it becomes active only
  after the next physical `KILL`→`RUN` proof. It cannot alter watchdog,
  thermal, power-fault or TX-lease enforcement.
- The safety MSPM0 owns the monotonic active-session deadline. At expiry it
  revokes leases, requests quiet, retains `FAULT_PLANE_PROOF_DUE`, asserts the
  fault request and requires physical `KILL`→`RUN` recovery.
- S3 publishes a bounded heartbeat and one short-lived lease naming the active
  signal group. The safety controller independently compares that lease with
  `ANY_TX_AON_N` and nine used bits of the 16-bit `TCA9535PWR` evidence register
  at private address `0x20`.
- The safety controller services the TPS3435 deadline only while its own loop,
  the S3 heartbeat, the active lease, power-fault input and three NTC channels
  are healthy. TPS3435 timeout or any controller fault asynchronously latches
  `FAULT_KILL`.
- The retained record contains primary source, affected zone or signal group,
  measured value, limit, evidence mask, rail state and monotonic event ID.
- C5 and RP remain reset after a fault. S3 may enter a signed, read-only
  fault-viewer image only while the UI/display thermal zone and main rail are
  safe. The screen states the cause, what was disabled and that the operator
  must move `RUN` to `KILL` before attempting restart.
- UI/display overtemperature or unsafe display power turns the screen off. The
  AON amber `FAULT` LED and retained record remain; automatic restart is never
  permitted.

The user installs one bundle, not five unrelated files. Its signed manifest
binds every image to the product, hardware range, physical target, build ID and
compatible inter-domain protocol range. The updater accepts either a release
root or a locally enrolled owner root.

Installation requires physical `RUN=KILL`, quiet TX evidence and qualified
stable power. All inactive images are written and read back before any target
is activated. Pack, Safety, C5 and RP then perform their local pending boot and
self-test while the old S3 remains coordinator; S3 activates last. A target
failure restores its local last-known-good image, and a failed bundle returns
already advanced peers to the compatible previous set.

The mechanism is deliberately open. Irreversible secure-boot, anti-rollback
and debug locks are not enabled by default. Signatures reject substituted
normal update packages; they do not take physical recovery away from the
owner. USB/UART/SWD recovery may replace all images and keys, but cannot bypass
`RUN/KILL`, the independent watchdog or `FAULT_KILL`.

The exact flash, RAM, slot, update and recovery contracts for all five images
are documented in the [memory contract](memory.md).

</details>
