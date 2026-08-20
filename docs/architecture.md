# Leshy2 firmware architecture

[Home](../README.md) · [Русский](architecture.ru.md) · [Hardware](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/hardware.md)

## Runtime domains

| Image | Physical owner | Local responsibilities | Independent recovery |
|---|---|---|---|
| S3 | `ESP32-S3-WROOM-1U-N16R8` | Application, menu, display, microSD, audio, BLE/Wi-Fi | Product USB, UART0, RESET, BOOT |
| C5 | `ESP32-C5-WROOM-1U-N8R8` | Native 2.4/5 GHz, IEEE 802.15.4, IR | Data-only USB, UART0, RESET, BOOT |
| RP | `SC1512-A4` (RP2354B) | nRF24 ×3, CC1101, SA518, U214 | Data-only USB, SWD, RUN, USB_BOOT |
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

### Unattended safety and fault display

- S3 publishes a bounded heartbeat and one short-lived lease naming the active
  signal group. The safety controller independently compares that lease with
  `ANY_TX_AON_N` and the eight per-path evidence bits.
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
