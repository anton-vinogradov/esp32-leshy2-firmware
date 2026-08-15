# Leshy2 Firmware

> **Target product document.** This page is assembled from accepted, reviewed decisions and describes the intended finished software—not the current implementation. See the [current engineering state](docs/status/current-state.md) for maturity, blockers, and pending proposals.

- [Русская версия](README.ru.md)
- [Hardware target product](https://github.com/anton-vinogradov/esp32-leshy2)
- [Canonical cross-repository review ledger](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review)

## Finished software target

Leshy2 firmware turns the portable dual-MCU hardware into an autonomous all-in-one field instrument for observation, diagnostics, communications, navigation, maintenance, and authorized experiments. The product exposes capabilities through explicit operating and safety contracts rather than treating hardware reachability as permission to act.

## Three functional levels

1. **Main** — everyday tools, reception, diagnostics, navigation, maintenance, and legitimate communications outside a security-research scenario.
2. **Lab** — passive, defensive, and bounded security-research tools.
3. **Lab → Controlled Zone** — genuinely dangerous active or disruptive tools. Every entry requires a fresh non-suppressible warning and hold-to-confirm, plus an isolated environment, an explicitly authorized target, or both as required by the tool.

Every third-level tool remains independently disarmed after entry and enforces its own target, environment, frequency, power, duty-cycle, destructive-action, and stop gates. Leaving the section, reset, watchdog, device lock, session timeout, STOP, or loss of a required accessory disarms the level and requires the banner again on re-entry. The canonical contract is [`DEC-0010`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0010-three-functional-levels.md).

## Onboarding and safe transmission

- Initial setup requires explicit acceptance of the non-aggression pledge. It is a separate first gate and never substitutes for technical interlocks or applicable law.
- Every transmitter starts off after power-on, reset, brownout, watchdog, or update; every Lab tool starts disarmed.
- Initial TX uses a conservative profile specific to the radio path. Maximum available power requires an explicit action for the current scenario and is never restored as a global default.
- Active TX state and the selected power must be visible. A saved preference or restored screen cannot silently arm transmission.
- Normal S3/C5 update paths require owner-authorized signed images, independent target-MCU validation, and working-image rollback. Keys, offline build/signing tools, and custom developer firmware remain under owner control; hardware Secure Boot, Flash Encryption, and eFuse lockdown require a separate opt-in decision after recovery proof ([`DEC-0013`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0013-owner-controlled-signed-updates.md)).

## Accepted device integration

- ESP32-C5 is the target owner of all three nRF24 radios and IR TX/RX; firmware uses the final transport only after its architecture and hardware proof are accepted.
- Navigation supports the external M5Stack Unit GPS v1.1 and the GNSS backend of a qualified combined expansion, with only one GNSS backend active at a time.
- LoRa supports M5Stack U214 as the first `EXT-RF14` backend for common 868/915 profiles within module and regional limits, with only one LoRa backend active at a time.
- The onboard mono ES8311 path provides digital capture, playback, routing, and level-control prerequisites while ordinary listening and microphone voice retain a hardware-default analog path across MCU or codec failure.

## How this page grows

Only accepted product contracts are summarized here. Open findings, implementation maturity, and unaccepted proposals remain in the [current-state page](docs/status/current-state.md) and the hardware-owned review ledger. As reviewed `REQ-*` and architecture artifacts appear, this page will grow into the complete start document for the finished firmware product.
