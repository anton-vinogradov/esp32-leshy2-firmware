# Firmware architecture — zero-based gate

- Status: **Waiting for zero-based hardware synthesis**
- Date: 2026-08-16
- Canonical method: [hardware `DEC-0027`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0027-zero-based-capability-driven-architecture.md)
- Current functional input: [hardware `CAP-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/CAP-0001-zero-based-capability-input.md)
- Current scenario input: [hardware `CON-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/CON-0001-hardware-neutral-concurrency-model.md)
- Current resource input: [hardware `RES-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/RES-0001-hardware-neutral-resource-demand.md)
- Current physical-fact input: [hardware `SRC-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/SRC-0001-primary-hardware-resource-facts.md)
- Current whole-device candidate input: [hardware `SYN-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/SYN-0001-zero-based-whole-device-candidates.md)
- Current exact-map input: [hardware `PIN-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PIN-0002-zero-based-exact-pin-maps.md)
- Current quantitative input: [hardware `BUD-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/BUD-0002-zero-based-memory-traffic-budget.md)
- Current power input: [hardware `PWR-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0001-zero-based-power-safety-envelope.md)
- Current RF input: [hardware `RFQ-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/RFQ-0001-zero-based-rf-zoning-coexistence.md)
- Current cost/burden input: [hardware `CST-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/CST-0001-dated-candidate-cost-burden.md)
- Atomic proposal: [hardware `PKG-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PKG-0001-zero-based-target-architecture-proposal.md) — **not accepted yet**

No prior layout, nRF owner, S3↔C5 transport, queue split, HAL boundary or pin assignment is a firmware architecture input. The fixed product roles are only those already accepted at capability level: S3 application/native Wi-Fi/BLE, and C5 Wi-Fi 2.4/5 GHz, IEEE 802.15.4 and dual-path IR.

The reviewed inputs no longer leave an analytical gap. `PKG-0001` proposes one complete result: S3 application/UI/audio/storage/native Wi-Fi/BLE, C5 dual-band Wi-Fi/802.15.4/IR, and an RP2354A A4 deterministic domain for 3×nRF24/CC1101/voice. This is still a proposal: firmware ownership and target README remain conditional until the owner accepts the package atomically.

The firmware architecture document will be created after the selected hardware package fixes:

- every programmable domain and its recovery/update boundary;
- control, event, bulk-data and safety transports;
- real-time owners and deadline/failure behavior;
- memory/storage/crypto budgets;
- STOP, TX lease and actual-TX evidence boundaries;
- optional accessory and open-build profiles.

Until then, this directory intentionally contains no speculative runtime contract. Target firmware READMEs remain product-level and do not claim an accepted implementation architecture.
