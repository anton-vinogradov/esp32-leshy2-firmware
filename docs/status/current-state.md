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
- onboard mono ES8311 audio with hardware-default analog bypass (`DEC-0009`);
- target C5 ownership of 3×nRF24 and IR (`DEC-0001`), without a claim that the inter-MCU transport is solved.

## Open engineering dependencies

- `FND-0001`: C5's single general-purpose SPI controller cannot perform both legacy nRF-master and S3↔C5-slave roles.
- `FND-0002`: the BLE owner conflicts between legacy repositories.
- `FND-0003`: the audio direction is accepted, but pins, electrical behavior, drivers, HIL, and feature-level gates are not yet proven.
- `FND-0006`: the proposed key matrix and accepted audio controls collide on `U13.P10..P17`.
- `FND-0007`: the current STOP button is only an I²C-expander input and cannot independently kill TX.
- Legacy firmware documents and source candidates remain non-authoritative until their producing stages are reviewed.

## Current decision gate

[`IMP-0010`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/improvements/IMP-0010-hardware-stop-and-expander-consolidation.md) awaits the owner's decision:

- recommended A: independent hardware STOP, safe reboot, 3×3 key matrix, remove `U14`, and reuse freed LoRa-control pins for audio;
- B: retain `U14` and point-to-point buttons, but still add an independent hardware STOP.

The System/UI substage cannot receive **Reviewed** status until this choice is accepted and propagated.
