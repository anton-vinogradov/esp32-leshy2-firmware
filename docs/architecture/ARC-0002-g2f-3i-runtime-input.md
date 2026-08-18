# ARC-0002 — G2F-3I runtime input

- Status: **reviewed paper-layout input; target firmware architecture remains blocked**
- Date: 2026-08-18
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
- hard STOP and actual-TX evidence: [`DEC-0061`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0061-aon-stop-and-per-path-tx-evidence.md), [`SAFE-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/SAFE-0002-accepted-aon-stop-and-evidence-circuit.md), [`REV-0005O`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005O-i2-safety-decision-propagation.md)
- replaceable-cell boundary: [`DEC-0062`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0062-individually-replaceable-2s-cells.md), [`REV-0005Q`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005Q-battery-format-decision-propagation.md)
- exact holder and thermal coupling: [`DEC-0077`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0077-keystone-1048p-qualified-cell-profile.md), [`PWR-0016`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0016-keystone-1048p-holder-and-ntc-coupling.md), [`REV-0005AH`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AH-battery-holder-and-ntc-coupling.md)
- exact first cell target: [`DEC-0079`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0079-xtar-18650-4000mah-qualification-target.md), [`PWR-0018`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0018-xtar-18650-4000mah-cell-profile.md), [`REV-0005AJ`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AJ-exact-cell-propagation.md)
- diagnostic hardware lockout: [`DEC-0078`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0078-hardware-diagnostic-refractory-lockout.md), [`PWR-0017`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0017-hardware-diagnostic-refractory-lockout.md), [`REV-0005AI`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AI-diagnostic-lockout-propagation.md)
- accepted supervised 2S topology: [`DEC-0065`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0065-supervised-2s-battery-topology.md), [`PWR-0006`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0006-one-or-two-cell-topology-comparison.md), [`REV-0005T`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005T-supervised-2s-topology-decision-propagation.md)
- accepted 2S manager: [`DEC-0066`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0066-max17320-mspm0-fail-closed-manager.md), [`PWR-0005`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0005-replaceable-2s-manager-options.md), [`REV-0005V`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005V-2s-manager-decision-propagation.md)
- accepted deep-cell/circuit boundary: [`DEC-0067`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0067-no-in-device-deep-cell-recovery.md), [`PWR-0007`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0007-max17320-2s-surrounding-circuit.md), [`REV-0005X`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005X-deep-cell-policy-propagation.md)
- sink-only USB-PD frontend: [`DEC-0063`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0063-sink-only-30w-usb-pd-power-path.md), [`PWR-0004`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0004-accepted-usb-pd-front-end.md), [`REV-0005R`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005R-usb-pd-decision-propagation.md)
- fixed downstream rail tree: [`DEC-0068`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0068-separate-fixed-downstream-rails.md), [`PWR-0008`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0008-exact-downstream-rail-tree.md), [`REV-0005Y`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005Y-downstream-rail-tree-propagation.md)
- latch-off external eFuse: [`DEC-0069`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0069-latch-off-external-efuse.md), [`REV-0005Z`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005Z-latch-off-efuse-propagation.md)
- enable-qualified switched-rail PG: [`DEC-0070`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0070-enable-qualified-switched-rail-pg.md), [`PWR-0009`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0009-enable-qualified-switched-rail-pg.md), [`REV-0005AA`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AA-switched-rail-pg-qualification.md)
- external-eFuse passive/startup profile: [`DEC-0071`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0071-post-start-accessory-transient-profile.md), [`PWR-0010`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0010-external-efuse-passive-profile.md), [`REV-0005AB`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AB-external-efuse-passive-profile.md)
- exact converter passive profile: [`DEC-0072`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0072-exact-converter-energy-feedback-passives.md), [`PWR-0011`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0011-application-converter-passive-profile.md), [`REV-0005AC`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AC-application-converter-passive-profile.md)
- exact converter control-passive profile: [`DEC-0073`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0073-exact-converter-control-passives.md), [`PWR-0012`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0012-exact-converter-control-passives.md), [`REV-0005AD`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AD-converter-control-passive-profile.md)
- exact source/AON/POR/main sequence: [`DEC-0080`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0080-exact-aon-pg-por-main-sequence.md), [`PWR-0019`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0019-exact-source-sequence-and-power-reserve.md), [`FND-0084`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0084-abstract-main-source-sequencer.md), [`REV-0005AK`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AK-source-sequence-propagation.md)
- independent internal-rail containment: [`DEC-0081`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0081-independent-internal-rail-containment.md), [`PWR-0020`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0020-independent-post-buck-containment.md), [`FND-0085`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0085-uncontained-internal-buck-high-side-short.md), [`REV-0005AL`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AL-internal-rail-containment-propagation.md)
- consolidated I3 paper closure: [`DEC-0082`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0082-i3-paper-closure.md), [`PWR-0021`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0021-i3-consolidated-paper-closure.md), [`FND-0086`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0086-i3-paper-and-hil-closure-were-conflated.md), [`REV-0005AM`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AM-i3-paper-closure-propagation.md)
- exact protected product USB port: [`DEC-0083`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0083-exact-protected-product-usb-port.md), [`USB-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/USB-0001-exact-product-usb-c-and-protection.md), [`FND-0087`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0087-product-usb-ended-on-abstract-port.md), [`REV-0005AN`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AN-product-usb-port-propagation.md)
- exact bounded pack diagnostic: [`DEC-0074`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0074-bounded-pack-diagnostic-pulse.md), [`PWR-0013`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0013-exact-pack-diagnostic-frontends.md), [`FND-0078`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0078-mspm0-pa24-forbids-injection-current.md), [`REV-0005AE`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AE-pack-diagnostic-profile.md)

