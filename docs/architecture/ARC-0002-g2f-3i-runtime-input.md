# ARC-0002 — G2F-3I runtime input

- Status: **reviewed paper-layout input; target firmware architecture remains blocked**
- Date: 2026-08-17
- Canonical hardware decision: [`DEC-0044`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0044-delegated-noninterference-layout.md)
- Hardware artifact: [`NIF-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/NIF-0001-digital-noninterference-layout.md)
- Exact generated map: [`G2F-pin-ledger`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/generated/G2F-pin-ledger.md)
- Reviewed principled pinout: [`PIN-0003`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PIN-0003-g2f-3i-principled-pinout.md), [`generated atlas`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/generated/G2F-3I-principled-pinout.md)
- Working-design decision: [`DEC-0051`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0051-principled-pinout-as-working-design.md)
- Signal groups: [`DEC-0045`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0045-one-active-signal-group.md)
- Quiet states: [`DEC-0046`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0046-unused-interface-quiet-by-default.md), [`QST-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/QST-0001-unused-interface-quiet-states.md)
- nRF RF acceptance: [`DEC-0047`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0047-qualified-nrf-mix-with-external-observer.md), [`N24H-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/N24H-0001-two-device-full-mix-fixture.md)
- nRF module/antenna choice: [`N24M-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/N24M-0001-exact-module-antenna-comparison.md), [`IMP-0040`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/improvements/IMP-0040-three-nrf-module-and-antenna-baseline.md)
- external antenna decision: [`DEC-0048`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0048-external-sma-antenna-bank.md)
- exact antenna count: [`DEC-0049`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0049-nine-dedicated-external-sma-paths.md)
- profiled antenna kit: [`DEC-0055`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0055-profiled-external-antenna-kit.md)
- feed-interface review: [`RFH-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/RFH-0001-module-to-external-sma-interface-review.md)
- exact codec fit: [`AUDIO-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/AUDIO-0001-es8311-exact-electrical-fit.md), [`REV-0005B`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005B-es8311-digital-fit-and-analog-gap.md)
- complete audio-path review: [`AUDIO-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/AUDIO-0002-complete-audio-path-comparison.md), [`FND-0067`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0067-audio-source-select-and-reset-bypass.md), [`REV-0005C`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005C-complete-audio-path-prerequisites.md)
- accepted audio topology: [`DEC-0054`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0054-fail-safe-complete-audio-path.md), [`REV-0005D`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005D-audio-decision-propagation.md)
- service/IPC amendment: [`DEC-0059`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0059-full-service-over-1bit-sdio.md), [`REV-0005L`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005L-full-service-1bit-sdio-propagation.md)

## Boundary

This document records the firmware consequences of the leading reviewed
**paper** layout. It does not start a toolchain, freeze three production
images, select exact peripheral drivers or restore the superseded `ARC-0001`
as target. Physical RF, exact parts/power/mechanics and HIL can still remap the
architecture before the atomic decision.
Hardware `DEC-0051` makes this reviewed projection visible as the current G3
working design. It does not convert the input into a frozen firmware HAL or G7
architecture.

## Candidate runtime domains

| Domain | Candidate local ownership | Dedicated transports/resources | Local invariants |
|---|---|---|---|
| S3 | product policy/UI, display, audio, microSD, native BLE, Unit profile | SPI3 to RP, 1-bit SDMMC host to C5, SPI2 display+SD scheduler, I²S0, internal I²C0, separate I²C1/UART1/GPIO Unit profile | UI feedback ≤100 ms; storage stalls never block radio leases/queues; native USB + default UART0 + EN/BOOT service |
| C5 | 2.4/5 GHz Wi-Fi, IEEE 802.15.4, dual-path IR RX and IR TX | exclusive 1-bit SDIO slave to S3; direct IR RMT/evidence | local RF/IR queues, lease expiry and safe-off; native USB + UART0 + EN/BOOT/strap service |
| RP2354B | 3×full-function nRF24, CC1101, voice/PTT and U214 LoRa/GNSS | four independent PIO0 compatibility-radio buses, PIO1 U214 SPI, UART1 GNSS, isolated U214 I²C, hardware SPI1 to S3 | direct IRQ/GDO/BUSY/PTT; no peer-radio bus wait; USB+SWD+RUN+BOOTSEL recovery |

The exact RP map uses the real B-package PIO base rule: PIO0 and PIO1 select
the `GPIO16..GPIO47` window, and every PIO data pin is in `GPIO30..GPIO46`.
The hardware validator also locks the fixed mux sets for S3 USB/UART0, C5
1-bit SDIO/native USB, and RP SPI1/UART0/UART1/I²C0; firmware must not remap
these as generic GPIO-matrix choices. The M5 Unit UART profile uses UART1 on
GPIO7/8 so it cannot create a second branch on the permanent S3 UART0 service
route.

Persistent capacity is budgeted before runtime implementation: RP uses 5/12
PIO state machines and 13/16 DMA channels; S3 uses 3/5 GDMA TX and 3/5 GDMA RX
channels. The reserves are not permission for an unreviewed driver to claim a
permanent channel: any new fixed DMA consumer changes the upstream contract.
The quiet-state decision also consumes RP GPIO15/GPIO23 for common nRF and CC
power gates and C5 GPIO4 for the IR frontend gate. Direct free GPIO reserve is
later reduced by `DEC-0052`, which consumes S3 GPIO41/GPIO42 for QSPI D2/D3.
After `DEC-0054` consumes S3 GPIO6 for `AUDIO_ARM`, it is S3=1, C5=1 and
RP=0; firmware cannot invent another direct RP
control. Hardware `PIN-0003/REV-0004V/0004X` derive these figures from the
machine source: S3 is `32 used / 3 reserved / 1 free`, C5 is `14/6/1`, RP is `48/0/0`,
and the slow plane is `24/0/0` after `FND-0067` assigns the previously omitted
ordinary `RX_AUDIO_SOURCE_SEL` to P27. The previously published C5/RP reserve
was stale and is corrected by `FND-0059`. After `DEC-0059`, GPIO43/44 are
permanent UART0 service and GPIO47 is the sole free direct S3 contact; GPIO6
`AUDIO_ARM` remains a normative machine input.

## Mandatory scheduler/queue contract

- `nrf0`, `nrf1`, `nrf2`, `cc` and `u214` are separate event sources with
  independent IRQ timestamps, queues and overflow/drop counters. A shared
  worker may dispatch them, but no lock may serialize physical bus ownership.
- `SG-N24` keeps all three nRF powered and active. Each independently selects
  `PRX` or `PTX`; `3R`, `1T+2R`, `2T+1R` and `3T` must execute concurrently.
  A local TX must not silently put peers in standby or create unreported RX
  gaps. Physical sensitivity limits are profile evidence, not scheduler gaps.
- RP↔S3 SPI must qualify ≥1.5 MB/s framed payload and alert-to-read ≤250 µs;
  control/safety events preempt bulk records and a stalled peer cannot retain
  TX authorization.
- C5↔S3 1-bit SDIO at 20 MHz provides 2.5 MB/s raw and must qualify
  ≥1.5 MB/s framed payload, ≤70% admitted occupancy and ≤2 ms control RTT; it
  exclusively owns the S3 SD/MMC host. Four-bit mode is not a runtime option:
  it is an upstream fallback only after failed HIL and a new service-isolation
  decision.
- Display and microSD deliberately share SPI2. `DEC-0052` assigns direct QSPI
  D2/D3 to S3 GPIO41/42 and replaces stale `256 B` slicing with measured
  `<=1 ms` uninterrupted display occupancy. The scheduler uses separate CS,
  per-device modes/clocks, QSPI only while SD CS is high, derived byte quanta,
  bounded SD commands/data chunks and critical-UI priority. Combined HIL must
  prove shared-D1 high-Z/no-contention, first visible response ≤100 ms, storage
  ≥4.0 MB/s, 1.5 MB/s record and survival of a measured 250 ms card stall.
- Internal I²C contains only slow UI/audio/receiver/control endpoints. PTT,
  radio FIFO/IRQ/GDO/BUSY, hard STOP and timing evidence never wait for it.
  P27 selects the ordinary Si4732-versus-SA518 receive-audio source; it is not
  a safety-deadline line and does not assert PTT.
- U214 external I²C is a separate RP branch behind TCA4307; stuck-low/hot-plug
  cannot stall the internal S3 control bus or Unit profile.

## Signal-group and quiet-state contract

- Exactly one top-level `active_signal_group` exists; boot/reset/fault/STOP
  enters `NONE` with every TX hardware-off. `SG-N24` is one group containing
  three concurrently full-function transceivers, not three mutually exclusive
  groups.
- Before a group switch, firmware revokes leases, proves actual TX off, stops
  controllers/DMA, establishes endpoint-safe levels, isolates/high-Z signal
  paths and only then rail-gates every non-member interface. Wake powers and
  settles the endpoint while I/O remains isolated, then connects safe parked
  signals. Failure or unknown evidence leaves `NONE`; prior TX state is never
  restored.
- S3 UI CPU, RP arbiter, power/fault supervision and required IPC remain system
  planes. Their peripheral clocks run only for bounded transactions, and they
  must pass active-receiver EMI HIL rather than being mislabeled powered-off.
- No background scan, advertising, beacon, periodic service log, accessory
  poll or update check may wake a non-member interface. It requires a visible
  manifest member or an explicit group switch.
- Quiet is verified from rail/current/status/actual-TX evidence where available;
  a successful driver call alone is not proof.

## Firmware HIL that follows from this map

1. every simultaneous three-nRF `3R/1T2R/2T1R/3T` role mix with independent
   channel/rate/address/session, per-source latency, overflow, loss/gap and
   exact RF-profile evidence;
2. RP IPC stress at accepted radio load while display, storage, audio and C5
   traffic run;
3. C5 1-bit IPC framed throughput/occupancy/control-priority/RTT, reset/link-loss
   visibility and TX lease expiry under Wi-Fi/802.15.4/IR load;
4. display+SD scheduling, hot removal and injected 250 ms card stalls;
5. U214 I²C stuck-low/hot-plug fault injection and independent Unit/internal
   bus operation;
6. independent programming/recovery/diagnostics for all three domains;
7. PIO instruction placement, DMA arbitration and SRAM-bank contention under
   the same simultaneous event load; static channel counts alone are not the
   timing proof;
8. every non-member quiet-state transition, no-back-power/fault injection and
   active-receiver desense under maximum valid system-plane traffic.
9. ES8311 address/readback, BCLK-derived simultaneous ADC+DAC, power-off
   no-backfeed and hardware-default analog bypass under reset/watchdog/fault,
   including stale P11/P12 after S3-only reset and proof that arm-low overrides
   both selector requests under accepted `DEC-0054`.

The fixture has two explicitly different evidence levels. Ordered ESP32-DIV
units form `L0 DIV↔DIV` pre-HIL: they validate the manifest/log workflow and
reproduce loss/self-desense, but cannot close Leshy2 RF, rail, antenna or
thermal acceptance. `T1 TARGET` uses two comparable Leshy2 revisions, or a
Leshy2 DUT plus a calibrated conducted/OTA peer, and is the only production
acceptance level.

Both levels use one shared test ID and explicit DUT/observer roles. They
exchange manifests and ordinary packet streams, never remote raw CE/GPIO.
Every device retains its own per-radio logs; results join by test ID, hardware
identity, packet sequence and timestamps with recorded synchronization error.
Role reversal on `L0` measures DIV asymmetry only; role reversal/reproducibility
on `T1` closes target evidence. The observer is HIL equipment, not a runtime
dependency of the base product.

`DEC-0048` makes antenna identity part of every manifest. All onboard paths
terminate at labelled external SMA; nRF0/1/2 map permanently to three distinct
SMA positions through compact IPEX modules and short feeds. Firmware must not
infer a correct antenna merely from connector presence: TX arming records the
selected band/path/antenna profile, permitted power and qualified feed loss.
External M5 accessories report their own antenna identity separately.

`DEC-0055` defines a 12-item field kit for nine simultaneous ports: one shared
exact MPN in quantity two for S3/C5, one in quantity three for nRF0/1/2,
separate CC 315/433/combined-868+915, separate VOICE VHF/UHF, FM/SW whip and
AM/LW loop/pod profiles. Every CC/VOICE profile change disarms TX. Unknown,
mismatched, expired or unqualified identities remain TX-disabled. Availability
is an exact-MPN-selection gate, not a continuously polled architecture input.

Hardware `RFH-0001/FND-0057` distinguishes the verified first-generation
U.FL/MHF I/AMC-compatible S3/C5 connectors from Ebyte's undocumented generic
`IPX` name. Firmware/test manifests must record exact module lot, harness MPN,
length and measured feed identity; they must not merge S3/C5/nRF feeds under
one generic pigtail SKU before the Ebyte specimen-fit/VNA gate. External
standard-versus-RP SMA choice changes assembly metadata, not the nine logical
path identities. Hardware `DEC-0050/REV-0004T` fixes RP-SMA jack/pin only for
`S3-2G4` and `C5-2G4/5`; the other seven use standard SMA jack/socket. The
detachable mates are respectively RP-SMA plug/socket and standard SMA
plug/pin. Exact qualified antenna MPN remains an upstream hardware gate.

Hardware `ANT-0001/REV-0004P` further proves that the Si4732 receiver has two
physical input domains: `FMI` for FM/SW and `AMI` for AM/LW. `DEC-0049` selects
nine dedicated SMA, including separate `RX-FM/SW` and `RX-AM/LW`. Firmware
must retain both logical antenna-profile identities and must not treat a generic
`RX` connector, cable or antenna as compatible with both. The AM/LW profile
accepts only a manifest-qualified direct loop/pod or buffered implementation;
arbitrary long coax remains default-denied.

Hardware `FND-0056` also removes a false SA518 assumption: rev 1.1 has no
dedicated `SQ` contact. The runtime input is therefore neutral
`VOICE_ACTIVITY`; firmware may assign carrier/squelch meaning only after exact
pin-18 `AUDIO_ON` HIL. `PIN-0003` now terminates UART, PTT, activity and the
service breakout on exact SA518 contacts, including pin 17 `UPDATE`; driving
that contact remains forbidden until its documented direction/pull-down
ambiguity passes specimen proof. The same atlas terminates the Si4732 I²C,
reset, interrupt, clock, audio and separate `FMI`/`AMI` routes on exact package
contacts.

## Exact ES8311 runtime boundary

Hardware `AUDIO-0001/REV-0005B` instantiate exact Everest Semiconductor
`ES8311` QFN-20 digital contacts. The later direct arm makes total S3 `32/3/1`:

- `GPIO1/SYS_I2C_SDA` ↔ codec `CDATA` pin 19;
- `GPIO2/SYS_I2C_SCL` → codec `CCLK` pin 1;
- `GPIO15/I2S_BCLK` → codec `SCLK` pin 6;
- `GPIO16/I2S_WS` → codec `LRCK` pin 8;
- `GPIO17/I2S_DOUT` → codec `DSDIN` pin 9;
- `GPIO18/I2S_DIN` ← codec `ASDOUT` pin 7;
- codec `MCLK` pin 2 is unconnected under the reviewed BCLK-derived-clock
  contract;
- codec `CE` pin 20 is fixed high through the documented `10 kΩ` reference
  strap for 7-bit address `0x19`.

`CE` is **not** enable or reset. Slow P10 is external `CODEC_PWR_EN` controlling
a still-unselected quiet-rail switch/sequencer. Firmware must never toggle CE,
must not start I2S clocks before valid power/readback, and must keep both analog
selectors in hardware bypass until the codec and selected analog conditioner
are proven ready. Any codec/readback/DMA/watchdog fault stops I2S, returns
bypass and leaves PTT off.

Exact ADC `MIC1P/MIC1N` and DAC `OUTP/OUTN` are differential. Hardware
`AUDIO-0002/REV-0005C` reviews the complete path rather than treating the
codec as an isolated endpoint:

- ordinary Si4732/SA518 AFOUT analog bypass to PAM8302A remains available with
  the codec off or faulty;
- the selected RX source reaches the ADC only through a high-impedance capture
  branch, because a direct ES8311 tap can load the Si4732 bypass;
- both DAC legs reach both PAM8302A inputs through a dual selector; no central
  differential-to-single-ended amplifier is required;
- DAC-to-SA518 injection has its own selector and roughly 35–45 dB attenuation,
  while electret-to-SA518 remains the default and audio selection never asserts
  PTT;
- P27 selects the ordinary receive source. P11/P12 request codec speaker/TX
  routing but can remain stale when only S3 resets.

`DEC-0054` accepts ES8311, `TLV9061IDBVR` active high-Z capture,
`TMUX1136DGSR` speaker selection, `TS5A63157DCKR` TX selection and
`SN74LVC2G08DCUR` gating of both P11/P12 requests by direct pulled-low GPIO6
`AUDIO_ARM`. Arm-low forces both selectors to analog defaults independently of
stale expander state and leaves GPIO43 free. Passive capture stays a same-PCB
DNP/cost-down experiment; TAC5111IRGER stays a more expensive new-driver
reference.

Normative firmware sequencing is disarm-first:

1. On boot/reset, never drive GPIO6 high; the external pull-down establishes
   speaker-bypass/electret defaults before firmware runs.
2. Keep `AUDIO_ARM=0` while powering and reading ES8311, starting/verifying
   I2S clocks, and writing/verifying P11/P12 requests.
3. Assert `AUDIO_ARM=1` last, only when the requested codec path is valid.
4. Before changing either request, codec power or clock state, clear
   `AUDIO_ARM`, verify analog defaults, update the request, then re-arm only if
   the complete path is healthy.
5. On any readback, DMA, I2C, watchdog, brownout or shutdown fault, clear arm
   first; stop/mute/power-down follow. No audio selection may assert PTT.

Firmware may now freeze these control states and ordering, but must not freeze
unmeasured gain/mute delays, codec register values or claim lossless TX/speaker
routing before electrical/HIL closure.

## Explicitly open

Hardware `FND-0060/0066/0067` list the remaining electrical/HIL endpoints:
display connector/backlight/protection/sourcing, exact codec power and passive
analog networks, IR
frontends/driver/evidence, hard STOP latch, power/current/thermal supervision,
load switching/isolation, audio HIL, Unit protection and service-
connector mechanics. Firmware must not infer drivers, levels or safe states
for those boundaries before they close.

Hardware `DEC-0052/REV-0004X` close `FND-0061`: direct S3 QSPI GPIO41/42 and
the time-based arbitration contract are now runtime inputs. Hardware
`DEC-0053/REV-0004Z` additionally accept a 3.5-inch portrait `320×480` IPS
QSPI+touch class, with `ST77922` primary HIL and `AXS15231B` secondary HIL.
Hardware `FND-0063/DSP-0005/REV-0005A` additionally instantiate exact current
assembly candidate `HMX035CTFT-001`: S3 GPIO39 is touch IRQ, GPIO41/42 are
QSPI D2/D3, slow P06/P07 are display/touch reset and GPIO43 remains free after
GPIO6 is assigned to `AUDIO_ARM`.
Firmware may implement reusable scheduler and distinct prototype driver
profiles, but cannot freeze a production-qualified assembly, touch protocol or
vendor init table before the sourcing and specimen proof gates.

Independent digital buses do not prove RF coexistence. `SG-N24` nevertheless
requires real concurrent roles with no hidden time-sharing. What remains open
is the measured channel/power/rate/antenna/wanted-level envelope: same/adjacent
local TX can desensitize a weak peer RX, and same-channel packets also collide.
Firmware must publish the exact qualified profile selected by `DEC-0047` and
measured through `N24H-0001`;
it must neither claim isolated sensitivity nor synthesize RX continuity by
silently pausing peers. C5 protocols still share one native RF resource and use
visible vendor coexistence inside their own group.
