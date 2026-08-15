# Leshy2 Firmware

The firmware design is being rebuilt from first principles together with the Leshy2 hardware.

- Previous documentation is preserved under [`drafts/legacy-2026-08-15/`](drafts/legacy-2026-08-15/README.md) and is not authoritative.
- The cross-repository review ledger is owned by the hardware repository under `docs/review/`.
- No firmware architecture, toolchain, protocol, directory structure, or feature promise is accepted until its stage is reviewed.
- The all-in-one profile is accepted: security functions progress from simple to the most serious and live only under **Lab**; initial setup requires acceptance of the non-aggression pledge. The canonical decision is [`DEC-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0002-project-vision.md).
- Safe TX defaults are accepted: all transmitters boot off, Lab tools start disarmed, initial TX uses a conservative profile, and maximum power requires an explicit choice. The canonical decision is [`DEC-0003`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0003-safe-tx-defaults.md).
- For the three nRF24 radios and IR, only the **target C5-ownership constraint** is accepted—not a working architecture. Its feasibility remains unproven: the legacy topology requires the C5's sole general-purpose SPI controller to serve simultaneously as nRF master and S3↔C5 slave. The blocker is recorded as [`FND-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0001-c5-single-gp-spi.md).

Current implementation status: **not started**.

*Русская версия: [README.ru.md](README.ru.md).*