## Boundary

This document records the firmware consequences of the leading reviewed
**paper** layout. It does not start a toolchain, freeze three production
images, select exact peripheral drivers or restore the superseded `ARC-0001`
as target. Physical RF, exact parts/power/mechanics and HIL can still remap the
architecture before the atomic decision.
Hardware `DEC-0051` makes this reviewed projection visible as the current G3
working design. It does not convert the input into a frozen firmware HAL or G7
architecture.
Hardware `DEC-0082/PWR-0021` now mark the I3 paper electrical subset reviewed
and activate dependent I4 paper work. That maturity only makes the exact
source/rail/fault contracts consumable here: procurement and prototype HIL
remain open, measured thresholds do not appear from calculations, and any
functional or derating conflict reopens I3 before it changes this input.
Hardware `DEC-0083/USB-0001` now close the first I4 paper endpoint. Firmware
may consume a protected native S3 USB2 path, sink-only CC path, automatic
port disconnect and the absence of Alt Mode. It may not promote unmeasured
USB Full-Speed RC/SI, ESD/short-to-VBUS behavior or the fixture-only protector
`FLT` signal into a production runtime claim.

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
  a safety-deadline line and does not assert PTT. TPS25751D is another bounded
  target on this bus. Its active-low IRQ shares GPIO37 with TCA6424 `INT`;
  every wake reads both status blocks and no driver assumes a unique source.
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

## Replaceable-cell admission input

- The battery has two individually replaceable exact
  `XTAR 18650 4000mAh` protected button-top cells in a supervised 2S
  arrangement. The pair is `28.8 Wh` nominal; each cell is `4000 mAh` typical /
  `3800 mAh` minimum, `10 A` maximum continuous discharge, `2 A` standard
  charge and `<=40 mOhm` initial-resistance class. Individual replacement does
  not imply that an arbitrary cell or combination is valid. Both admitted
  cells are required for battery operation.
- The exact reference holder is polarized `Keystone 1048P`; the selected cell
  maximum envelope is `18.7 × 69.7 mm`. Raw flat-top, XTAR USB-equipped and
  third-party protected variants are unsupported even when they share a core.
  Mechanical polarity remains below firmware, while exact-cell identity is a
  declared qualified profile: neither S3 nor the admission MCU can authenticate
  an arbitrary two-terminal cell by measurement alone.
- The qualified profile carries exact model, approved source, assembly
  certification/test-summary identity, lot, nominal capacity, expected
  resistance/droop distributions and temperature policy. Missing or stale
  certification/lot evidence blocks a production kit; firmware does not
  manufacture identity from voltage, capacity or a packaging security code.
- `PWR-0005/FND-0075` separate gauging from pre-closure admission, while
  `PWR-0006/FND-0076` retain the controlled-1S cross-charge, common-current and
  SOC consequences as future-variant evidence. `DEC-0066` freezes the hardware
  identities and roles: `MAX17320G20+T` is the local gauge/protector and
  `MSPM0C1104SDGS20R` is the admission owner. Register policy and image format
  remain implementation outputs, not permission to change those roles.
