# ARC-0002 — G2F-3I runtime input

- Status: **reviewed paper-layout input; target firmware architecture remains blocked**
- Date: 2026-08-17
- Canonical hardware decision: [`DEC-0044`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0044-delegated-noninterference-layout.md)
- Hardware artifact: [`NIF-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/NIF-0001-digital-noninterference-layout.md)
- Exact generated map: [`G2F-pin-ledger`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/generated/G2F-pin-ledger.md)

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

## Mandatory scheduler/queue contract

- `nrf0`, `nrf1`, `nrf2`, `cc` and `u214` are separate event sources with
  independent IRQ timestamps, queues and overflow/drop counters. A shared
  worker may dispatch them, but no lock may serialize physical bus ownership.
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

## Firmware HIL that follows from this map

1. simultaneous three-nRF PRX plus CC/U214 events with per-source latency,
   overflow and unexplained-loss assertions;
2. RP IPC stress at accepted radio load while display, storage, audio and C5
   traffic run;
3. C5 IPC control-priority/RTT, link-loss visibility and TX lease expiry under
   Wi-Fi/802.15.4/IR load;
4. display+SD scheduling, hot removal and injected 250 ms card stalls;
5. U214 I²C stuck-low/hot-plug fault injection and independent Unit/internal
   bus operation;
6. independent programming/recovery/diagnostics for all three domains.
7. PIO instruction placement, DMA arbitration and SRAM-bank contention under
   the same simultaneous event load; static channel counts alone are not the
   timing proof.

## Explicitly open

Independent digital buses do not prove RF coexistence. Same/adjacent-band
transmitters can desensitize co-located receivers, and C5 protocols share
on-chip RF/coexistence resources. Firmware must not promise arbitrary
simultaneous RF operation until the hardware zoning/filter/antenna gate either
qualifies it or publishes an explicit, visible time-sharing contract.
