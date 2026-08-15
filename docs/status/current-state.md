# Leshy2 Firmware — current engineering state

> Snapshot: 2026-08-16. This page describes what is proven now. The finished software target is in the [firmware product README](../../README.md), and the finished device target is in the [hardware product README](https://github.com/anton-vinogradov/esp32-leshy2).

- Canonical evidence: [hardware-owned review ledger](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review)
- Русская версия: [current-state.ru.md](current-state.ru.md)
- Legacy reference only: [`drafts/legacy-2026-08-15/`](../../drafts/legacy-2026-08-15/README.md)

## Review and implementation progress

| Layer | State |
|---|---|
| Cross-repository stages 0–1 | Reviewed |
| Stage 2: capabilities and exclusions | In progress |
| Stages 3–6: architecture through hardware validation | Not started |
| Stage 7: firmware design | Not started |
| Stage 8: UI, safety, and legal controls | Not started |
| Firmware implementation | Not started |

The canonical stage table is [`docs/review/stages.md`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/stages.md). No firmware architecture, toolchain, protocol, directory structure, or implementation claim is accepted yet.

## Accepted target constraints

- all-in-one product profile, the install-time non-aggression pledge, and three functional levels (`DEC-0002`, `DEC-0010`);
- conservative TX defaults and explicit selection of maximum available power (`DEC-0003`);
- reconsideration of legally and technically feasible legacy exclusions (`DEC-0004`);
- cost optimization only with proof of no product loss (`DEC-0005`);
- external M5 GNSS and external U214 LoRa+GNSS (`DEC-0006`, `DEC-0008`);
- an NMEA baseline and a conditional per-revision advanced CASIC profile without another GNSS (`DEC-0014`);
- an FM/RDS/ordinary-AM baseline and an open owner-imported SSB/CW patch loader without a bundled blob (`DEC-0015`);
- a conditional SA518 dual-band analog-voice target with an honest UHF-only SA868S fallback (`DEC-0016`);
- external M5 Unit NFC U216 as the first HF NFC backend, RFID2 as limited compatibility, and custom PN7160 as a qualification fallback (`DEC-0017`);
- onboard mono ES8311 audio with hardware-default analog bypass (`DEC-0009`);
- target C5 ownership of 3×nRF24 and IR (`DEC-0001`), without a claim that the inter-MCU transport is solved.
- owner-controlled signed S3/C5 updates with rollback and an open developer lifecycle (`DEC-0013`), without enabling irreversible hardware lockdown.

## Open engineering dependencies

- `FND-0001`: C5's single general-purpose SPI controller cannot perform both legacy nRF-master and S3↔C5-slave roles.
- `FND-0002`: the BLE owner conflicts between legacy repositories.
- `FND-0003`: the audio direction is accepted, but pins, electrical behavior, drivers, HIL, and feature-level gates are not yet proven.
- `FND-0006`: the proposed key matrix and accepted audio controls collide on `U13.P10..P17`.
- `FND-0007`: the current STOP button is only an I²C-expander input and cannot independently kill TX.
- `FND-0011`: SA868 now has PTT receive-default, PD power-down-default, and a physical low-power H/L ceiling; independent STOP and controllable high power still require stage-3 proof.
- `FND-0013`: VOX has no microphone-capture path and is explicitly deferred to the consolidated audio/pin budget.
- `FND-0015`: both documented M5 NFC Units require a 5 V PORT.A power profile, while current hardware `J40/J41` provide 3.3 V; the electrical correction awaits the consolidated port/power design.
- Legacy firmware documents and source candidates remain non-authoritative until their producing stages are reviewed.

## Current review work

The System/UI/storage capability slice is **Reviewed** under `REV-0002I`.

The GNSS/navigation slice [`REQ-GNSS-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-GNSS-0001-navigation-integrity.md) is **Reviewed** under `REV-0002K`. The owner accepted `IMP-0012/A` as [`DEC-0014`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0014-casic-gnss-profile.md): NMEA is the mandatory baseline of a qualified profile, while assistance and receiver-reported jamming/spoofing remain conditional on exact revision/firmware proof. Unsupported, timeout, and parser error mean `unknown`, not “no threat,” and host heuristics are kept distinct from receiver status.

`FND-0009` is closed at requirement level. UART/power hardware, parser, assistance source, actual Unit/U214 advanced-message support, RF self-desense, and HIL remain unimplemented evidence for later stages.

The Si4732 slice [`REQ-RX-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-RX-0001-si4732-receiver.md) is **Reviewed** under `REV-0002M`. The owner accepted `IMP-0013/A` as [`DEC-0015`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0015-open-si4732-ssb-patch-loader.md): an open bounded loader is in the target, the SSB blob is locally imported with distinct integrity/provenance states, and synchronous AM remains deferred pending separate proof. `FND-0010` is closed at requirement level; RF/frontend, patch rights/compatibility, loader, audio/storage/decoder, and coexistence HIL remain unimplemented.

The analog-voice slice [`REQ-VHF-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-VHF-0001-analog-voice-modem.md) is **Reviewed** under `REV-0002O`. The owner accepted `IMP-0014/A` as [`DEC-0016`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0016-conditional-sa518-dual-band-voice.md): SA518 is the preferred 136–174/400–470 MHz half-duplex analog-FM target, while SA868S remains an explicitly UHF-only fallback until price, supply, PCB/power, and conducted-RF qualification pass. The peak 2 W-class→1 W trade is accepted and is not recorded as zero-loss saving. `FND-0012` is closed at requirement level; microphone capture/VOX (`FND-0013`), independent STOP, high-power control, exact hardware, protocol, RF, audio, and HIL proof remain for later stages.

The NFC/RFID slice [`REQ-NFC-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-NFC-0001-hf-nfc-rfid.md) is **Reviewed** under `REV-0002Q`. The owner accepted `IMP-0005/A` as [`DEC-0017`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0017-u216-hf-nfc-backend.md): the external $7 M5 Unit NFC U216 is the first HF NFC target, the $4.95 RFID2 is limited compatibility, and custom PN7160 is a fallback only after qualification failure. The $2.05 accessory delta is accepted to retain A/B/F/V, ISO15693/FeliCa, limited emulation, and custom-mode scope; it does not affect the base BOM. `FND-0016` is closed at requirement level by explicit three-tier gates and by rejecting universal clone, one-frontend relay, key-recovery, LF 125 kHz, and payment-compliance overclaims. The exact U216 IC is NRND, and exact-revision/lifecycle, 5 V `PORT.A-NFC` (`FND-0015`), driver/SBOM, protocol, and HIL proof remain open implementation work.

## Deferred architecture gate

[`IMP-0010`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/improvements/IMP-0010-hardware-stop-and-expander-consolidation.md) remains open, but [`DEC-0012`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0012-defer-imp-0010-to-pin-budget.md) defers the A/B choice to stage 3. No owner decision is requested until a consolidated pin/GPIO/resource budget covers both MCUs, expanders, fixed-function pins, inter-MCU transport, audio, UI/touch, external modules, and genuinely freed onboard GNSS/LoRa lines.

`FND-0006` and `FND-0007` remain open. The deferral neither selects `U14`/the 3×3 matrix nor proves a hardware STOP.