- Hardware owns reverse-insertion prevention, observation before admission and
  the charge/discharge FET boundary. Firmware may request admission but cannot
  force a refused pair on or use balancing to mask an unsafe mismatch.
- `DEC-0067` forbids in-device deep-cell recovery. A cell below the qualified
  admission floor is refused; `3.0 V` relaxed/no-load per cell is a paper
  starting point, not yet a firmware constant. The protected MAX17320 image
  keeps zero-volt charge and linear prequalification disabled, and firmware
  must verify that state before requesting release. There is no S3, admission-
  MCU or product-menu command that can enable either path.
- Normal charge is capped at `2 A`, the exact cell's standard value, and is
  blocked outside `0…45 °C` until an assembly-specific qualification narrows
  or explicitly extends that range. The 4-A manufacturer maximum is not a
  runtime option. Source current, system load, any invalid NTC or HIL policy
  may only reduce the 2-A ceiling.
- The physical `ZVC` contact is unused by hardware. Firmware must not describe
  a register write as an alternative recovery path. Any characterization or
  attempted recovery uses a separately powered isolated Controlled-Zone
  fixture and is outside the handheld runtime protocol.
- Firmware retains distinct `cell_0`, `cell_1`, set/bus, temperature, contact and
  admission states. Missing/inconsistent evidence is `unknown` and blocks
  charge, high-load operation and TX leases rather than inheriting the prior
  battery state.
- `PACK_NTC0` and `PACK_NTC1` are direct mid-can channels for their own cells.
  The BQ25798 TS input is a third physically independent sensor populated at
  the HIL-qualified thermally worst slot. Open, short, lifted, implausibly
  static or mutually inconsistent temperature evidence blocks admission or
  charge; firmware cannot substitute a model or the neighboring sensor. If no
  single charger-TS site bounds both slots, hardware must reopen the topology.
- Single-cell removal, contact bounce, a single-cell replacement and reset are
  fresh admission events. No previous state-of-charge, health or approved-pair
  identity is restored until both cells pass the hardware/firmware contract.
  The base product exposes no one-cell battery-operation mode.
- The admission MCU owns local gauge polling, protected-NVM verification,
  midpoint/full-stack ADC evidence on PA25/A2 and PA26/A1, diagnostic-load sequencing
  and the release decision. S3 consumes a
  read-only state/fault window and may request evaluation but cannot access the
  local gauge bus directly or override a refusal. The admission MCU is a
  fourth independently recoverable firmware image and service domain, not an
  application task silently hosted on S3.
- The admission image runs a bounded low-clock/duty state machine from AOLDO.
  Flash programming/recovery uses isolated fixture or admitted system power;
  firmware must not assume AOLDO can supply erase/program current.
- `PA24/A3` is not an ADC fallback: the exact MSPM0C1104 datasheet permits no
  injection current there, while the battery dividers can remain live during
  admission-supply loss. The corrected PA25/PA26 allocation preserves the
  `12 used / 3 service-reserved / 3 free` budget.
- The accepted diagnostic command is edge-only. Firmware waits at least 1 ms
  after stable admission VDD, holds `PA22/A4` low, writes one rising edge and
  returns it low; it never drives the load MOSFET directly and never treats
  GPIO-high time as the pulse duration. `TPUL2G223BQBR` channel 1 is
  non-retriggerable and produces approximately 34.4 ms typical with a
  conservative 28.7-40.7-ms paper window. Production accepts only a measured
  25-50-ms pulse. The falling channel-1 Q edge then starts channel 2, whose
  complementary output asynchronously clears channel 1 for a production-
  measured 350-860 ms. Repeated writes or a stuck-high GPIO therefore cannot
  extend one pulse or bypass the independent refractory interval.
- The admission ADC uses the internal 1.4-V reference. Before baseline it
  waits at least 10 ms after the last relevant source/contact edge. After the
  diagnostic trigger it waits at least 10 ms for the 10-nF divider filters,
  then captures midpoint and stack inside the remaining hardware pulse. The
  measured 25-ms production floor, rather than an X7R assumption, guarantees
  that window. A
  missing/invalid loaded sample, unexpected post-pulse droop or inconsistent
  gauge evidence blocks admission.
