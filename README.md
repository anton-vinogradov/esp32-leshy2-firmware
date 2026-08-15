# Leshy2 Firmware

The firmware design is being rebuilt from first principles together with the Leshy2 hardware.

- Previous documentation is preserved under [`drafts/legacy-2026-08-15/`](drafts/legacy-2026-08-15/README.md) and is not authoritative.
- The cross-repository review ledger is owned by the hardware repository under `docs/review/`.
- No firmware architecture, toolchain, protocol, directory structure, or feature promise is accepted until its stage is reviewed.
- The all-in-one profile is accepted: security functions progress from simple to the most serious and live only under **Lab**; initial setup requires acceptance of the non-aggression pledge. The canonical decision is [`DEC-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0002-project-vision.md).
- The ESP32-C5 owns the three nRF24 radios and IR.
- The S3↔C5 transport remains unresolved due to the ESP32-C5 single-GP-SPI conflict.

Current implementation status: **not started**.

*Русская версия: [README.ru.md](README.ru.md).*
