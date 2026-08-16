# Firmware architecture — zero-based gate

- Status: **Waiting for zero-based hardware synthesis**
- Date: 2026-08-16
- Canonical method: [hardware `DEC-0027`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0027-zero-based-capability-driven-architecture.md)
- Current functional input: [hardware `CAP-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/CAP-0001-zero-based-capability-input.md)
- Current scenario input: [hardware `CON-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/CON-0001-hardware-neutral-concurrency-model.md)
- Current resource input: [hardware `RES-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/RES-0001-hardware-neutral-resource-demand.md)
- Current physical-fact input: [hardware `SRC-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/SRC-0001-primary-hardware-resource-facts.md)

No prior layout, nRF owner, S3↔C5 transport, queue split, HAL boundary or pin assignment is a firmware architecture input. The fixed product roles are only those already accepted at capability level: S3 application/native Wi-Fi/BLE, and C5 Wi-Fi 2.4/5 GHz, IEEE 802.15.4 and dual-path IR.

The three full-function nRF24 radios have no preselected MCU, controller, bridge or runtime owner. `CON-0001` fixes only mandatory concurrency, honest time-sharing and failure behavior; `RES-0001` adds logical compute/interface/timing/power obligations without placement. Firmware services will be derived only after several complete hardware candidates are compared.

The firmware architecture document will be created after the selected hardware package fixes:

- every programmable domain and its recovery/update boundary;
- control, event, bulk-data and safety transports;
- real-time owners and deadline/failure behavior;
- memory/storage/crypto budgets;
- STOP, TX lease and actual-TX evidence boundaries;
- optional accessory and open-build profiles.

Until then, this directory intentionally contains no speculative runtime contract. Target firmware READMEs remain product-level and do not claim an accepted implementation architecture.
