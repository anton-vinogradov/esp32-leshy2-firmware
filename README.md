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

- ESP32-C5 is the currently accepted target owner of all three full-function nRF24 radios and IR TX/RX; firmware uses the final transport only after its architecture and hardware proof are accepted.
- C5 Wi-Fi operates in one selected 2.4/5 GHz band; `AUTO` does not mean simultaneous operation. OpenThread is the open ordinary-Thread baseline, while Zigbee coordinator/router/end-device support is an optional conditional adapter with separate provenance/rights/SBOM/version/hash/signature/update/rollback gates and no proprietary-binary dependency for core/raw/Thread builds. Main covers owner-administered networks, Lab covers passive raw 802.15.4/Wi-Fi analysis, and Controlled Zone contains bounded active tests. DFS SoftAP, full/lossless monitor, and public deauth/disassociation support are not promised ([`DEC-0020`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0020-open-first-thread-conditional-zigbee.md)).
- ESP32-S3 is the sole baseline native Bluetooth LE owner for ordinary scan/advertise, GAP/GATT/SMP/HID, product identity, and bond storage; C5 BLE is default-off. This does not reduce the nRF24 radios: only their extra experimental legacy-1M BLE-compatible subset is limited because nRF24 is not a complete BLE controller ([`DEC-0021`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0021-s3-native-ble-owner.md)).
- Each of the three nRF24 paths retains the native transceiver feature set, independent PTX/PRX sessions, and simultaneous reception. They also provide 2.4 GHz energy sampling and calibrated binary RPD hit-rate sector comparison. Records retain sampling and calibration state; UI/exports never invent RSSI/dBm, bearing, angle, or VSWR. Passive ESB discovery is Lab, authorized single-target exploitation is Controlled Zone, and interference/carrier tests require both authorization and conducted or RF-shielded containment ([`DEC-0019`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0019-calibrated-rpd-three-antenna-hunt.md), [`REQ-N24-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-N24-0001-three-nrf24-raw-2g4.md)).
- Navigation supports the external M5Stack Unit GPS v1.1 and the GNSS backend of a qualified combined expansion, with only one GNSS backend active at a time. NMEA navigation is the baseline; assistance and receiver-reported interference/spoofing status are available only for a proven revision/firmware combination. Unsupported, timeout, and parser errors yield `unknown`, never a false “no threat,” and host heuristics are shown separately ([`DEC-0014`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0014-casic-gnss-profile.md)).
- LoRa supports M5Stack U214 as the first `EXT-RF14` backend for common 868/915 profiles within module and regional limits, with only one LoRa backend active at a time.
- The onboard mono ES8311 path provides digital capture, playback, routing, and level-control prerequisites while ordinary listening and microphone voice retain a hardware-default analog path across MCU or codec failure.
- The onboard Si4732 provides FM/RDS and ordinary LW/MW/SW reception. SSB USB/LSB and CW via BFO become available after the owner locally imports a compatible volatile patch through an open bounded loader; no third-party blob ships without proven provenance and redistribution rights. Synchronous AM is not promised pending separate proof ([`DEC-0015`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0015-open-si4732-ssb-patch-loader.md)).
- The preferred voice-radio backend is a half-duplex analog-FM SA518 covering VHF 136–174 and UHF 400–470 MHz at 0.5/1 W under explicit regional/licence profiles. A UHF-only SA868S fallback remains until price, supply, and RF qualification pass, and is never labelled dual-band. The 2 W-class→1 W peak trade is accepted for one VHF+UHF module; an external SMA is not represented as licence-exempt PMR446 equipment ([`DEC-0016`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0016-conditional-sa518-dual-band-voice.md)).
- HF NFC/RFID uses an external M5 Unit NFC U216 through a qualified 5 V `PORT.A-NFC`, with ordinary NFC-A/B/F/V tag operations in Main. Credential analysis belongs to Lab; recovery, credential writing/cloning, emulation, and a two-frontend relay belong to the Controlled Zone and require an authorized target. RFID2 is limited compatibility and a custom PN7160 design is only a qualification fallback. Exact U216 revision/lifecycle support is conditional, and the software makes no universal-clone, payment-compliance, or LF 125 kHz claim ([`DEC-0017`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0017-u216-hf-nfc-backend.md)).
- Consumer IR uses two C5 receive paths: TSOP38238 for robust demodulated 38 kHz reception and TSMP95000 for measured-carrier learning from 30 to 60 kHz; TSAL6200 is the first conditional 940 nm emitter candidate. Carrier provenance is retained in typed records. Own-device remote/replay is Main, passive analysis is Lab, unknown/security replay requires an authorized target in the Controlled Zone, and disruptive multi-code sweeps require both isolation and authorization. Automatic 455 kHz/out-of-band learning remains deferred ([`DEC-0018`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0018-dual-path-consumer-ir.md)).

## How this page grows

Only accepted product contracts are summarized here. Open findings, implementation maturity, and unaccepted proposals remain in the [current-state page](docs/status/current-state.md) and the hardware-owned review ledger. As reviewed `REQ-*` and architecture artifacts appear, this page will grow into the complete start document for the finished firmware product.