- The exact 10-Ohm load is two parallel 20-Ohm/2-W branches. Firmware neither
  detects nor compensates a missing branch: production continuity/calibration
  rejects the assembly, while any runtime loaded sample outside the signed
  exact-profile envelope fails closed.
- Production droop/contact thresholds and ADC acquisition/calibration come
  only from the exact approved-cell/contact/timer HIL profile. Every normal
  retry waits at least 10 seconds; an exact-cell profile may lengthen but never
  shorten that floor. The hardware 350-ms minimum is a separate fault bound,
  not a normal scheduling interval, and the short 0.57-0.88-A screen is never
  reported as proof of the 2.78-A product-load transient.
- Runtime diagnostics name the exact protected path without controlling it:
  `CSD87313DMST` CHG/DIS state, two slot-fuse/NTC channels, the 5-mOhm shunt,
  reset-default ALRT hold and admission-supply source. Unknown or inconsistent
  evidence keeps the path open; it never falls back to a software estimate.

## Sink-only USB-PD and charge input

- `TPS25751DREFR` autonomously loads its policy from dedicated
  `CAT24C512WI-GT3`; `BQ25798RQMR` is on the TPS-local I2C controller bus.
  S3 is a host/observer through TPS I2Ct, not the component required to make
  an ordinary dead-battery attachment negotiate safely.
- Raw connector power reaches both TPS `VBUS` and `VBUS_IN`. Hardware straps
  `ADCIN1=7`, `ADCIN2=0` select SafeMode and target address `0x20`: before an
  application rail exists, the VBUS LDO powers attach detection and the
  address-`0x50` EEPROM while PPHV, PD and charging remain disabled. The
  startup sequence is therefore raw attach → SafeMode → EEPROM load → accepted
  contract → PPHV/BQ SYS → `AON_SAFE_3V3` → TPS `VIN_3V3` and application
  rails. `VIN_3V3` presence is never itself permission to enable PPHV or CE.
- The TPS validates the programmed configuration format needed to load it; it
  does not independently establish owner-signature authenticity at every
  raw-VBUS boot. Authenticity is established by factory provisioning or the
  signed S3 update transaction before a region becomes active. Firmware must
  not describe a TPS format/CRC success as a fresh signature verification.
- The only accepted contracts are 5-V fallback, 9 V/3 A and 15 V/2 A. Firmware
  never requests or exposes 20 V, PPS, source/power-bank or BQ OTG. Any
  unexpected role/PDO is a latched power-policy fault and charge is disabled.
- Runtime state is explicit: negotiated voltage/current/power, cable/source
  class, input/charge limits, charger mode/faults, both cell states, EEPROM
  image version/hash/active region and whether recovery is required. Unknown
  is never converted into 30-W availability.
- The first charge-current ceiling is 2 A and is further reduced or paused by
  system load, connector/charger/cell temperature, weak-source behavior and
  cell-manager decisions. The 5-A IC capability is not a runtime default.
- The initial paper admission rule treats only `0.85 × negotiated input power`
  as usable. It first reserves `max(declared scenario load, measured SYS load
  + measurement margin)` and derives charge current from the non-negative
  remainder divided by pack voltage, still capped at 2 A. Missing measurements,
  DPM/current limiting, thermal derating or any power fault makes the requested
  charge current zero. This conservative rule is an admission floor pending
  measured efficiency maps, not a claim that conversion efficiency is 85%.
- Hardware fixes BQ25798 to 2S/750 kHz with an exact 2.2-uH/7-A inductor.
  POR or charger-watchdog reset restores 1-A charge, 7.0-V VSYSMIN and 8.4-V
  VREG; firmware has no frequency/cell-count profile selector.
- Before TPS GPIO1 may sink the reset-high CE line, the controller must
  validate the source contract, write and read back IINDPM at or below the
  advertised current and the 2.71-3.29-A physical ILIM envelope, confirm both
  cells and direct BQ TS are valid, then calculate a load-aware charge current
  no greater than 2 A. Unknown power or temperature releases CE.
- BQ TS uses a third electrically independent B57332V5103F360 and remains
  enabled. Firmware may narrow the qualified charge window, but must never set
  `TS_IGNORE`; the two MAX17320 cell sensors remain separate evidence.
