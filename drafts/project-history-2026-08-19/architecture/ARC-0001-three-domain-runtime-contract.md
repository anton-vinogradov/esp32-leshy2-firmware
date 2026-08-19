# ARC-0001 — former three-domain runtime candidate

- Status: **Superseded as the target architecture; retained as a candidate/reference**
- Date: 2026-08-16
- Superseding process decision: [`DEC-0032`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0032-reopen-product-design-before-cad.md)
- Hardware decision: [`DEC-0028`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0028-accept-zero-based-syn-3a.md)
- Component revision decision: [`DEC-0029`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0029-c5-v1.2-production-floor.md)
- Development-access decision: [`DEC-0031`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0031-permanent-three-domain-development-access.md)
- Normative hardware package: [`PKG-0001/SYN-3A`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PKG-0001-zero-based-target-architecture-proposal.md)
- Exact pin/controller map: [`PIN-0002/SYN-3A`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PIN-0002-zero-based-exact-pin-maps.md)

> The entire model below records the former `SYN-3A` candidate. It is not a
> normative target, does not select S3/C5/RP or any exact interconnect, and must
> not be used as a prerequisite for implementation. Target firmware ownership
> and failure boundaries will be selected only after product design,
> whole-device comparison and conceptual hardware/software co-design.
>
> Its `10 full-frame-equivalents/s`/`≥4.5 MB/s` display row is additionally
> superseded by hardware `DEC-0043`. The active software contract uses
> dirty/tiled preemptible updates, `≤100 ms` critical/menu first feedback and
> explicit waterfall coalescing/drop evidence.

This document remains useful as a reviewed source of candidate requirements,
risks and measurements. It does not claim that the current source tree
implements them.

## Runtime domains

| Target | Owned services | Must remain local |
|---|---|---|
| S3 N16R2 | product state/UI, touch and slow controls, display, files/microSD, USB/web, ES8311/Si4732 audio, native 2.4 GHz Wi-Fi/BLE, U214/GNSS/U216 profiles, orchestration | UI state, filesystem ownership, audio buffers, accessory policy, global session view |
| C5 N8R8 production rev ≥v1.2 | 2.4/5 GHz Wi-Fi, IEEE 802.15.4, two-path IR RX and IR TX, SDIO slave, native-radio lease enforcement | radio/IR timing, country/profile checks available to the target, local queues, lease expiry and safe-off |
| `SC1512-A4` (`RP2354B0A4`) | 3×nRF24, CC1101, analog-voice UART/control/PTT, direct physical PTT, local dead-man, packet timestamps/FIFOs, direct STOP observation, SPI slave | CE/CSN/IRQ/GDO/PTT timing, radio identity, queue admission, lease expiry and safe-off |

S3 is the product orchestrator, not the sole safety authority. C5 and RP reject unsafe or stale commands independently and never require S3 to meet their peripheral deadlines.

## Inter-domain links

| Link | Physical transport | Roles | Qualified floor |
|---|---|---|---|
| S3↔C5 | S3 SDMMC host, C5 1-bit SDIO slave | S3 policy/orchestration; C5 native-radio/IR service | ≥1.5 MB/s framed payload, ≤70% admitted occupancy, control RTT ≤2 ms |
| S3↔RP | S3 GP-SPI3 master, RP SPI1 slave, initial 20 MHz, dedicated `RP_ALERT_N` | S3 policy/orchestration; RP packet/voice service | ≥1.5 MB/s framed payload with measured latency/liveness |

Both links expose the same semantic channel classes:

| Channel | Purpose | Backpressure/failure rule |
|---|---|---|
| `CH-CTL` | bounded commands, configuration and acknowledgements | never dropped silently; timeout fails closed |
| `CH-EVT` | state transitions, actual-TX, faults and completion | priority bounded queue; overflow is a persistent fault |
| `CH-BULK` | captures, packet batches and update blocks | credit based; may pause or produce explicit gaps |
| `CH-LIVE` | heartbeat, compatibility, lease renewal and time calibration | loss expires local leases |
| `CH-REC` | signed update/recovery transfer and result | globally TX-off; resumable only at verified block boundaries |

Every frame carries protocol version, source domain, channel, sequence, payload length and integrity check. Events and records additionally carry source-local monotonic time, S3-time mapping uncertainty, loss/gap counters and the exact physical source. Wall-clock or GNSS corrections never reorder safety evidence.

IPC is never remote raw GPIO. A command expresses intent and bounded parameters; the owner performs hardware sequencing and reports actual result.

## Boot and compatibility state machine

