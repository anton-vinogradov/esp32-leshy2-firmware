# ARC-0002 — G2F-3I runtime input

- Status: **reviewed paper-layout input; target firmware architecture remains blocked**
- Date: 2026-08-17
- Canonical hardware decision: [`DEC-0044`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0044-delegated-noninterference-layout.md)
- Hardware artifact: [`NIF-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/NIF-0001-digital-noninterference-layout.md)
- Exact generated map: [`G2F-pin-ledger`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/generated/G2F-pin-ledger.md)
- Signal groups: [`DEC-0045`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0045-one-active-signal-group.md)
- Quiet states: [`DEC-0046`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0046-unused-interface-quiet-by-default.md), [`QST-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/QST-0001-unused-interface-quiet-states.md)
- Open nRF RF acceptance: [`IMP-0039`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/improvements/IMP-0039-three-nrf-full-mix-acceptance.md)

## Boundary

This document records the firmware consequences of the leading reviewed
**paper** layout. It does not start a toolchain, freeze three production
images, select exact peripheral drivers or restore the superseded `ARC-0001`
as target. Physical RF, exact parts/power/mechanics and HIL can still remap the
architecture before the atomic decision.

## Candidate runtime domains

| Domain | Candidate local ownership | Dedicated transports/resources | Local invariants |
|---|---|---|---|
| S3 | product policy/UI, display, audio, microSD, native BLE, Unit profile | SPI3 to RP, 4-bit SDMMC host to C5, SPI2 display+SD scheduler, I²S0, internal I²C0, separate Unit profile | UI feedback ≤100 ms; storage stalls never block radio leases/queues; native USB recovery |
| C5 | 2.4/5 GHz Wi-Fi, IEEE 802.15.4, dual-path IR RX and IR TX | exclusive 4-bit SDIO slave to S3; direct IR RMT/evidence | local RF/IR queues, lease expiry and safe-off; permanent UART0+EN/BOOT/strap recovery because runtime SDIO consumes USB pins |
| RP2354B | 3×full-function nRF24, CC1101, voice/PTT and U214 LoRa/GNSS | four independent PIO0 compatibility-radio buses, PIO1 U214 SPI, UART1 GNSS, isolated U214 I²C, hardware SPI1 to S3 | direct IRQ/GDO/BUSY/PTT; no peer-radio bus wait; USB+SWD+RUN+BOOTSEL recovery |

The exact RP map uses the real B-package PIO base rule: PIO0 and PIO1 select
the `GPIO16..GPIO47` window, and every PIO data pin is in `GPIO30..GPIO46`.
The hardware validator also locks the fixed mux sets for S3 USB, C5 4-bit
SDIO, and RP SPI1/UART0/UART1/I²C0; firmware must not remap these as generic
GPIO-matrix choices.

Persistent capacity is budgeted before runtime implementation: RP uses 5/12
PIO state machines and 13/16 DMA channels; S3 uses 3/5 GDMA TX and 3/5 GDMA RX
channels. The reserves are not permission for an unreviewed driver to claim a
permanent channel: any new fixed DMA consumer changes the upstream contract.
The quiet-state decision also consumes RP GPIO15/GPIO23 for common nRF and CC
power gates and C5 GPIO4 for the IR frontend gate. Direct free GPIO reserve is
therefore S3=4, C5=1 and RP=0; firmware cannot invent another direct RP control.

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
- C5↔S3 4-bit SDIO must qualify ≥1.5 MB/s framed payload and ≤2 ms control RTT;
  it exclusively owns the S3 SD/MMC host in this candidate.
- Display and microSD deliberately share SPI2. The scheduler uses separate CS
  and per-device clocks, display transactions ≤256 B, bounded SD commands/data
  chunks and critical-UI priority. The combined HIL must show first visible
  response ≤100 ms, storage ≥4.0 MB/s, 1.5 MB/s record and survival of a
  measured 250 ms card stall.
- Internal I²C contains only slow UI/audio/receiver/control endpoints. PTT,
  radio FIFO/IRQ/GDO/BUSY, hard STOP and timing evidence never wait for it.
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
3. C5 IPC control-priority/RTT, link-loss visibility and TX lease expiry under
   Wi-Fi/802.15.4/IR load;
4. display+SD scheduling, hot removal and injected 250 ms card stalls;
5. U214 I²C stuck-low/hot-plug fault injection and independent Unit/internal
   bus operation;
6. independent programming/recovery/diagnostics for all three domains;
7. PIO instruction placement, DMA arbitration and SRAM-bank contention under
   the same simultaneous event load; static channel counts alone are not the
   timing proof;
8. every non-member quiet-state transition, no-back-power/fault injection and
   active-receiver desense under maximum valid system-plane traffic.

## Explicitly open

Independent digital buses do not prove RF coexistence. `SG-N24` nevertheless
requires real concurrent roles with no hidden time-sharing. What remains open
is the measured channel/power/rate/antenna/wanted-level envelope: same/adjacent
local TX can desensitize a weak peer RX, and same-channel packets also collide.
Firmware must publish the exact qualified profile selected through `IMP-0039`;
it must neither claim isolated sensitivity nor synthesize RX continuity by
silently pausing peers. C5 protocols still share one native RF resource and use
visible vendor coexistence inside their own group.