- Product USB2 remains native on S3 GPIO19/20 through the automatic four-line
  port protector and exact initial 22-Ohm series resistors; its exact PHY limit
  is Full-Speed 12 Mbit/s. Two hardware shunt-capacitor positions remain DNP
  pending measured tuning. There is no firmware profile that enables TPS
  BC1.2/liquid pins, BQ DPDM or physical Type-C SBU/Alt Mode on the data pair.
- Connector overvoltage opens affected CC/data paths in hardware. Runtime
  treats detach, PD fault or failed USB re-enumeration as a closed USB session,
  clears any USB-derived Controlled-Zone authorization and reports the fault;
  it does not bypass protection or enter a tight reset/re-enumeration loop.
- Direct protector `FLT` is intentionally fixture-only because the paper map
  preserves GPIO47. Production runtime therefore uses TPS status, native USB
  link state and re-enumeration outcome; it never fabricates the missing direct
  FLT observation. Full-Speed RC/signal-integrity and enumeration remain HIL;
  a failed gate reopens hardware values, placement or protection rather than
  changing the advertised PHY class or removing protection.
- A PD image update is permitted only while TX is disarmed, input and cells are
  stable, the signed manifest targets the exact board/controller/tool version,
  and the inactive EEPROM region is writable. Readback/hash/boot validation
  occurs before retiring the previous region; interruption preserves rollback.
- EEPROM WP is reset-high through an exact pull-up. TPS GPIO0 is an open-drain
  sink only: firmware/configuration may release it or pull it low inside the
  authorized signed-write window, never drive it high or leave WP writable
  across reset/fault. TPS GPIO1 remains the separate open-drain CE sink.
- The autonomous local SCL/SDA pair has exact 2.2-kOhm LDO_3V3 pull-ups; the
  S3 host SCL/SDA pair has exact 2.2-kOhm 3V3_MAIN pull-ups and SYS_INT_N has
  one 10-kOhm pull-up. Bus speed remains bounded by measured aggregate
  capacitance/rise time; firmware may not infer 1 MHz solely from the EEPROM
  rating or start host transactions before 3V3_MAIN is valid.
- Factory/recovery pads remain the authority for a blank or corrupt EEPROM.
  The ordinary FLxx region-update flow assumes an initialized image and cannot
  be presented as blank-device provisioning. First image is programmed before
  placement or by a current-limited raw-VBUS fixture that observes
  `ReadyForPatch`, verifies I2Cc high-Z, then uses direct SDA/SCL/WP pads. It
  never injects 3.3 V into the TPS LDO output. Firmware presents those recovery
  instructions but cannot claim that an application-only update path is
  independent recovery.
- HIL covers every supported/fallback cable and source, blank/corrupt image,
  interrupted update, shared-IRQ concurrency, no-battery/deep-cell refusal,
  supplement/removal/bounce, thermal derating and proof that 20 V/source/OTG
  never reaches the connector.

## Fixed downstream rail runtime input

- `BQ25798RQMR.SYS` feeds four electrically independent, hardware-fixed
  converters. `TPS629203DRLR` creates `AON_RAW_3V3`, and separate
  `TPS564252DRLR` devices create `MAIN_RAW_3V3`, `VVOICE_RAW_4V` and the
  pre-protection 5-V accessory rail. An exact independent cutoff admits each
  internal raw rail to `AON_SAFE_3V3`, `3V3_MAIN` or protected `VVOICE_4V`.
  Firmware has no voltage selector, feedback-network mode or command that can
  bridge a cutoff or turn the 4-V voice output into 5 V.
- The fixed hardware profile is exact rather than runtime-configurable:
  TPS629203 selects 3.3 V with open `FB/VSET` and a 42.2-kOhm MODE/S-CONF
  strap; the three TPS564252 dividers produce nominal 3.318/4.000/5.000 V.
  Their paper limits are acceptance inputs, not ADC calibration values or
  software-adjustable set points. Firmware exposes the rail identity and
  measured qualification result, never a voltage-setting API.
