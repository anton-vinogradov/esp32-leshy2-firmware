# Leshy2 Firmware

> **Target product document.** This page describes reviewed software behavior
> independent of a selected electronic architecture. See the
> [current engineering state](docs/status/current-state.md).

- [Русская версия](README.ru.md)
- [Hardware target product](https://github.com/anton-vinogradov/esp32-leshy2)
- [Canonical cross-repository review ledger](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review)

## Finished-software intent

Leshy2 firmware turns the future portable hardware into an autonomous all-in-one
radio/wireless communication, observation, diagnostic and authorized-research
instrument, including wireless/contact credential tools. Navigation, storage,
maintenance and compute support those results; they are not general-purpose
peripheral-computer scope. Hardware reachability never implies permission to act.

Compute count, target images, HAL ownership, IPC transports, pins and component
drivers remain open. The former three-domain `ARC-0001/PKG-0001/SYN-3A` is a
candidate study only after hardware `DEC-0032`.

## Three functional levels

1. **Main** — everyday tools, reception, diagnostics, navigation, maintenance
   and legitimate communications.
2. **Lab** — passive, defensive and bounded security-research tools.
3. **Lab → Controlled Zone** — dangerous active/disruptive tools. Every entry
   requires a fresh non-suppressible warning; every action separately checks
   authorized target and/or isolated/conducted environment requirements.

Leaving the level, lock, timeout, reset, watchdog, update, STOP or loss of a
required accessory invalidates every affected arm and lease. Initial setup also
requires explicit acceptance of the non-aggression pledge.

## Architecture-independent software contracts

- Every transmitter starts off after power, reset, brownout, watchdog or update.
- Initial TX uses a conservative per-path profile; maximum available power
  requires an explicit current-scenario choice and is never a restored default.
- Commanded TX, observed current, device-reported TX and independent actual-TX
  evidence remain distinct states.
- Physical STOP dominates UI, IPC and storage; releasing it never restores a
  prior target/channel/power/session.
- Each future physical radio owner enforces timing, bounded queues, lease expiry
  and local safe-off; IPC cannot be remote raw GPIO.
- Normal updates use owner-authorized signed images, target validation and
  rollback. Keys, reproducible/offline build/signing and developer firmware
  remain owner-controlled; irreversible lockdown is optional and separate.
- Every selected programmable target remains independently recoverable and
  diagnosable without a healthy peer or application image.
- Three full-function nRF24 paths retain independent PTX/PRX and support every
  simultaneous `3R/1T2R/2T1R/3T` mix without automatic peer standby or hidden
  RX gaps; exact mixed-RF sensitivity remains a measured profile gate.
- Wi-Fi 2.4/5, IEEE 802.15.4, native BLE, packet Sub-GHz, analog voice,
  broadcast/audio, IR and qualified external GNSS/LoRa/NFC profiles retain
  their reviewed capability and safety boundaries.
- The external iButton/1-Wire profile separates ordinary owned devices, Lab
  credential reading and individually armed Controlled-Zone emulation/write;
  accessory presence never authorizes or starts an operation.
- The accessory manager treats M5 Unit A/B/C/custom and the full U214-compatible
  Cap as the primary low-rate tier, with a profile-derived high-throughput tier
  only for accepted raw SDR and external RF/credential-analysis workloads. It
  never advertises generic host or blanket M5-Bus compatibility or substitutes
  a command link for a raw-data path.
- Unknown hardware, firmware or accessory identity is visible and fails closed;
  it never silently selects a permissive compatibility mode.
- The base has no permanent text keyboard. A declared rare/long text workflow
  may use a locally paired owner phone with an authenticated, visible and
  revocable session. Incoming text and consequences are shown on Leshy2; the
  phone cannot accept the pledge, enter Controlled Zone, arm/confirm TX or
  destructive actions, change trust or authorize recovery.
- The renderer uses dirty/tiled, preemptible display updates rather than a
  video-like full-frame target. Critical and first menu feedback is visible
  within 100 ms under admitted concurrent load; waterfall coalescing/drop is
  explicit and never silently trades away raw radio/audio capture.
- The optional external IMU profile records timestamped raw accel/gyro,
  pitch/roll, short-term relative rotation and motion quality only when a
  qualified indexed mount/axis transform is active. Missing or stale IMU data
  invalidates pose metadata, not raw RF records or safety; six-axis data is
  never advertised as absolute heading or RF bearing.
- Generic USB host, personal FIDO/U2F authentication and 6 GHz/Wi-Fi 6E are
  outside the product mission. High-throughput transport exists only when
  derived by a concrete accepted RF/SDR profile.
- BadUSB/DuckyScript is a release-optional Controlled-Zone software exception
  over the existing USB device/service path. It adds no hardware/architecture
  requirement and cannot block the radio/key release, but still requires fresh
  authorization, isolated execution, parser/USB review and HIL before shipping.

## Build boundary

The future architecture may produce one or several images. It must publish an
explicit compatibility manifest containing hardware/profile identities,
protocol ranges, hashes, rollback indices and required migrations. Shared code
may define policy vocabulary, package formats and test vectors but cannot erase
physical ownership or safety boundaries.

## Development state

Firmware implementation has not started. Repeated hardware G2 review is closed;
hardware `DEC-0044/NIF-0001/REV-0004L` select `G2F-3I` as the leading reviewed
paper map with independent radio buses/IPC and bounded display+SD sharing.
Hardware `DEC-0045/0046` additionally require one active top-level signal group,
the three-radio `SG-N24` full mix and verified quiet states for every unused
interface. `DEC-0047/N24H-0001` use the ordered second ESP32-DIV as an early
`L0 DIV↔DIV` pre-HIL observer; final pass requires `T1` on the exact Leshy2
revision. `DEC-0048` fixes three nRF IPEX→external-SMA paths and external SMA
for every onboard antenna endpoint; firmware records port/antenna identity in
the TX manifest. Hardware `ANT-0001` now proves separate Si4732 FM/SW and
AM/LW antenna domains; `DEC-0049` accepts nine labelled SMA and separate
`RX-FM/SW`/`RX-AM/LW` paths. Firmware does not merge their identities, and
AM/LW accepts only a manifest-qualified loop/pod profile. Hardware
`RFH-0001/FND-0057` forbid treating generic Ebyte `IPX` as proven U.FL/MHF I;
the specimen-fit/VNA gate remains mandatory. `RFH-0002/REV-0004S` show RP-SMA
as typical for native Wi-Fi, standard SMA in Ebyte/nRF and both polarities in
sub-GHz. `IMP-0042` therefore compares uniform standard SMA with a bounded
`2 RP-SMA + 7 standard SMA` option without changing runtime identities.
`FND-0056` also replaces
the false SA518 `SQ` pin with a qualified-only `VOICE_ACTIVITY` input and keeps
its UPDATE recovery fixture open. No observer is a
base-product dependency. Its firmware
consequences are recorded in
[`ARC-0002`](docs/architecture/ARC-0002-g2f-3i-runtime-input.md), but physical
RF, exact peripherals, power and HIL must close before the adapted legacy
physical mockup. Reviewed physical co-design, whole-device optimality,
conceptual placement and a new atomic architecture decision must precede
target-specific runtime/HAL/toolchain work.
The former [`ARC-0001`](docs/architecture/ARC-0001-three-domain-runtime-contract.md)
is retained only as candidate/reference evidence.
