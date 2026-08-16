# Leshy2 Firmware — current engineering state

> Snapshot: 2026-08-16. This page describes what is proven now. The finished software target is in the [firmware product README](../../README.md), and the finished device target is in the [hardware product README](https://github.com/anton-vinogradov/esp32-leshy2).

- Canonical evidence: [hardware-owned review ledger](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review)
- Русская версия: [current-state.ru.md](current-state.ru.md)
- Legacy reference only: [`drafts/legacy-2026-08-15/`](../../drafts/legacy-2026-08-15/README.md)

## Review and implementation progress

| Layer | State |
|---|---|
| Cross-repository stages 0–1 | Reviewed |
| Stage 2: capabilities and exclusions | Reviewed (`REV-0002AD`) |
| Stage 3: architecture and ownership | Reviewed (`DEC-0028`, `REV-0003U`) |
| Stages 4–6: components through hardware validation | Stage 4 in progress; entry register reviewed |
| Stage 7: firmware design | Architecture contract accepted; detailed design not started |
| Stage 8: UI, safety, and legal controls | Not started |
| Firmware implementation | Not started |

The canonical stage table is [`docs/review/stages.md`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/stages.md). Firmware ownership, transport, safety, update and failure boundaries are accepted in [`ARC-0001`](../architecture/ARC-0001-three-domain-runtime-contract.md); toolchain, concrete wire encoding, directory structure and implementation remain later work.

## Accepted target constraints

- all-in-one product profile, the install-time non-aggression pledge, and three functional levels (`DEC-0002`, `DEC-0010`);
- conservative TX defaults and explicit selection of maximum available power (`DEC-0003`);
- reconsideration of legally and technically feasible legacy exclusions (`DEC-0004`);
- cost optimization only with proof of no product loss (`DEC-0005`);
- external M5 GNSS and external U214 LoRa+GNSS (`DEC-0006`, `DEC-0008`);
- an NMEA baseline and a conditional per-revision advanced CASIC profile without another GNSS (`DEC-0014`);
- an FM/RDS/ordinary-AM baseline and an open owner-imported SSB/CW patch loader without a bundled blob (`DEC-0015`);
- a conditional SA518 dual-band analog-voice target with an honest UHF-only SA868S fallback (`DEC-0016`);
- a dedicated STOP-dominant 4.0 V `VVOICE` rail for SA518 and separate stuffing/supply qualification for SA868S (`DEC-0025`);
- external M5 Unit NFC U216 as the first HF NFC backend, RFID2 as limited compatibility, and custom PN7160 as a qualification fallback (`DEC-0017`);
- dual-path consumer IR on C5 with TSOP38238 robust RX and TSMP95000 measured-carrier learning from 30 to 60 kHz (`DEC-0018`);
- calibrated three-antenna nRF24 RPD hit-rate sector comparison without invented RSSI/dBm, bearing, or VSWR (`DEC-0019`);
- OpenThread as the open Thread baseline and an optional conditional Zigbee adapter without closing the core product (`DEC-0020`);
- S3 as the sole baseline native-BLE owner, with C5 BLE default-off and no reduction of the full native nRF24 scope (`DEC-0021`);
- a complete owner-confirmed wishlist before multiple layouts and a consolidated resource budget (`DEC-0022`);
- a frozen 125-leaf wishlist with base/optional/deferred boundaries after delegated self-review (`DEC-0023`);
- a latched physical hard STOP that drives RP `RUN` and the S3/C5 reset/enable policy, independently inhibits/power-cuts external TX domains, and requires physical re-arm (`DEC-0024`, `DEC-0028`);
- onboard mono ES8311 audio with hardware-default analog bypass (`DEC-0009`);
- the accepted three-domain `PKG-0001/SYN-3A`: S3 N16R2 application/UI/audio/storage/native Wi-Fi/BLE, C5 N8R8 dual-band Wi-Fi/802.15.4/IR and RP2354A A4 direct 3×nRF24/CC1101/voice (`DEC-0028`);
- owner-controlled signed S3/C5/RP updates with A/B rollback, physical recovery and an open developer lifecycle (`DEC-0013`, `DEC-0028`), without enabling irreversible hardware lockdown.

## Open engineering dependencies

- `FND-0001`: C5's single general-purpose SPI controller cannot perform both legacy nRF-master and S3↔C5-slave roles.
- `FND-0003`: the audio direction is accepted, but pins, electrical behavior, drivers, HIL, and feature-level gates are not yet proven.
- `FND-0006`: the proposed key matrix and accepted audio controls collide on `U13.P10..P17`.
- `FND-0007`: the current artifact still has only an I²C-expander STOP input. `DEC-0024` fixes the target architecture, but latch/gate/rail firmware integration and fault-injection HIL are not implemented.
- `FND-0011`: SA868 now has PTT receive-default, PD power-down-default, and a physical low-power H/L ceiling. `DEC-0024/0025` fix the target STOP/power architecture; exact gates and HIL remain unimplemented.
- `FND-0013`: VOX has no microphone-capture path and is explicitly deferred to the consolidated audio/pin budget.
- `FND-0015`: both documented M5 NFC Units require a 5 V PORT.A power profile, while current hardware `J40/J41` provide 3.3 V; the electrical correction awaits the consolidated port/power design.
- `FND-0017`: the legacy IR source still has S3 ownership, an unqualified generic emitter/current path, and no proved STOP/TX-state/optical behavior. Its false `FAB-READY` label was removed and Q58 now has a reset-safe pull-down.
- `FND-0019`: the three generic nRF24 PA/LNA placeholders still use the S3 bus, exact modules/STOP/TX detectors are absent, and the post-dual-IR C5 resource budget is unproved. False `FAB-READY` labels were removed and shared CE now has a reset-safe pull-down.
- `FND-0021`: ESB/MouseJack/KeySniffer/BLE-compatible/interference claims require separate capability, security, licence, and HIL gates; no active C5 implementation currently proves them.
- `FND-0022`: the C5 hardware source was corrected from legacy N8R4/the false ANT2 feed to current N8R8 and the stock ANT1 path, but exact antenna/power/STOP/TX-live/EMC/AVL proof remains open.
- `FND-0023`: public C5 Wi-Fi raw TX does not support arbitrary management/deauth and `AUTO` is not simultaneous dual band; a patched vendor binary needs a separate provenance/licence/update/HIL boundary.
- `FND-0024`: the country/DFS/PMF/privacy state machine is not implemented; DFS SoftAP is excluded by the current contract.
- `FND-0026`: native BLE advertising scan is not a promiscuous connection-follow sniffer, a rotating address is not stable identity, and RSSI does not prove metres or direction.
- `FND-0027`: Continuity/iBeacon/Find My and attack labels require versioned corpus/spec/licence/peer proof; ordinary, passive, and disruptive BLE cases have distinct security gates.
- `FND-0028`: prior static nRF ownership maps are now reference-only archives, not inputs to the new synthesis. There is no standalone owner decision: the owner is derived only inside a complete zero-based package under `DEC-0026/0027`.
- `FND-0029`: the S3 memory variant, S3↔C5 transport, and recovery interfaces consume overlapping scarce pins. N8R8 is not a drop-in replacement for N8R2 because Octal PSRAM consumes GPIO35–37, while C5 4-bit SDIO conflicts with native USB on GPIO13/14.
- `FND-0030`: legacy 5 V voice power would exceed the accepted SA518 1 W profile. `DEC-0025` fixes the target with a dedicated 4.0 V rail; the legacy schematic and conducted HIL remain open.
- `FND-0032`: old matrix accounting incorrectly freed U214 RESET. The corrected candidate retains `EXT_RF_RST`, moves C5 BOOT to physical recovery, and aggregates touch IRQ; matrix/U14 still needs a decision and HIL.
- Legacy firmware documents and source candidates remain non-authoritative until their producing stages are reviewed.

## Current review work

The System/UI/storage capability slice is **Reviewed** under `REV-0002I`.

The GNSS/navigation slice [`REQ-GNSS-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-GNSS-0001-navigation-integrity.md) is **Reviewed** under `REV-0002K`. The owner accepted `IMP-0012/A` as [`DEC-0014`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0014-casic-gnss-profile.md): NMEA is the mandatory baseline of a qualified profile, while assistance and receiver-reported jamming/spoofing remain conditional on exact revision/firmware proof. Unsupported, timeout, and parser error mean `unknown`, not “no threat,” and host heuristics are kept distinct from receiver status.

`FND-0009` is closed at requirement level. UART/power hardware, parser, assistance source, actual Unit/U214 advanced-message support, RF self-desense, and HIL remain unimplemented evidence for later stages.

The Si4732 slice [`REQ-RX-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-RX-0001-si4732-receiver.md) is **Reviewed** under `REV-0002M`. The owner accepted `IMP-0013/A` as [`DEC-0015`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0015-open-si4732-ssb-patch-loader.md): an open bounded loader is in the target, the SSB blob is locally imported with distinct integrity/provenance states, and synchronous AM remains deferred pending separate proof. `FND-0010` is closed at requirement level; RF/frontend, patch rights/compatibility, loader, audio/storage/decoder, and coexistence HIL remain unimplemented.

The analog-voice slice [`REQ-VHF-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-VHF-0001-analog-voice-modem.md) is **Reviewed** under `REV-0002O`. The owner accepted `IMP-0014/A` as [`DEC-0016`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0016-conditional-sa518-dual-band-voice.md): SA518 is the preferred 136–174/400–470 MHz half-duplex analog-FM target, while SA868S remains an explicitly UHF-only fallback until qualification. [`DEC-0025`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0025-dedicated-4v-sa518-voice-rail.md) fixes separate 4.0 V `VVOICE` and fallback stuffing/supply profiles. The peak 2 W-class→1 W trade is accepted and is not recorded as zero-loss saving. `FND-0012` is closed at requirement level; microphone capture/VOX (`FND-0013`), exact STOP/power hardware, protocol, RF, audio, and HIL proof remain for later stages.

The NFC/RFID slice [`REQ-NFC-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-NFC-0001-hf-nfc-rfid.md) is **Reviewed** under `REV-0002Q`. The owner accepted `IMP-0005/A` as [`DEC-0017`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0017-u216-hf-nfc-backend.md): the external $7 M5 Unit NFC U216 is the first HF NFC target, the $4.95 RFID2 is limited compatibility, and custom PN7160 is a fallback only after qualification failure. The $2.05 accessory delta is accepted to retain A/B/F/V, ISO15693/FeliCa, limited emulation, and custom-mode scope; it does not affect the base BOM. `FND-0016` is closed at requirement level by explicit three-tier gates and by rejecting universal clone, one-frontend relay, key-recovery, LF 125 kHz, and payment-compliance overclaims. The exact U216 IC is NRND, and exact-revision/lifecycle, 5 V `PORT.A-NFC` (`FND-0015`), driver/SBOM, protocol, and HIL proof remain open implementation work.

The consumer-IR slice [`REQ-IR-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-IR-0001-consumer-infrared.md) is **Reviewed** under `REV-0002S`. The owner accepted `IMP-0015/A` as [`DEC-0018`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0018-dual-path-consumer-ir.md): C5 uses TSOP38238 for robust demodulated 38 kHz receive and TSMP95000 for measured-carrier learning from 30 to 60 kHz, consuming both C5 RX RMT channels; TSAL6200 is the first conditional 940 nm emitter candidate. Cheaper single-learning/fixed-38 variants lose an accepted capability and cannot be substituted silently. `FND-0018` is closed at requirement level; automatic 455 kHz/out-of-band learning remains deferred. Own remote/replay is Main, passive analysis is Lab, unknown replay is Controlled Zone `AUTHORIZED_TARGET`, and TV-B-Gone/brute-force/multi-code sweep is Controlled Zone `BOTH`. `FND-0017`, C5 pins/transport, exact BOM, STOP, optics, licences and HIL remain open implementation work.

The 3×nRF24 capability audit passed `REV-0002T`/`REV-0002U`: [`REQ-N24-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-N24-0001-three-nrf24-raw-2g4.md) preserves three simultaneous full-function radios and accepted [`DEC-0019`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0019-calibrated-rpd-three-antenna-hunt.md), a calibrated binary RPD hit-rate sector comparison that is never RSSI/dBm/bearing/VSWR. Ownership remained open at this stage-2 checkpoint and was later resolved to direct RP2354A control by `DEC-0028`. `REV-0002Z`/`AUD-0003`/`IMP-0021` remain historical idea/risk sources; `FND-0019` and `FND-0021` remain implementation gates.

The C5 Wi-Fi/IEEE 802.15.4 prerequisite audit passed `REV-0002V`, and final propagation under [`REV-0002W`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0002W-c5-wifi-802154-decision-propagation.md) makes [`REQ-W5-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-W5-0001-c5-wifi-ieee802154.md) **Reviewed**. The owner accepted `IMP-0018/A` as [`DEC-0020`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0020-open-first-thread-conditional-zigbee.md): OpenThread is the open baseline and Zigbee is an optional conditional adapter not required by core/raw/Thread builds. Main/Lab/Controlled Zone are separated, and the shared C5 2.4 GHz path is not represented as simultaneous radios. `FND-0025` is closed at requirement level. `FND-0022`–`FND-0024`, transport/STOP, binary lifecycle, and coexistence HIL remain implementation work. `IMP-0003` and a private patched Wi-Fi backend were not accepted automatically.

The native BLE prerequisite audit [`REV-0002X`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0002X-ble-prerequisites.md) is completed by [`DEC-0021`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0021-s3-native-ble-owner.md) and `REV-0002Y`: S3 is the sole baseline native-BLE owner, C5 BLE is default-off, [`REQ-BLE-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-BLE-0001-native-ble-and-security.md) is **Reviewed**, and `FND-0002` is closed. Only the extra experimental legacy-1M BLE-compatible nRF24 subset is limited; native nRF24 functions remain intact. Dedicated nRF52 connection sniffing and Bluetooth Mesh are retained as optional deferred-release profiles, not core-build blockers.

The remaining stage-2 slices are **Reviewed** under `REQ-W24-0001`, `REQ-SUB-0001`, `REQ-LORA-0001`, and `REQ-X-0001`. `INV-0004` accounts for 125/125 candidate leaves and twelve decisions from ten source extras; `REV-0002AD` closes stage 2 at requirement level.


## Reviewed architecture and next gate

Hardware stage 3 was restarted under [`DEC-0027`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0027-zero-based-capability-driven-architecture.md). [`FND-0033`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0033-legacy-layout-assumptions-leaked-into-synthesis.md) records why: prior work optimized legacy owners, buses and pins instead of independently deriving hardware from the accepted capabilities.

All previous stage-3 layouts and nRF-owner proposals are now reference-only archives. They do not determine firmware ownership, transport or HAL. The new canonical chain begins with hardware [`CAP-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/CAP-0001-zero-based-capability-input.md), which covers the full wishlist without pin/bus allocation and is **Reviewed** under `REV-0003J`. Hardware [`CON-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/CON-0001-hardware-neutral-concurrency-model.md) fixes mandatory parallelism, time-sharing and failure behavior without owner placement (`REV-0003K`), while [`RES-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/RES-0001-hardware-neutral-resource-demand.md) derives logical compute/interface/timing/power obligations without MCU/GPIO placement (`REV-0003L`). Hardware [`SRC-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/SRC-0001-primary-hardware-resource-facts.md) then records package/controller/peripheral facts from primary sources without choosing a layout (`REV-0003M`).

The zero-based method initially fixed only product-level roles. `DEC-0028` now resolves the full target: RP2354A directly owns all three nRF24 radios, CC1101 and voice real-time control; 1-bit SDIO and SPI+alert are the accepted links. [`ARC-0001`](../architecture/ARC-0001-three-domain-runtime-contract.md) propagates the runtime contract.

Hardware [`SYN-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/SYN-0001-zero-based-whole-device-candidates.md) compared three complete zero-based placements. `REV-0003N/3O` reviewed them without choosing a winner; the later atomic package selected the three-domain deterministic RP2354A A4 design in `DEC-0028`.

Hardware [`PIN-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PIN-0002-zero-based-exact-pin-maps.md) completes exact pin/controller/recovery mapping for all three candidates. `SYN-2A/2B` have no safe generic GPIO reserve; `SYN-3A` adds an RP2354 target but retains seven ordinary C5 GPIO. `FND-0034` moves `SYN-2A` U214/GNSS to C5 without dropping capability.

Hardware [`BUD-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/BUD-0002-zero-based-memory-traffic-budget.md) is reviewed under `REV-0003P`. It fixes the common S3/C5/RP memory and flash envelopes, the 600 kB/s aggregate admitted three-nRF profile, explicit overflow accounting, 1.5 MB/s IPC and storage/display/audio gates without choosing an owner. The theoretical single-bus maximum is not called lossless; failure of the admitted HIL automatically reopens split ownership.

Hardware [`PWR-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0001-zero-based-power-safety-envelope.md) passes `REV-0003Q`: all candidates share the same allowed-scenario rail floors and STOP/brownout ordering. `SYN-3A`'s auxiliary-controller allowance fits the common 3.3 V converter and adds energy, not another supply domain.

Hardware [`RFQ-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/RFQ-0001-zero-based-rf-zoning-coexistence.md) passes `REV-0003R`. It holds antenna geometry and RF paths constant, keeps mandatory three-nRF PRX, starts cross-domain receive pairs as qualification-only and all TX pairs as prohibited. Authorization does not bypass the shielded/conducted or spectrum gate.

Hardware [`CST-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/CST-0001-dated-candidate-cost-burden.md) passes `REV-0003S`. `2B` is the recurring-BOM minimum, `2A` the implementation-burden minimum, and `3A` the margin maximum with about a $1.10 conservative historical midpoint premium over `2A` and a third signed target. Hardware `FND-0035` corrects the old below-500 RP2354A stock claim using exact `SC1511-A4`; production quotes, traceability and assembly proof remain open.

Hardware [`PKG-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PKG-0001-zero-based-target-architecture-proposal.md) is accepted atomically in [`DEC-0028`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0028-accept-zero-based-syn-3a.md). Hardware `REV-0003U` verifies propagation into both target READMEs and [`ARC-0001`](../architecture/ARC-0001-three-domain-runtime-contract.md); stage 3 is **Reviewed**.

The active cross-repository gate is stage 4 component/BOM qualification. Hardware [`BOM-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/components/BOM-0001-stage4-component-evidence-register.md) is a reviewed complete register, not a component pass. Hardware [`BOM-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/components/BOM-0002-compute-clock-recovery-evidence.md) reviews the compute/clock/recovery facts. The owner accepted `IMP-0024/A` as [`DEC-0029`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0029-c5-v1.2-production-floor.md): production/release/qualification C5 requires ≥v1.2, with v1.0 restricted engineering-only; hardware `REV-0004C` reviews propagation. Hardware `LIB-0001/REV-0004D` finds that the legacy/mutable CAD source cannot reproducibly represent exact S3/C5/RP/TCA/crystal identities and opens `IMP-0025` on repository-vendored critical libraries. Firmware implementation remains unstarted and must consume the resulting exact manifests rather than infer hardware from legacy sources.