- AON power is autonomous. `TPS629203.EN` is strapped directly to admitted
  `SYS`; `TPS25961DRVR` independently admits the resulting raw rail. The
  converter PG pull-up and `TPS3808G33` SENSE/POR supply exist only on
  protected `AON_SAFE_3V3`. PG drives `MR_N`; only valid raw-converter PG plus
  protected SENSE above 3.07 V for the exact CT delay releases
  open-drain `POR_N`, whose 10-kOhm pull-up and 100-kOhm main-EN fail-low pull
  produce about 3.0 V and enable the main converter. There is no programmable
  source sequencer. Application firmware observes the result but cannot start
  AON, bypass its eFuse/POR or keep the main rail alive after protected AON
  PG/SENSE loss.
- The amended converter-control profile has ten physical resistor positions:
  the AON PG pull-up, POR pull-up, three application EN fail-low pulls, both
  optional PG pulls, both qualifier-base resistors and the common fault pull.
  Their values do not create a firmware setting, timing constant or retry
  path: runtime consumes the safe defaults and `EN AND NOT(PG)` truth table,
  then uses measured HIL deadlines.
- Main and voice each cross a physically separate `TPS25974LRPWR` latch-off
  boundary with fixed OVLO, circuit-breaker, dVdt, ITIMER and PGTH parts.
  Firmware consumes only protected-side PG as operational load-good evidence.
  Raw main/voice converter PG is fixture-only and must never grant a rail,
  lease, signal group or retry.
- `3V3_MAIN` is admitted by hardware after a valid battery or USB source and
  supplies the three compute domains. Protected `MAIN_3V3_PG_N` loss joins
  `POWER_FAULT_N`; firmware immediately revokes every lease and returns the
  logical signal group to `NONE`, but protection and reset do not wait for
  that reaction.
- Five independent `TPS22919DCKR` branches gate the complete nRF group,
  CC1101, microSD, ES8311 and Si4732. Every ON input has an external reset-off
  default. QOD discharges the disabled output; firmware may call a branch
  quiet only after its controller and pins are parked, the rail has completed
  the measured discharge interval and back-power/current evidence passes.
- The nRF branch is deliberately common to all three radios. Entering
  `SG-N24` powers and settles all three, then enables their independent buses;
  it never cycles a peer rail to implement `3R`, `1T+2R`, `2T+1R` or `3T`.
  Leaving the group parks all three interfaces before the common branch opens.
- Voice sequencing asserts the STOP-dominant `VOICE_DOMAIN_EN_SAFE`, waits for
  qualified `POWER_FAULT_N` collector to release, keeps PTT forced RX and
  `AUDIO_ARM=0`, then qualifies the SA518/codec path before allowing
  selection. Hardware uses protected `VOICE_4V_PG_N` locally to hold the
  voice domain reset/PD. During the bounded start interval the qualified
  collector is expected low because `EN=1, PG=0`; it becomes a fault only if
  it does not release by the measured deadline. Disable occurs in the
  opposite order, and `EN=0` makes protected PG low a normal off state. A 4-V PG
  timeout or fault cannot fall back to the accessory rail.
- A main/voice protection trip is a latched hardware fault. Runtime first
  revokes every affected lease, forces the logical signal group to `NONE`,
  records protected PG/fault evidence and parks signal pins. Voice recovery is
  a new validated power session through its existing STOP-dominant enable; a
  latched main trip requires complete source removal and fresh hardware
  admission. AON overcurrent/thermal recovery attempts are owned and bounded
  by TPS25961 hardware; firmware cannot accelerate them, and main remains off
  until protected PG/SENSE/CT are continuously valid. Firmware has no direct
  eFuse reset/bypass API and never loops rail power against a persistent fault.
- Accessory sequencing asserts the shared STOP-dominant enable of both the
  5-V converter and `TPS259470LRPWR`, waits for the enable-qualified converter
  PG collector to release and the eFuse output to complete its qualified
  controlled ramp, and only then identifies/enables U214 signal paths.
  `EN=1, PG=0` is a bounded pending state; failure to release is latched, while
  `EN=0, PG=0` is normal quiet state and must not create a fault. The nominal
  1.509-A eFuse limit is active immediately during startup: runtime must never
  claim that `ITIMER` defers it. The 4.7-nF `dVdt` profile admits at most 1 mF
  effective accessory input capacitance pending HIL. The port is 1.25 A
  continuous; 2.0 A is one bounded post-start excursion, approximately
  86.6…404 ms on the paper limits, not a startup or continuous budget. The
  eFuse always blocks reverse current. Its active-low `FLT` also joins
  `POWER_FAULT_N`; `ILM` is a protected factory/HIL test point, not an
  invented runtime ADC channel.