1. `AON_SAFE` holds all TX gates inactive before any programmable target runs.
2. S3, C5 and RP boot independently into signed candidate or last-known-good images; no restored UI/session state arms TX.
3. Each target reports silicon/board identity, firmware version, protocol range, manifest hash, reset cause, self-test and recovery capability.
   Production firmware additionally requires C5 revision ≥v1.2. A v1.0 board is admitted only by an explicit engineering manifest, remains TX-off by default, disables HUK/Key Manager, PSRAM encryption and peripheral-domain power-down, and cannot emit production qualification evidence (`DEC-0029`).
4. S3 admits a peer only when the compatibility manifest intersects. Unknown or mismatched peers remain visible and TX-disabled.
5. C5 and RP keep local gates inactive until STOP is released, required self-tests pass and a fresh bounded lease is accepted.
6. Physical RE-ARM after STOP release only permits a new TX-off session; it never restores target/channel/power or a previous lease.

For the current G2F working input, hardware `DEC-0061` supersedes the former
steps 5–6 implementation detail: STOP resets all three compute domains through
the AON circuit, release alone does not boot them, and a fresh physical RE-ARM
starts a new TX-off boot. Firmware cannot be part of the dominant stop path.

Missing C5 permits S3-only non-dependent receive/UI/storage functions. Missing RP disables nRF/CC/voice functions. Missing or unhealthy S3 leaves C5/RP TX-off and recoverable through their physical service paths.

## Safety lease contract

Every TX-capable action uses one per-owner lease containing at least:

- capability/action and exact physical source;
- functional level and fresh Controlled-Zone entry generation where required;
- authorized target and/or contained-environment evidence class;
- region/profile, frequency/channel, power and duration/duty bounds;
- monotonic issue/expiry times and unique nonce;
- STOP generation, accessory identity and required rail/profile state.

The owner validates the lease against local state before touching a TX gate. Renewal is bounded and explicit. STOP, reset, watchdog, brownout, peer/link loss, manifest change, accessory removal, profile violation, expiry or a safety-relevant queue fault invalidates the lease. A stale message cannot renew it.

Commanded TX, rail/current observation, device-reported TX and independent actual-TX evidence are distinct states. UI and logs must not collapse them into one boolean.

## Functional-level enforcement

- `Main`: ordinary owned-device, reception, navigation, files, maintenance and legal communication flows.
- `Laboratory`: passive/defensive analysis and bounded experiments after the installation non-aggression pledge.
- `Laboratory → Controlled Zone`: every entry shows a fresh non-suppressible banner and hold-to-confirm. Each action remains separately disarmed and validates exact authorization/containment requirements.

Leaving the level, device lock, session timeout, STOP, watchdog, reset, update or loss of a required peer/accessory invalidates every affected arm and lease.

## Data, memory and admission

| Contract | Accepted floor/ceiling |
|---|---|
| S3 PSRAM | ≥1792 KiB usable: 896 KiB resident +512 KiB worst overlay +384 KiB reserve |
| S3 internal DMA | ≥192 KiB available before foreground I/O; planned use ≤160 KiB |
| C5 PSRAM | ≥7168 KiB usable with ≥2048 KiB margin |
| RP SRAM | planned use ≤416 KiB; ≥104 KiB guard |
| three nRF PRX | 200 kB/s payload each, 600 kB/s aggregate admitted |
| mixed packet profile | nRF aggregate 450 kB/s + CC 60 kB/s |
| audio | 48 kHz mono 16-bit full duplex, 192 kB/s, no unexplained DMA loss |
| display | historical 480×320/10-full-frame candidate; superseded by hardware `DEC-0043` task contract |
| storage | ≤1.5 MB/s admitted records, ≥4 MB/s qualified SD, ≥512 KiB queue over 250 ms stall |

The theoretical 3×nRF+CC maximum is not a lossless product promise. Admission either rejects, schedules gaps or records overflow explicitly. Safety/control/event traffic preempts bulk traffic.

S3 is the sole normal filesystem writer. USB MSC uses exclusive ownership or a read-only snapshot; host and firmware never write the same filesystem simultaneously.

## Update and recovery

| Target | Normal owner-signed lifecycle | Independent physical recovery |
|---|---|---|
| S3 | streamed verification, A/B image, first-boot confirmation/rollback | dedicated USB-C + physical GPIO0/EN + UART0 on DBG10 |
| C5 | signed package over `CH-REC`, target-side verification, A/B rollback | dedicated USB-C GPIO13/14 + physical GPIO28/CHIP_PU + UART0 GPIO11/12 on DBG10; GPIO27 held high for USB/UART Joint Download Boot 0 |
| RP | signed package over `CH-REC`, first-stage verification, A/B rollback | dedicated USB-C + USB_BOOT/RUN + SWD on DBG10 |

Updates are sequential, power-qualified and globally TX-off. One target cannot bypass another target's verifier. Owner keys, reproducible/offline signing and intentional developer recovery remain available; irreversible eFuse/OTP lockdown is optional and outside the accepted baseline.

