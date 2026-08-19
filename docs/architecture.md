# Leshy2 firmware architecture

[Home](../README.md) · [Русский](architecture.ru.md) · [Hardware](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/hardware.md)

## Runtime domains

| Image | Physical owner | Local responsibilities | Independent recovery |
|---|---|---|---|
| S3 | `ESP32-S3-WROOM-1U-N16R2` | Application, menu, display, microSD, audio, BLE/Wi-Fi | Product USB, UART0, RESET, BOOT |
| C5 | `ESP32-C5-WROOM-1U-N8R8` | Native 2.4/5 GHz, IEEE 802.15.4, IR | Data-only USB, UART0, RESET, BOOT |
| RP | `SC1512-A4` (RP2354B) | nRF24 ×3, CC1101, SA518, U214 | Data-only USB, SWD, RUN, USB_BOOT |
| Pack | `MSPM0C1104SDGS20R` | Two-cell admission and local fail-closed power state | Keyed fixture interface and reset |

S3 coordinates the user scenario but does not replace local owners. C5 and RP
meet radio deadlines locally, revoke TX when a lease disappears and report
actual path state. The pack controller exposes only bounded read-only state and
fault information to S3; S3 cannot command it to accept an unsafe cell pair.

## Inter-processor messages

- S3↔C5 uses dedicated 1-bit SDIO for data and events.
- S3↔RP uses dedicated SPI3 plus a separate alert.
- Every message carries a type, version, length, sequence, deadline and target
  owner.
- Completion means a verified local state-machine transition and matching
  evidence, not merely queue insertion.
- An incompatible version, corrupt frame, timeout or peer reset closes the
  active lease and leaves TX off.

## Scheduling and quiet states

One top-level signal group is active at a time. The nRF24 group itself is the
exception: all three radios operate concurrently in every required RX/TX mix.
A group transition is transactional:

1. stop accepting new work and finish the bounded current transfer;
2. revoke TX and wait for absence of actual-TX evidence;
3. disable the old group's interface, power and output drivers;
4. verify discharge and quiet state;
5. power the new group, verify identity and only then grant a lease.

Display QSPI, microSD sessions and inter-processor links use bounded quanta.
They do not hold CPU or bus resources long enough to miss a radio deadline.

## User interface

- The main model is a menu, status bar and tool workspace.
- The waterfall appends one new row or column and scrolls the visible region;
  menus and indicators update only dirty rectangles.
- The first local response appears within 100 ms even during radio, audio or
  storage activity.
- The encoder uses hardware PCNT; the key matrix is interrupt-driven rather
  than continuously polled.
- `PTT` is a separate held voice-TX request. `STOP` is asynchronous and always
  dominates. `RE-ARM` never repeats an old command.

## Radio and IR

Each radio service exposes scan/receive, constrained transmit, identity,
profile configuration, actual-TX evidence, fault and quiet state. The regional
profile defines available bands and conservative power; maximum power is never
the default.

The three nRF24 radios have independent queues, SPI resources, IRQs and
evidence. Their group scheduler coordinates them without turning mixed mode
into a sequential simulation. The IR service concurrently receives a
demodulated 38-kHz stream and measures a 30–60-kHz carrier; transmit requires
hardware STOP qualification and optical evidence.

## Storage, audio and expansion

- microSD power exists only for an active session. Clean eject drains writes
  and unmounts first; unexpected removal marks the missing tail as incomplete.
- The audio graph explicitly selects microphone or radio RX for capture and
  speaker or headphones for playback. SA518 PTT is never inferred from audio
  samples.
- U214 and M5 Unit use independent `OFF → STARTING → IDENTIFY → ACTIVE →
  STOPPING` states and a latch-off fault. An unknown module profile never gains
  power or dangerous commands automatically.
- A phone acts only as local text input and data exchange; it cannot confirm a
  Controlled-Zone action.

## Safety and update

A potentially dangerous function requires the appropriate UI level, an
authorized target/profile, preview, separate arming and a time-bounded lease.
Evidence confirms execution but never creates permission.

An update package contains signed target-bound images, a shared manifest and
compatible protocol versions. It writes inactive slots and commits only after
boot health succeeds; otherwise it rolls back. Independent recovery for every
domain always ends TX-off.

Owner keys are supported alongside release keys. Signature verification
protects image integrity and authorship without preventing modification of the
open source.