- OVLO recovery on the selected eFuse bypasses the normal `dVdt` ramp and
  restarts current-limited. Runtime treats that event as a new accessory
  admission: signal paths remain isolated until rail/evidence qualification
  completes, even if the request and enable never changed.
- On disable or fault, accessory signals isolate first, converter/eFuse enable
  clears, and the connector is allowed to reach its measured passive-discharge
  threshold before the UI reports it safe to remove. External 5-V injection,
  qualified-PG/FLT disagreement, expired post-start transient, timeout or
  unknown evidence remains a latched accessory fault and cannot be cleared by
  re-enabling in a loop. The exact `L` suffix
  also latches thermal/latched faults in hardware until EN is explicitly taken
  below shutdown or input power is cycled; the former 110-ms auto-retry suffix
  is not a target behavior.
- microSD is unmounted/flushed and SPI pins are parked before `SD_PWR_EN`
  clears. ES8311 follows the stricter audio-arm sequence below. Si4732 and
  CC1101 similarly park reset/bus pins before their independent branches open.
  A failed settle, readback or discharge gate leaves the whole requested group
  unavailable rather than silently weakening the quiet-state contract.

## Hard STOP and actual-TX input

- The AON hardware latch, not firmware, owns the dominant stop path. STOP or an
  open normally-closed loop asynchronously blocks every reviewed TX/rail
  request and holds `S3.EN`, `C5.EN` and `RP.RUN` low. Firmware therefore cannot
  observe a live STOP session from those targets; it reconstructs the cause
  best-effort after a new physical RE-ARM and fresh TX-off boot.
- Releasing STOP does nothing. Only a new edge from the normally-open RE-ARM
  control permits the three processors to boot, and no target/profile/power/
  payload/lease state is restored.
- RP GPIO22 is direct active-low `RP_ANY_TX_N`. It is independent of software,
  I2C and the source-mask expander. Low means at least one qualified evidence
  channel asserts; high alone does not convert missing or faulty evidence into
  proof of no transmission.
- RP local I2C0 also reads TCA9534A address `0x20`: P0..P7 map exactly to
  `S3_RF`, `C5_RF`, `NRF0_RF`, `NRF1_RF`, `NRF2_RF`, `CC_RF`, `VOICE_RF` and
  `IR_OPTICAL`. Its interrupt is a test point, not a new RP GPIO dependency.
- Firmware reports `commanded`, `device-reported`, `actual` and
  `unknown/unavailable` independently. All eight evidence lines low are
  sufficient positive observations; an impossible aggregate/mask combination,
  I2C failure or an unqualified accessory is a fault/unknown state and expires
  any proof-dependent lease.

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

Hardware `FND-0060/0066/0067/0079/0080/0081/0082/0083/0085/0086` list remaining electrical/HIL endpoints:
display connector/backlight/protection/sourcing, passive codec/analog networks,
IR frontend/driver, TPS25751 raw-VBUS/SafeMode/CC-capacitance and bus-rise-time
HIL, exact-cell diagnostic thresholds and timer/load hot HIL,
source-transition, brownout, thermal/source-handover/fault HIL, Unit
protection and service-connector
mechanics. The active downstream converters, their 24 energy/configuration/
feedback parts, ten control resistors, direct AON EN strap, exact AON-PG/POR/main sequence, switches and
independent AON/main/voice post-buck cutoffs with protected PG, plus
external eFuse plus its eight profile passives, and the corrected dual-channel
pack diagnostic timer/load/divider/filter instances, plus the exact BQ25798 inductor, 19
capacitor instances, ten resistors and third NTC, plus the 17 exact TPS/EEPROM
support components and hardware SafeMode straps, plus exact polarized 1048P
holder contacts, two exact XTAR cell instances and the three-NTC physical roles,
are now reviewed paper inputs under `DEC-0082/PWR-0021`,
but firmware must not infer unmeasured delays, thresholds or safe states for
their still-open HIL boundaries.

The hard STOP latch, reset fanout, gate topology and digital evidence delivery
are paper-reviewed inputs from `DEC-0061`; exact RF/optical detector taps,
matching, thresholds and fault-injection HIL remain open under hardware `I6`.

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