C5 physical recovery does not depend on GPIO26, S3 firmware or the C5
application image. The service fixture holds GPIO28 low, preserves GPIO27 high
and toggles CHIP_PU before using native USB or UART0. This exact strap contract
comes from hardware `FND-0037/REC-0001`; automated normal updates still use
`CH-REC` and never emulate the physical recovery control.

### Permanent development access

Each domain has a permanently fitted keyed 2×5 DBG10 header with common
semantics: pin 1 `VTREF_SENSE`, 2 GND, 3 active-low reset, 4 active-low boot,
5/6 target debug pair, 7 GND, 8 `ID0`, 9 GND and 10 `ID1`. The fixture first
reads passive `ID1:ID0` (`00=S3`, `01=C5`, `10=RP`, `11=invalid`) while reset,
boot and debug drivers remain high-impedance. It senses target voltage but
never powers the target through DBG10.

The target mappings are S3 `EN/GPIO0/UART0 TX GPIO43/RX GPIO44`, C5
`CHIP_PU/GPIO28/UART0 TX GPIO11/RX GPIO12`, and RP
`RUN/USB_BOOT/SWDIO/SWCLK`. GPIO11/12 are therefore service-reserved on C5,
leaving GPIO2/4/5/23/24 as the five generic C5 reserve pins (`FND-0038`). Each
domain also has parallel physical BOOT and RESET buttons. None depends on a
peer, expander, running image or firmware-controlled mux. C5/RP USB does pass
through one fixed-selected board-powered isolation switch, so USB data is
deliberately unavailable when the product is off while DBG10 remains passive.

S3 USB remains the product data/protected-power path. C5 and RP USB are
board-powered data-only service ports: their VBUS reaches only a 1-MOhm
bleeder and high-impedance test pad and cannot feed the board power tree;
power-off isolation also blocks D-line backfeed.
Connecting three hosts simultaneously must not cause backfeed, false attach,
reset storms or TX re-arm. Reset, BOOT and debug events expire affected TX
leases; service firmware remains subject to STOP and all RF authorization and
containment gates.

The complete runtime and fixture ordering, invalid-ID behavior and service
event schema are defined by [`SVC-0001`](SVC-0001-service-recovery-runtime-contract.md).

On C5, manual flash-encryption provisioning—if a later opt-in profile accepts it—runs at CPU ≤160 MHz because `FLASH-938` also affects v1.2. `ECC-833` remains a separate security constraint. Selecting v1.2 does not itself enable encryption, HUK or irreversible lockdown.

## Build and interface boundaries

The repository shall produce three explicit images and one compatibility manifest:

- `leshy2-s3`: product application and orchestration;
- `leshy2-c5`: native-radio/IR service;
- `leshy2-rp`: packet/voice deterministic service and first-stage recovery support;
- signed release manifest: compatible protocol ranges, hardware revisions, component/profile identifiers, hashes, rollback indices and required migrations.

The hardware component/profile identifiers for the three compute targets are
the exact C-001…003 identities from the repository-local CAD provenance
manifest accepted by hardware DEC-0030. Firmware must not infer a board profile
from a generic ESP32/RP family symbol, shared footprint geometry or legacy
tsCircuit part identifier.

Shared code may define message schemas, policy vocabulary, crypto/package format and test vectors. It must not erase target ownership or make a peer driver perform raw GPIO over IPC.

## Failure behavior

| Failure | Required visible result |
|---|---|
| IPC CRC/version/sequence error | reject frame, increment evidence counter; safety-relevant error expires lease |
| heartbeat timeout | local safe-off, peer degraded, no hidden automatic re-arm |
| bulk queue pressure | explicit pause/gap/drop counters; control/event channels preserved |
| storage stall/removal | RAM queue then explicit gap; recording failure cannot hold TX |
| STOP or brownout | asynchronous hardware safe state; best-effort post-boot reason reconstruction only |
| incompatible or rollback image | reject/rollback target, keep dependent capabilities disabled |
| unknown accessory/profile | power/isolation safe-off and visible unsupported state |

## Verification gates

Firmware release remains blocked until the hardware `KG-01…08` evidence exists. In particular:

- shared-bus three-nRF 600 kB/s timing and latency must pass on RP;
- both IPC links must pass payload, RTT, malformed-frame, stall and lease-expiry tests;
- all three memory/DMA floors and A/B recovery paths must pass;
- STOP, actual-TX evidence, rail faults and brownout must pass hardware-in-the-loop fault injection;
- unqualified RF/TX pairs remain disabled even when the user is authorized.

Failure reopens the complete affected architecture package; firmware must not silently switch to `SYN-2A`, reduce the radio count or weaken recovery/safety behavior.
