# Firmware architecture — accepted zero-based target

- Status: **Reviewed**
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
- Accepted package: [hardware `PKG-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PKG-0001-zero-based-target-architecture-proposal.md), [decision `DEC-0028`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0028-accept-zero-based-syn-3a.md)
- Normative runtime contract: [`ARC-0001`](ARC-0001-three-domain-runtime-contract.md)

No legacy layout, nRF owner, transport or pin assignment was treated as an input. The accepted architecture was derived from the complete reviewed capability/concurrency/resource graph.

`PKG-0001/SYN-3A` is accepted: S3 owns application/UI/audio/storage/native Wi-Fi/BLE and external-profile orchestration; C5 owns dual-band Wi-Fi/802.15.4/IR; RP2354A A4 owns deterministic 3×nRF24/CC1101/voice control. S3↔C5 is 1-bit SDIO and S3↔RP is SPI+alert.

[`ARC-0001`](ARC-0001-three-domain-runtime-contract.md) fixes:

- every programmable domain and its recovery/update boundary;
- control, event, bulk-data and safety transports;
- real-time owners and deadline/failure behavior;
- memory/storage/crypto budgets;
- STOP, TX lease and actual-TX evidence boundaries;
- optional accessory and open-build profiles.

Current source remains unverified implementation material until later stages prove conformance. Architecture changes must follow hardware package change control rather than silently changing owners, transports, pins or safety behavior in code.
