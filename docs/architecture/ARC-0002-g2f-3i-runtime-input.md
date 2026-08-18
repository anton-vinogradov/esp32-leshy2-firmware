# ARC-0002 — G2F-3I runtime input

- Status: **reviewed paper-layout input; target firmware architecture remains blocked**
- Date: 2026-08-18
- Canonical hardware decision: [`DEC-0044`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0044-delegated-noninterference-layout.md)
- Hardware artifact: [`NIF-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/NIF-0001-digital-noninterference-layout.md)
- Exact generated map: [`G2F-pin-ledger`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/generated/G2F-pin-ledger.md)
- Reviewed principled pinout: [`PIN-0003`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PIN-0003-g2f-3i-principled-pinout.md), [`generated atlas`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/generated/G2F-3I-principled-pinout.md)
- Working-design decision: [`DEC-0051`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0051-principled-pinout-as-working-design.md)
- Signal groups: [`DEC-0045`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0045-one-active-signal-group.md)
- Quiet states: [`DEC-0046`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0046-unused-interface-quiet-by-default.md), [`QST-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/QST-0001-unused-interface-quiet-states.md)
- nRF RF acceptance: [`DEC-0047`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0047-qualified-nrf-mix-with-external-observer.md), [`N24H-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/N24H-0001-two-device-full-mix-fixture.md)
- nRF module/antenna choice: [`N24M-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/N24M-0001-exact-module-antenna-comparison.md), [`IMP-0040`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/improvements/IMP-0040-three-nrf-module-and-antenna-baseline.md)
- exact three-nRF electrical endpoint: [`N24E-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/N24E-0001-exact-three-nrf-electrical-endpoint.md), [`DEC-0091`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0091-exact-three-nrf-electrical-endpoint.md), [`REV-0005AV`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AV-i6-three-nrf-propagation.md)
- exact native S3/C5 RF evidence endpoints: [`NAT-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/NAT-0001-exact-s3-c5-native-rf-evidence-endpoints.md), [`DEC-0092`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0092-exact-s3-c5-native-rf-endpoints.md), [`REV-0005AW`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AW-i6-native-rf-propagation.md)
- exact CC1101 three-band endpoint: [`CCRF-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/CCRF-0001-exact-cc1101-three-band-endpoint.md), [`DEC-0093`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0093-exact-cc1101-three-band-endpoint.md), [`REV-0005AX`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AX-i6-cc1101-propagation.md)
- exact SA518 RF endpoint: [`VRF-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/VRF-0001-exact-sa518-broadband-rf-endpoint.md), [`DEC-0094`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0094-exact-sa518-broadband-rf-endpoint.md), [`REV-0005AY`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AY-i6-sa518-rf-propagation.md)
- exact IR endpoint: [`IRF-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/IRF-0001-exact-dual-receiver-transmit-and-optical-evidence-endpoint.md), [`DEC-0095`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0095-exact-ir-endpoint.md), [`REV-0005AZ`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AZ-i6-ir-propagation.md)
- exact Si4732 dual-input RF endpoint and corrected SOIC-16 map: [`RXF-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/RXF-0001-exact-si4732-dual-input-receive-frontend.md), [`DEC-0096`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0096-exact-si4732-dual-input-rf-endpoint.md), [`FND-0102`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0102-si4732-soic16-contact-map-was-shifted.md), [`REV-0005BA`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005BA-i6-si4732-rf-propagation.md), [`REV-0005BB`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005BB-si4732-soic16-pin-map-correction.md)
- consolidated I6 qualification: [`COX-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/COX-0001-consolidated-i6-qualification-matrix.md), [`DEC-0097`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0097-one-group-i6-qualification-and-fixtures.md), [`FND-0103`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0103-cross-group-hil-could-reopen-forbidden-concurrency.md), [`FND-0104`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0104-monolithic-receiver-audio-quiet-contract.md), [`REV-0005BC`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005BC-i6-consolidated-proof-propagation.md)
- exact independent M5 expansion boundary: [`EXP-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/EXP-0001-exact-m5-expansion-boundary.md), [`DEC-0098`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0098-exact-independent-m5-expansion-boundary.md), [`FND-0105`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0105-no-m5-presence-contact.md), [`REV-0005BD`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005BD-i7-m5-expansion-propagation.md)
- external antenna decision: [`DEC-0048`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0048-external-sma-antenna-bank.md)
- exact antenna count: [`DEC-0049`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0049-nine-dedicated-external-sma-paths.md)
- profiled antenna kit: [`DEC-0055`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0055-profiled-external-antenna-kit.md)
- feed-interface review: [`RFH-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/RFH-0001-module-to-external-sma-interface-review.md)
- exact codec fit: [`AUDIO-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/AUDIO-0001-es8311-exact-electrical-fit.md), [`REV-0005B`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005B-es8311-digital-fit-and-analog-gap.md)
- complete audio-path review: [`AUDIO-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/AUDIO-0002-complete-audio-path-comparison.md), [`FND-0067`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0067-audio-source-select-and-reset-bypass.md), [`REV-0005C`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005C-complete-audio-path-prerequisites.md)
- accepted audio topology: [`DEC-0054`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0054-fail-safe-complete-audio-path.md), [`REV-0005D`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005D-audio-decision-propagation.md)
- exact I5 audio/receiver endpoint: [`AUDIO-0003`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/AUDIO-0003-exact-audio-and-receiver-endpoint.md), [`DEC-0090`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0090-i5-exact-audio-and-receiver-paper-closure.md), [`REV-0005AU`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AU-i5-audio-receiver-propagation.md)
- service/IPC amendment: [`DEC-0059`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0059-full-service-over-1bit-sdio.md), [`REV-0005L`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005L-full-service-1bit-sdio-propagation.md)
- hard STOP and actual-TX evidence: [`DEC-0061`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0061-aon-stop-and-per-path-tx-evidence.md), [`SAFE-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/SAFE-0002-accepted-aon-stop-and-evidence-circuit.md), [`REV-0005O`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005O-i2-safety-decision-propagation.md)
- replaceable-cell boundary: [`DEC-0062`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0062-individually-replaceable-2s-cells.md), [`REV-0005Q`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005Q-battery-format-decision-propagation.md)
- exact holder and thermal coupling: [`DEC-0077`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0077-keystone-1048p-qualified-cell-profile.md), [`PWR-0016`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0016-keystone-1048p-holder-and-ntc-coupling.md), [`REV-0005AH`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AH-battery-holder-and-ntc-coupling.md)
- exact first cell target: [`DEC-0079`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0079-xtar-18650-4000mah-qualification-target.md), [`PWR-0018`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0018-xtar-18650-4000mah-cell-profile.md), [`REV-0005AJ`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AJ-exact-cell-propagation.md)
- diagnostic hardware lockout: [`DEC-0078`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0078-hardware-diagnostic-refractory-lockout.md), [`PWR-0017`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0017-hardware-diagnostic-refractory-lockout.md), [`REV-0005AI`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AI-diagnostic-lockout-propagation.md)
- accepted supervised 2S topology: [`DEC-0065`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0065-supervised-2s-battery-topology.md), [`PWR-0006`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0006-one-or-two-cell-topology-comparison.md), [`REV-0005T`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005T-supervised-2s-topology-decision-propagation.md)
- accepted 2S manager: [`DEC-0066`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0066-max17320-mspm0-fail-closed-manager.md), [`PWR-0005`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0005-replaceable-2s-manager-options.md), [`REV-0005V`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005V-2s-manager-decision-propagation.md)
- accepted deep-cell/circuit boundary: [`DEC-0067`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0067-no-in-device-deep-cell-recovery.md), [`PWR-0007`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0007-max17320-2s-surrounding-circuit.md), [`REV-0005X`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005X-deep-cell-policy-propagation.md)
- sink-only USB-PD frontend: [`DEC-0063`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0063-sink-only-30w-usb-pd-power-path.md), [`PWR-0004`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0004-accepted-usb-pd-front-end.md), [`REV-0005R`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005R-usb-pd-decision-propagation.md)
- fixed downstream rail tree: [`DEC-0068`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0068-separate-fixed-downstream-rails.md), [`PWR-0008`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0008-exact-downstream-rail-tree.md), [`REV-0005Y`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005Y-downstream-rail-tree-propagation.md)
- latch-off external eFuse: [`DEC-0069`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0069-latch-off-external-efuse.md), [`REV-0005Z`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005Z-latch-off-efuse-propagation.md)
- enable-qualified switched-rail PG: [`DEC-0070`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0070-enable-qualified-switched-rail-pg.md), [`PWR-0009`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0009-enable-qualified-switched-rail-pg.md), [`REV-0005AA`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AA-switched-rail-pg-qualification.md)
- external-eFuse passive/startup profile: [`DEC-0071`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0071-post-start-accessory-transient-profile.md), [`PWR-0010`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0010-external-efuse-passive-profile.md), [`REV-0005AB`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AB-external-efuse-passive-profile.md)
- exact converter passive profile: [`DEC-0072`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0072-exact-converter-energy-feedback-passives.md), [`PWR-0011`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0011-application-converter-passive-profile.md), [`REV-0005AC`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AC-application-converter-passive-profile.md)
- exact converter control-passive profile: [`DEC-0073`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0073-exact-converter-control-passives.md), [`PWR-0012`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0012-exact-converter-control-passives.md), [`REV-0005AD`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AD-converter-control-passive-profile.md)
- exact source/AON/POR/main sequence: [`DEC-0080`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0080-exact-aon-pg-por-main-sequence.md), [`PWR-0019`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0019-exact-source-sequence-and-power-reserve.md), [`FND-0084`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0084-abstract-main-source-sequencer.md), [`REV-0005AK`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AK-source-sequence-propagation.md)
- independent internal-rail containment: [`DEC-0081`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0081-independent-internal-rail-containment.md), [`PWR-0020`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0020-independent-post-buck-containment.md), [`FND-0085`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0085-uncontained-internal-buck-high-side-short.md), [`REV-0005AL`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AL-internal-rail-containment-propagation.md)
- consolidated I3 paper closure: [`DEC-0082`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0082-i3-paper-closure.md), [`PWR-0021`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0021-i3-consolidated-paper-closure.md), [`FND-0086`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0086-i3-paper-and-hil-closure-were-conflated.md), [`REV-0005AM`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AM-i3-paper-closure-propagation.md)
- exact protected product USB port: [`DEC-0083`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0083-exact-protected-product-usb-port.md), [`USB-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/USB-0001-exact-product-usb-c-and-protection.md), [`FND-0087`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0087-product-usb-ended-on-abstract-port.md), [`REV-0005AN`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AN-product-usb-port-propagation.md)
- exact protected display electrical endpoint: [`DEC-0084`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0084-exact-protected-display-electrical-endpoint.md), [`DSP-0006`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/DSP-0006-exact-display-rail-backlight-and-mate-profile.md), [`FND-0088`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0088-display-endpoint-still-contained-abstract-circuits.md), [`REV-0005AO`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AO-display-endpoint-propagation.md)
- exact isolated microSD endpoint: [`DEC-0085`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0085-exact-isolated-microsd-electrical-endpoint.md), [`STO-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/STO-0001-exact-isolated-microsd-endpoint.md), [`FND-0089`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0089-microsd-endpoint-was-backpowered-and-unprotected.md), [`REV-0005AP`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AP-microsd-endpoint-propagation.md)
- exact bounded pack diagnostic: [`DEC-0074`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0074-bounded-pack-diagnostic-pulse.md), [`PWR-0013`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/PWR-0013-exact-pack-diagnostic-frontends.md), [`FND-0078`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0078-mspm0-pa24-forbids-injection-current.md), [`REV-0005AE`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/reviews/REV-0005AE-pack-diagnostic-profile.md)

## Boundary

This document records the firmware consequences of the leading reviewed
**paper** layout. It does not start a toolchain, freeze three production
images, select exact peripheral drivers or restore the superseded `ARC-0001`
as target. Physical RF, exact parts/power/mechanics and HIL can still remap the
architecture before the atomic decision.
Hardware `DEC-0051` makes this reviewed projection visible as the current G3
working design. It does not convert the input into a frozen firmware HAL or G7
architecture.
Hardware `DEC-0082/PWR-0021` now mark the I3 paper electrical subset reviewed
and activate dependent I4 paper work. That maturity only makes the exact
source/rail/fault contracts consumable here: procurement and prototype HIL
remain open, measured thresholds do not appear from calculations, and any
functional or derating conflict reopens I3 before it changes this input.
Hardware `DEC-0083/USB-0001` now close the first I4 paper endpoint. Firmware
may consume a protected native S3 USB2 path, sink-only CC path, automatic
port disconnect and the absence of Alt Mode. It may not promote unmeasured
USB Full-Speed RC/SI, ESD/short-to-VBUS behavior or the fixture-only protector
`FLT` signal into a production runtime claim.
Hardware `DEC-0084/DSP-0006` close the second I4 paper endpoint. Firmware may
consume default-low display/touch reset, common protected logic power,
reset-dark PWM backlight and hardware latch-off with power-cycle-only
recovery. It has no direct backlight-fault GPIO and therefore must not invent a
runtime fault readback from the fixture-only `FAULT_N` point. The exact first
connector candidate does not freeze a production mate or vendor init table.
Hardware `DEC-0088/DSP-0007` later identifies exact integrated `ST77922`,
touch address `0x38` and active-low TP_INT. Firmware consumes one fixed
10-kOhm-plus-`SN74LVC1G07DCKR` path to shared GPIO37; no polarity profile or
inverting population is supported. Specimen readback/IRQ/reset proof remains
upstream HIL.
Hardware `DEC-0085/STO-0001` close the third I4 paper endpoint. Firmware may
consume an always-readable active-low detect input, a fail-low/QOD switched
card rail, Ioff host-to-card isolation and a DAT0/MISO return enabled only while
`SD_CS_N` is low. It must perform SPI-mode entry before other bus traffic after
every card-power cycle and distinguish clean unmount from unexpected removal.
No unmeasured media, throughput, corruption-window or fault behavior becomes a
production claim.
Hardware `DEC-0089/IOX-0001` then close the consolidated I4 paper electrical
block. Firmware consumes exact main TCA6424A address `0x22`, fixed pack target
address `0x2A`, shared open-drain interrupt discovery, fixture RESET_N and
full `3V3_MAIN` cycle recovery. P22 STOP observation remains low in RUN/high
when latched; P23 S3 evidence remains active low. Their new AON open-drain
isolation changes no logical polarity and grants no control over STOP or TX.
Physical, signal-integrity and no-back-power behavior remains upstream HIL;
I4 review does not freeze a HAL or authorize implementation.
Hardware `DEC-0090/AUDIO-0003` then close the I5 paper electrical block.
Firmware may consume exact ES8311 address `0x19`, Si4732 two-address specimen
probing, supervisor-held power/interface admission, reset-default receive/
electret paths, P00/P01/P02 controls and the exact endpoint mode table below.
It may not claim measured gain, noise, pop/click, RF immunity, crystal trim or
concurrent-load performance before HIL. I5 review does not freeze a HAL or
authorize implementation; I6 RF front ends are now active upstream.
Hardware `DEC-0091/N24E-0001` now close the first I6 paper subblock. Firmware
may consume three switched-rail Ioff-isolated digital endpoints, exact common
power sequencing and per-radio directional forward-power evidence. It may not
call the Ebyte `IPX` receptacle U.FL, infer a threshold from the calculation or
claim target coexistence before specimen and T1 HIL. I6 remains active for all
other RF endpoints and the consolidated result.
Hardware `DEC-0092/NAT-0001` then close the native S3/C5 paper subblock.
Firmware may consume independent S3 2.4-GHz and C5 2.4/5-GHz actual-TX
channels after real external module contacts, exact dual-band directional
couplers and complete LTC5532 support. It may not enable C5 ANT2, invent a
shared native antenna, infer detector thresholds from typical values or claim
regional EIRP before full-feed loss and antenna qualification. Exact jumper,
chassis connector, thresholds and coexistence remain upstream physical gates.
Hardware `DEC-0093/CCRF-0001` next close the exact CC1101 paper subblock.
Firmware may consume dedicated RP PIO0 SM3 ownership, powered-off P03/P04
three-band selection, dual-ended branch isolation and final-line AD8314
evidence. It may not hot-switch a band, infer a physical switch position from
an expander register, treat inbound RF as authorization, invent detector
thresholds or claim the first-pass matching coupon before VNA/conducted HIL.
The final chassis SMA, measured feed loss, legal profiles and coexistence remain
upstream gates.
Hardware `DEC-0094/VRF-0001` then closes the SA518 RF paper subblock. Firmware
may consume physical ANT contact 7, one direct protected 50-Ohm SMA feed and a
separate AD8314 actual-TX channel sampled through exact 5.1-kOhm/52.3-Ohm
attenuation. It may not treat inbound RF as PTT authorization, infer thresholds
from nominal arithmetic, reuse the 7-V CC TVS profile, or invent an external
VHF/UHF filter bank. A measured conducted failure reopens the hardware
subblock; P05 was free at that I6 checkpoint and is later consumed by
`DEC-0098` for native-Unit power. Final SMA, antenna lots, evidence
thresholds, emissions/legal proof and coexistence remain upstream gates.
Hardware `DEC-0095/IRF-0001` then closes the separate IR paper subblock.
Firmware may consume exact simultaneous robust-envelope and carrier-cycle
inputs, a reset-off/Ioff-isolated receive rail, a STOP-qualified current-limited
emitter and physical optical evidence. It may not label the demodulated path as
measured carrier, infer optical safety from the 69.7-mA paper bound, use
evidence as authorization or overlap receive/learn with transmit. Receiver
identity, optical geometry, thresholds, duty/temperature/IEC 62471 proof and
whole-device coexistence remain upstream gates.

## Candidate runtime domains

| Domain | Candidate local ownership | Dedicated transports/resources | Local invariants |
|---|---|---|---|
| S3 | product policy/UI, display, audio, microSD, native BLE, Unit profile | SPI3 to RP, 1-bit SDMMC host to C5, SPI2 display+SD scheduler, I²S0, internal I²C0, separate I²C1/UART1/GPIO Unit profile | UI feedback ≤100 ms; storage stalls never block radio leases/queues; native USB + default UART0 + EN/BOOT service |
| C5 | 2.4/5 GHz Wi-Fi, IEEE 802.15.4, dual-path IR RX and IR TX | exclusive 1-bit SDIO slave to S3; direct IR RMT/evidence | local RF/IR queues, lease expiry and safe-off; native USB + UART0 + EN/BOOT/strap service |
| RP2354B | 3×full-function nRF24, CC1101, voice/PTT and U214 LoRa/GNSS | four independent PIO0 compatibility-radio buses, PIO1 U214 SPI, UART1 GNSS, isolated U214 I²C, hardware SPI1 to S3 | direct IRQ/GDO/BUSY/PTT; no peer-radio bus wait; USB+SWD+RUN+BOOTSEL recovery |

The exact RP map uses the real B-package PIO base rule: PIO0 and PIO1 select
the `GPIO16..GPIO47` window, and every PIO data pin is in `GPIO30..GPIO46`.
The hardware validator also locks the fixed mux sets for S3 USB/UART0, C5
1-bit SDIO/native USB, and RP SPI1/UART0/UART1/I²C0; firmware must not remap
these as generic GPIO-matrix choices. The M5 Unit UART profile uses UART1 on
GPIO7/8 so it cannot create a second branch on the permanent S3 UART0 service
route.

Persistent capacity is budgeted before runtime implementation: RP uses 5/12
PIO state machines and 13/16 DMA channels; S3 uses 3/5 GDMA TX and 3/5 GDMA RX
channels. The reserves are not permission for an unreviewed driver to claim a
permanent channel: any new fixed DMA consumer changes the upstream contract.
The quiet-state decision also consumes RP GPIO15/GPIO23 for common nRF and CC
power gates and C5 GPIO4 for the IR frontend gate. Direct free GPIO reserve is
later reduced by `DEC-0052`, which consumes S3 GPIO41/GPIO42 for QSPI D2/D3.
After `DEC-0054` consumes S3 GPIO6 for `AUDIO_ARM`, only GPIO47 remained free.
`DEC-0086` consumes GPIO39/GPIO47 as the direct PCNT0 encoder phase pair, so
firmware cannot invent another direct S3 or RP control. Hardware derives these
figures from the machine source: S3 is `33 used / 3 reserved / 0 free`, C5 is `14/6/1`, RP is `48/0/0`,
and the main slow plane is `24/0/0`: P27 selects the receive source, while I5
uses P00 for RX/microphone capture, P01 for speaker enable and P02 for
headphone absence. P03/P04 are CC1101 rail-off band truth bits and P05 requests
the independent native-Unit power branch. The previously published C5/RP reserve
was stale and is corrected by `FND-0059`. GPIO43/44 remain permanent UART0
service; GPIO6 `AUDIO_ARM` and GPIO39/47 encoder capture are normative machine
inputs.

## Mandatory scheduler/queue contract

- `nrf0`, `nrf1`, `nrf2`, `cc` and `u214` are separate event sources with
  independent IRQ timestamps, queues and overflow/drop counters. A shared
  worker may dispatch them, but no lock may serialize physical bus ownership.
- `SG-N24` keeps all three nRF powered and active. Each independently selects
  `PRX` or `PTX`; `3R`, `1T+2R`, `2T+1R` and `3T` must execute concurrently.
  A local TX must not silently put peers in standby or create unreported RX
  gaps. Physical sensitivity limits are profile evidence, not scheduler gaps.
  Entry asserts the common STOP-qualified rail request, waits at least 100 ms
  after rail validity for the nRF24 power-on-reset maximum, then reads and
  validates all three identities/configurations before admitting the group.
  Any missing/mismatched radio returns the whole group to `NONE`; peers are not
  silently used as a degraded two-radio product.
- RP↔S3 SPI must qualify ≥1.5 MB/s framed payload and alert-to-read ≤250 µs;
  control/safety events preempt bulk records and a stalled peer cannot retain
  TX authorization.
- C5↔S3 1-bit SDIO at 20 MHz provides 2.5 MB/s raw and must qualify
  ≥1.5 MB/s framed payload, ≤70% admitted occupancy and ≤2 ms control RTT; it
  exclusively owns the S3 SD/MMC host. Four-bit mode is not a runtime option:
  it is an upstream fallback only after failed HIL and a new service-isolation
  decision.
- Native radio service keeps two distinct evidence identities: `s3_native_24`
  covers only S3 channels 2412…2484 MHz; `c5_native` covers C5 channels
  2412…2484 MHz and 5180…5885 MHz. C5 uses ANT1 only. ANT2 is not a profile,
  antenna choice or automatic fallback and remains default-disabled/no-connect.
- Every native TX lease names owner, band/channel, regional profile, requested
  power, antenna/feed profile and evidence-calibration revision. The admitted
  power/EIRP limit subtracts the measured loss of that exact
  module→jumper→PCB mate→coupler→chassis feed; a nominal coupler insertion-loss
  value is not a substitute for the completed feed measurement.
- During a commanded native transmission, the matching independent evidence
  channel must assert inside its calibrated time/power window and return quiet
  inside the calibrated decay window after TX ends. Missing, stuck or
  inconsistent evidence expires the lease, disables the affected TX profile
  and reports `Unknown`; it never authorizes TX. Strong inbound RF may cause a
  conservative false positive and delay quiet/group transition, but cannot
  create, extend or validate a transmit lease.
- S3 UI/display/storage and C5 IPC servicing remain bounded system planes while
  a native group is active. Native radio queues and lease deadlines cannot wait
  for a display refresh, microSD transaction or peer-radio operation; the
  complete device must still pass active-receiver desense/coexistence HIL.
- CC service exposes three hardware endpoint identities: `cc_315` uses
  V1/V2=`10` and RF1, `cc_433` uses `01` and RF2, and `cc_868_915` uses `11`
  and RF3. The last identity still requires distinct legal `868` and `915`
  channel/power profiles; sharing one physical branch never merges regional
  policy. V1/V2=`00` is isolation, not a transmit or receive profile.
- S3 is the sole writer of TCA6424A P03/P04; RP alone owns CC PIO/DMA, the
  CC rail request and transceiver state. A versioned cross-domain transaction
  binds requested endpoint, regional profile and generation. S3 may acknowledge
  `BAND_PRESELECTED` only after RP reports `CC_OFF/EVIDENCE_QUIET`; RP may power
  the endpoint only after that matching acknowledgement. Timeout, reset or a
  generation mismatch leaves `00`/rail-off and invalidates the transaction.
- Every CC TX lease names endpoint, channel, regional profile, requested power,
  antenna/feed identity, calibrated complete-feed loss, evidence-calibration
  revision and expiry. During commanded TX, final-line
  `GJM1555C1HR47BB01D`→`AD8314ACPZ-RL7` evidence must assert and decay within
  the qualified per-band/per-power windows. Missing, stuck or contradictory
  evidence expires the lease and powers down the path. Strong inbound RF may
  conservatively assert this non-directional detector and delay quiet, but can
  never create, extend or validate a lease.
- Every voice TX lease names `voice_vhf` or `voice_uhf`, exact channel,
  regional profile, requested H/L power, separately labelled antenna/feed
  identity, evidence-calibration revision and expiry. An unknown, wrong-band or
  changed antenna leaves both voice rail and PTT disarmed.
- Voice entry arms the evidence hold before the protected 4-V rail, validates
  the SA518 identity/configuration/ready state and only then permits the
  independent AON-gated PTT. During PTT, the matching `AD8314ACPZ-RL7` channel
  must assert inside its per-band/per-power window. Missing evidence revokes
  PTT and rail as `evidence_missing`; evidence can never create a lease.
- Voice shutdown forces RX first, waits for evidence quiet, removes the 4-V
  rail and accepts quiet only inside the calibrated finite hold/decay window.
  Strong inbound RF may report `external_rf_present` and conservatively delay
  quiet, but never extends PTT. Timeout is fail-closed and requires a fresh
  lease after the RF state clears.
- Display and microSD deliberately share SPI2. `DEC-0052` assigns direct QSPI
  D2/D3 to S3 GPIO41/42 and replaces stale `256 B` slicing with measured
  `<=1 ms` uninterrupted display occupancy. The scheduler uses separate CS,
  per-device modes/clocks, QSPI only while SD CS is high, derived byte quanta,
  bounded SD commands/data chunks and critical-UI priority. Combined HIL must
  prove shared-D1 high-Z/no-contention, first visible response ≤100 ms, storage
  ≥4.0 MB/s, 1.5 MB/s record and survival of a measured 250 ms card stall.
- `DEC-0085` makes storage session admission explicit. With `SD_PWR_EN` low,
  stop SPI2 work and park `LCD_CS_N`/`SD_CS_N` high, SCK low and MOSI/D1 high.
  Accept a debounced insertion, enable the rail, wait for its bounded rise and,
  with every other CS high, issue low-speed startup clocks and enter SPI mode
  before display work resumes. Timeout or failed identity leaves the rail off
  and the storage service unavailable; it does not weaken the sequence.
- Clean unmount first rejects new writers, synchronizes and drains queues,
  closes the filesystem, raises CS, clears `SD_PWR_EN` and waits for the
  qualified QOD discharge boundary before reporting safe removal. Unexpected
  detect loss aborts new I/O, marks the unwritten tail possibly lost, preserves
  last committed metadata and requires checked recovery/remount. Firmware must
  never label that path a clean or lossless recording.
- Hardware reset sequencing is independent of that scheduler. On boot, keep
  GPIO40 low and both expander reset outputs low until `3V3_MAIN` is stable;
  issue a pulse of at least 10 us, release display reset and wait at least
  120 ms before Sleep Out, then release touch reset and wait at least 100 ms
  before I2C use. Enable PWM last. On controlled shutdown, disable PWM, enter
  Sleep In, assert both resets and only then permit main-power removal. Never
  auto-retry a latched backlight branch; a new attempt requires a complete
  main-power cycle and fresh display initialization.
- Internal I²C contains only slow UI/audio/receiver/control endpoints. Exact
  currently closed addresses are ES8311 `0x19`, TPS25751D `0x20`, main
  TCA6424A `0x22`, pack admission `0x2A` and ST77922 `0x38`; UI TCA9534A
  remains candidate `0x3F` until assembled HIL. Si4732 initialization probes
  both public strap outcomes `0x11` and `0x63` until specimen HIL freezes its
  physical identity. The
  dedicated TCA9534A at candidate address `0x3F` holds P0…P3 low in idle, so
  any D-pad/OK, BACK, OPT, F1, F2 or encoder-push change starts a bounded 4×3
  scan through P4…P6; P7 is reserved. Encoder A/B edges never use that bus:
  PCNT0 captures GPIO39/GPIO47 and
  the driver accepts only valid Gray transitions/full detents after qualified
  chatter filtering. No concurrent display/storage/radio load may lose or
  invent a detent. PTT,
  radio FIFO/IRQ/GDO/BUSY, hard STOP and timing evidence never wait for it.
  P27 selects the ordinary Si4732-versus-SA518 receive-audio source; P00
  selects chosen-RX versus local-microphone capture, P01 enables the speaker
  only when no headphones are inserted, and P02 reads headphone absence.
  None is a safety-deadline line and none asserts PTT. TPS25751D is another bounded
  target on this bus. Its active-low IRQ shares GPIO37 with TCA6424 `INT`, UI
  TCA9534A `INT_N`, pack admission and the fixed ST77922 touch adapter; every wake
  reads all enabled status
  blocks and no driver assumes a unique source. ST77922 responds at exact
  7-bit address `0x38`; active-low TP_INT has a 10-kOhm raw pull-up and fixed
  non-inverting open-drain `SN74LVC1G07DCKR`. Firmware has no inverter profile
  and does not replace the IRQ with polling.
  TCA6424A startup verifies address/identity and all-input defaults. Recovery
  first performs bounded bus clocking plus STOP; if the expander remains
  unavailable, firmware enters safe/degraded operation and requests a complete
  `3V3_MAIN` cycle rather than endlessly retrying. Fixture diagnostics may
  assert `SLOW_IO_RESET_N` directly, but product runtime does not own that pad.
- U214 external I²C is a separate RP branch behind TCA4307; stuck-low/hot-plug
  cannot stall the internal S3 control bus or Unit profile.

### Exact M5 expansion runtime admission

- U214 and native Unit are two independent power domains. P17 requests only
  U214; P05 requests only native Unit. Either may keep the common fixed-5-V
  converter alive, but each exposed output has its own latch-off,
  true-reverse-blocking eFuse.
- There is no hardware presence bit. `P26=UNIT_READY` is protected-rail
  readiness after admission, not proof that a connector is mechanically
  occupied. Firmware must not restore the removed `ACCESSORY_PRESENT_N`
  abstraction or background-poll an unpowered connector.
- State for each branch is `OFF → REQUESTED → POWER_PENDING → READY → IDENTIFY
  → ACTIVE → QUIETING → OFF`, with `FAULT_LATCHED` reachable from every
  powered state. Signal isolation remains disabled until branch READY and the
  host 3.3-V domain are valid.
- `U214_READY` enables the three Ioff SPI/UART/control buffers and permits
  TCA4307 connection; `U214_I2C_READY` is separate stuck-bus/segment evidence.
  Both must match the expected transition before RP starts PIO1, UART1 or I²C0.
- `UNIT_READY` permits `TXS0102DCUR` OE. The signed profile declares I²C,
  UART, push-pull GPIO, open-drain GPIO or candidate 1-Wire use and all required
  pulls/timing. 1-Wire is enabled only by a passed exact accessory/cable HIL
  profile, never from the generic GPIO capability alone.
- Identity is profile-specific after power: exact U214 assembly/peripheral
  readback for Cap, exact driver identity/protocol for Unit. Unknown/mismatch,
  reverse-source/external-power, overcurrent, stuck bus, bad READY order or
  timeout disables isolation and the branch, records evidence and requires a
  fresh explicit user session; there is no automatic retry loop.
- U214 downstream Port A load is part of the U214 manifest and current budget.
  Simultaneous U214 + downstream Unit + native Unit is legal only for an exact
  manifest that passed combined power/thermal/no-stall HIL.
- A generic USB-host/high-throughput HAL remains absent. A concrete future
  RF/SDR accessory may derive a new transport only after naming its bandwidth,
  power, legal, isolation and recovery requirements.

## Signal-group and quiet-state contract

- Exactly one top-level `active_signal_group` exists; boot/reset/fault/STOP
  enters `NONE` with every TX hardware-off. `SG-N24` is one group containing
  three concurrently full-function transceivers, not three mutually exclusive
  groups.
- Before a group switch, firmware revokes leases, proves actual TX off, stops
  controllers/DMA, establishes endpoint-safe levels, isolates/high-Z signal
  paths and only then rail-gates every non-member interface. Wake powers and
  settles the endpoint while I/O remains isolated, then connects safe parked
  signals. Failure or unknown evidence leaves `NONE`; prior TX state is never
  restored.
- For `SG-N24`, CE0/1/2 go low and CSN0/1/2 high before all three PIO/DMA
  engines stop. Firmware waits until the three forward-power evidence bits are
  inactive, then clears the common rail request. The AD8314 enable-hold remains
  physical through QOD fall; software neither shortens it nor treats an early
  detector shutdown as proof. Re-entry begins only after the measured rail
  discharge/no-backpower interval.
- CC band entry is strictly `OFF → PRESELECTED → POWERING → READY_RX`; TX adds
  `TX_ARMED → TX`, and any exit passes through `QUIETING → OFF`. To change
  bands, reject new work, revoke the lease, command CC IDLE with CSN high and
  SCLK/SI parked, wait for final-line evidence quiet, stop PIO/DMA, remove the
  CC rail and wait the qualified discharge interval. Only then may S3 change
  P03/P04. After the matching generation is acknowledged, RP powers the rail,
  waits the qualified crystal/power interval, reads CC identity and the complete
  register profile, then admits RX or TX. No powered-state P03/P04 write is valid.
- S3 UI CPU, RP arbiter, power/fault supervision and required IPC remain system
  planes. Their peripheral clocks run only for bounded transactions, and they
  must pass active-receiver EMI HIL rather than being mislabeled powered-off.
- No background scan, advertising, beacon, periodic service log, accessory
  poll or update check may wake a non-member interface. It requires a visible
  manifest member or an explicit group switch.
- Quiet is verified from rail/current/status/actual-TX evidence where available;
  a successful driver call alone is not proof.

### Consolidated I6 runtime and evidence contract

- The catalog is `SG-N24`, `SG-S3-24`, `SG-C5-NATIVE`, `SG-CC`, `SG-VOICE`,
  `SG-BROADCAST`, `SG-U214`, `SG-IR` and one exact `SG-EXT-*` manifest.
  Cross-group runtime is prohibited. Contained cross-group injection is
  Laboratory characterization only and never grants runtime permission,
  regardless of a successful HIL result.
- Allowed concurrency exists only inside the active manifest: all required
  three-radio nRF PTX/PRX mixes, visible native S3/C5 time division and exact
  U214 LoRa/GNSS members. UI, STOP, power/fault supervision and bounded IPC are
  system planes; storage, audio and diagnostics are support planes only when
  declared by that group profile.
- Quiet control is split into independent `RECEIVER_QUIET`,
  `CODEC_AUDIO_QUIET` and `VOICE_INTERFACE_QUIET` contracts. This lets
  `SG-BROADCAST` keep Si4732 active and `SG-VOICE` keep SA518 interfaces active
  without waking the other receiver/audio boundaries. Storage and service use
  separate `STORAGE_QUIET` and `SERVICE_IPC_QUIET` contracts.
- Every installed-group transition passes through `NONE` in this order:
  revoke leases → prove actual TX off → stop controller/DMA → park and isolate
  pins → remove and verify rail/discharge → self-test the new group → publish
  visible identity → require a separate TX arm. A failed or unknown step stays
  in `NONE`; prior TX state is never restored.
- One timestamped evidence bundle covers the exact manifest, isolated
  baseline, every foreign boundary quiet, maximum valid system-plane load,
  allowed intragroup mixes, transitions, STOP/reset/brownout/stuck-line faults
  and thermal/legal limits. Raw traces must prove: no nRF FIFO miss; CC service
  independent of nRF/U214; no U214 UART overflow; S3↔RP alert-to-read `<=250 us`
  and framed throughput `>=1.5 MB/s`; S3↔C5 `>=1.5 MB/s`, admitted occupancy
  `<=70%` and control RTT `<=2 ms`; display non-preemptible occupancy `<=1 ms`;
  ordinary UI response `<=100 ms`; continuous audio DMA; and no lost or
  invented encoder detents.

This is reviewed paper qualification input, not measurement. Conducted, OTA,
optical, no-stall, thermal and fault HIL remain `not_executed`; a failed trace
reopens the owning hardware subblock and cannot broaden runtime permission.

## Replaceable-cell admission input

- The battery has two individually replaceable exact
  `XTAR 18650 4000mAh` protected button-top cells in a supervised 2S
  arrangement. The pair is `28.8 Wh` nominal; each cell is `4000 mAh` typical /
  `3800 mAh` minimum, `10 A` maximum continuous discharge, `2 A` standard
  charge and `<=40 mOhm` initial-resistance class. Individual replacement does
  not imply that an arbitrary cell or combination is valid. Both admitted
  cells are required for battery operation.
- The exact reference holder is polarized `Keystone 1048P`; the selected cell
  maximum envelope is `18.7 × 69.7 mm`. Raw flat-top, XTAR USB-equipped and
  third-party protected variants are unsupported even when they share a core.
  Mechanical polarity remains below firmware, while exact-cell identity is a
  declared qualified profile: neither S3 nor the admission MCU can authenticate
  an arbitrary two-terminal cell by measurement alone.
- The qualified profile carries exact model, approved source, assembly
  certification/test-summary identity, lot, nominal capacity, expected
  resistance/droop distributions and temperature policy. Missing or stale
  certification/lot evidence blocks a production kit; firmware does not
  manufacture identity from voltage, capacity or a packaging security code.
- `PWR-0005/FND-0075` separate gauging from pre-closure admission, while
  `PWR-0006/FND-0076` retain the controlled-1S cross-charge, common-current and
  SOC consequences as future-variant evidence. `DEC-0066` freezes the hardware
  identities and roles: `MAX17320G20+T` is the local gauge/protector and
  `MSPM0C1104SDGS20R` is the admission owner. Register policy and image format
  remain implementation outputs, not permission to change those roles.
- Hardware owns reverse-insertion prevention, observation before admission and
  the charge/discharge FET boundary. Firmware may request admission but cannot
  force a refused pair on or use balancing to mask an unsafe mismatch.
- `DEC-0067` forbids in-device deep-cell recovery. A cell below the qualified
  admission floor is refused; `3.0 V` relaxed/no-load per cell is a paper
  starting point, not yet a firmware constant. The protected MAX17320 image
  keeps zero-volt charge and linear prequalification disabled, and firmware
  must verify that state before requesting release. There is no S3, admission-
  MCU or product-menu command that can enable either path.
- Normal charge is capped at `2 A`, the exact cell's standard value, and is
  blocked outside `0…45 °C` until an assembly-specific qualification narrows
  or explicitly extends that range. The 4-A manufacturer maximum is not a
  runtime option. Source current, system load, any invalid NTC or HIL policy
  may only reduce the 2-A ceiling.
- The physical `ZVC` contact is unused by hardware. Firmware must not describe
  a register write as an alternative recovery path. Any characterization or
  attempted recovery uses a separately powered isolated Controlled-Zone
  fixture and is outside the handheld runtime protocol.
- Firmware retains distinct `cell_0`, `cell_1`, set/bus, temperature, contact and
  admission states. Missing/inconsistent evidence is `unknown` and blocks
  charge, high-load operation and TX leases rather than inheriting the prior
  battery state.
- `PACK_NTC0` and `PACK_NTC1` are direct mid-can channels for their own cells.
  The BQ25798 TS input is a third physically independent sensor populated at
  the HIL-qualified thermally worst slot. Open, short, lifted, implausibly
  static or mutually inconsistent temperature evidence blocks admission or
  charge; firmware cannot substitute a model or the neighboring sensor. If no
  single charger-TS site bounds both slots, hardware must reopen the topology.
- Single-cell removal, contact bounce, a single-cell replacement and reset are
  fresh admission events. No previous state-of-charge, health or approved-pair
  identity is restored until both cells pass the hardware/firmware contract.
  The base product exposes no one-cell battery-operation mode.
- The admission MCU owns local gauge polling, protected-NVM verification,
  midpoint/full-stack ADC evidence on PA25/A2 and PA26/A1, diagnostic-load sequencing
  and the release decision. S3 consumes a
  read-only state/fault window and may request evaluation but cannot access the
  local gauge bus directly or override a refusal. The admission MCU is a
  fourth independently recoverable firmware image and service domain, not an
  application task silently hosted on S3.
- The admission image runs a bounded low-clock/duty state machine from AOLDO.
  Flash programming/recovery uses isolated fixture or admitted system power;
  firmware must not assume AOLDO can supply erase/program current.
- `PA24/A3` is not an ADC fallback: the exact MSPM0C1104 datasheet permits no
  injection current there, while the battery dividers can remain live during
  admission-supply loss. The corrected PA25/PA26 allocation preserves the
  `12 used / 3 service-reserved / 3 free` budget.
- The accepted diagnostic command is edge-only. Firmware waits at least 1 ms
  after stable admission VDD, holds `PA22/A4` low, writes one rising edge and
  returns it low; it never drives the load MOSFET directly and never treats
  GPIO-high time as the pulse duration. `TPUL2G223BQBR` channel 1 is
  non-retriggerable and produces approximately 34.4 ms typical with a
  conservative 28.7-40.7-ms paper window. Production accepts only a measured
  25-50-ms pulse. The falling channel-1 Q edge then starts channel 2, whose
  complementary output asynchronously clears channel 1 for a production-
  measured 350-860 ms. Repeated writes or a stuck-high GPIO therefore cannot
  extend one pulse or bypass the independent refractory interval.
- The admission ADC uses the internal 1.4-V reference. Before baseline it
  waits at least 10 ms after the last relevant source/contact edge. After the
  diagnostic trigger it waits at least 10 ms for the 10-nF divider filters,
  then captures midpoint and stack inside the remaining hardware pulse. The
  measured 25-ms production floor, rather than an X7R assumption, guarantees
  that window. A
  missing/invalid loaded sample, unexpected post-pulse droop or inconsistent
  gauge evidence blocks admission.
- The exact 10-Ohm load is two parallel 20-Ohm/2-W branches. Firmware neither
  detects nor compensates a missing branch: production continuity/calibration
  rejects the assembly, while any runtime loaded sample outside the signed
  exact-profile envelope fails closed.
- Production droop/contact thresholds and ADC acquisition/calibration come
  only from the exact approved-cell/contact/timer HIL profile. Every normal
  retry waits at least 10 seconds; an exact-cell profile may lengthen but never
  shorten that floor. The hardware 350-ms minimum is a separate fault bound,
  not a normal scheduling interval, and the short 0.57-0.88-A screen is never
  reported as proof of the 2.78-A product-load transient.
- Runtime diagnostics name the exact protected path without controlling it:
  `CSD87313DMST` CHG/DIS state, two slot-fuse/NTC channels, the 5-mOhm shunt,
  reset-default ALRT hold and admission-supply source. Unknown or inconsistent
  evidence keeps the path open; it never falls back to a software estimate.

## Sink-only USB-PD and charge input

- `TPS25751DREFR` autonomously loads its policy from dedicated
  `CAT24C512WI-GT3`; `BQ25798RQMR` is on the TPS-local I2C controller bus.
  S3 is a host/observer through TPS I2Ct, not the component required to make
  an ordinary dead-battery attachment negotiate safely.
- Raw connector power reaches both TPS `VBUS` and `VBUS_IN`. Hardware straps
  `ADCIN1=7`, `ADCIN2=0` select SafeMode and target address `0x20`: before an
  application rail exists, the VBUS LDO powers attach detection and the
  address-`0x50` EEPROM while PPHV, PD and charging remain disabled. The
  startup sequence is therefore raw attach → SafeMode → EEPROM load → accepted
  contract → PPHV/BQ SYS → `AON_SAFE_3V3` → TPS `VIN_3V3` and application
  rails. `VIN_3V3` presence is never itself permission to enable PPHV or CE.
- The TPS validates the programmed configuration format needed to load it; it
  does not independently establish owner-signature authenticity at every
  raw-VBUS boot. Authenticity is established by factory provisioning or the
  signed S3 update transaction before a region becomes active. Firmware must
  not describe a TPS format/CRC success as a fresh signature verification.
- The only accepted contracts are 5-V fallback, 9 V/3 A and 15 V/2 A. Firmware
  never requests or exposes 20 V, PPS, source/power-bank or BQ OTG. Any
  unexpected role/PDO is a latched power-policy fault and charge is disabled.
- Runtime state is explicit: negotiated voltage/current/power, cable/source
  class, input/charge limits, charger mode/faults, both cell states, EEPROM
  image version/hash/active region and whether recovery is required. Unknown
  is never converted into 30-W availability.
- The first charge-current ceiling is 2 A and is further reduced or paused by
  system load, connector/charger/cell temperature, weak-source behavior and
  cell-manager decisions. The 5-A IC capability is not a runtime default.
- The initial paper admission rule treats only `0.85 × negotiated input power`
  as usable. It first reserves `max(declared scenario load, measured SYS load
  + measurement margin)` and derives charge current from the non-negative
  remainder divided by pack voltage, still capped at 2 A. Missing measurements,
  DPM/current limiting, thermal derating or any power fault makes the requested
  charge current zero. This conservative rule is an admission floor pending
  measured efficiency maps, not a claim that conversion efficiency is 85%.
- Hardware fixes BQ25798 to 2S/750 kHz with an exact 2.2-uH/7-A inductor.
  POR or charger-watchdog reset restores 1-A charge, 7.0-V VSYSMIN and 8.4-V
  VREG; firmware has no frequency/cell-count profile selector.
- Before TPS GPIO1 may sink the reset-high CE line, the controller must
  validate the source contract, write and read back IINDPM at or below the
  advertised current and the 2.71-3.29-A physical ILIM envelope, confirm both
  cells and direct BQ TS are valid, then calculate a load-aware charge current
  no greater than 2 A. Unknown power or temperature releases CE.
- BQ TS uses a third electrically independent B57332V5103F360 and remains
  enabled. Firmware may narrow the qualified charge window, but must never set
  `TS_IGNORE`; the two MAX17320 cell sensors remain separate evidence.
- Product USB2 remains native on S3 GPIO19/20 through the automatic four-line
  port protector and exact initial 22-Ohm series resistors; its exact PHY limit
  is Full-Speed 12 Mbit/s. Two hardware shunt-capacitor positions remain DNP
  pending measured tuning. There is no firmware profile that enables TPS
  BC1.2/liquid pins, BQ DPDM or physical Type-C SBU/Alt Mode on the data pair.
- Connector overvoltage opens affected CC/data paths in hardware. Runtime
  treats detach, PD fault or failed USB re-enumeration as a closed USB session,
  clears any USB-derived Controlled-Zone authorization and reports the fault;
  it does not bypass protection or enter a tight reset/re-enumeration loop.
- Direct protector `FLT` is intentionally fixture-only because the paper map
  preserves GPIO47. Production runtime therefore uses TPS status, native USB
  link state and re-enumeration outcome; it never fabricates the missing direct
  FLT observation. Full-Speed RC/signal-integrity and enumeration remain HIL;
  a failed gate reopens hardware values, placement or protection rather than
  changing the advertised PHY class or removing protection.
- A PD image update is permitted only while TX is disarmed, input and cells are
  stable, the signed manifest targets the exact board/controller/tool version,
  and the inactive EEPROM region is writable. Readback/hash/boot validation
  occurs before retiring the previous region; interruption preserves rollback.
- EEPROM WP is reset-high through an exact pull-up. TPS GPIO0 is an open-drain
  sink only: firmware/configuration may release it or pull it low inside the
  authorized signed-write window, never drive it high or leave WP writable
  across reset/fault. TPS GPIO1 remains the separate open-drain CE sink.
- The autonomous local SCL/SDA pair has exact 2.2-kOhm LDO_3V3 pull-ups; the
  S3 host SCL/SDA pair has exact 2.2-kOhm 3V3_MAIN pull-ups and SYS_INT_N has
  one 10-kOhm pull-up. Bus speed remains bounded by measured aggregate
  capacitance/rise time; firmware may not infer 1 MHz solely from the EEPROM
  rating or start host transactions before 3V3_MAIN is valid.
- Factory/recovery pads remain the authority for a blank or corrupt EEPROM.
  The ordinary FLxx region-update flow assumes an initialized image and cannot
  be presented as blank-device provisioning. First image is programmed before
  placement or by a current-limited raw-VBUS fixture that observes
  `ReadyForPatch`, verifies I2Cc high-Z, then uses direct SDA/SCL/WP pads. It
  never injects 3.3 V into the TPS LDO output. Firmware presents those recovery
  instructions but cannot claim that an application-only update path is
  independent recovery.
- HIL covers every supported/fallback cable and source, blank/corrupt image,
  interrupted update, shared-IRQ concurrency, no-battery/deep-cell refusal,
  supplement/removal/bounce, thermal derating and proof that 20 V/source/OTG
  never reaches the connector.

## Fixed downstream rail runtime input

- `BQ25798RQMR.SYS` feeds four electrically independent, hardware-fixed
  converters. `TPS629203DRLR` creates `AON_RAW_3V3`, and separate
  `TPS564252DRLR` devices create `MAIN_RAW_3V3`, `VVOICE_RAW_4V` and the
  pre-protection 5-V accessory rail. An exact independent cutoff admits each
  internal raw rail to `AON_SAFE_3V3`, `3V3_MAIN` or protected `VVOICE_4V`.
  Firmware has no voltage selector, feedback-network mode or command that can
  bridge a cutoff or turn the 4-V voice output into 5 V.
- The fixed hardware profile is exact rather than runtime-configurable:
  TPS629203 selects 3.3 V with open `FB/VSET` and a 42.2-kOhm MODE/S-CONF
  strap; the three TPS564252 dividers produce nominal 3.318/4.000/5.000 V.
  Their paper limits are acceptance inputs, not ADC calibration values or
  software-adjustable set points. Firmware exposes the rail identity and
  measured qualification result, never a voltage-setting API.
- AON power is autonomous. `TPS629203.EN` is strapped directly to admitted
  `SYS`; `TPS25961DRVR` independently admits the resulting raw rail. The
  converter PG pull-up and `TPS3808G33` SENSE/POR supply exist only on
  protected `AON_SAFE_3V3`. PG drives `MR_N`; only valid raw-converter PG plus
  protected SENSE above 3.07 V for the exact CT delay releases
  open-drain `POR_N`, whose 10-kOhm pull-up and 100-kOhm main-EN fail-low pull
  produce about 3.0 V and enable the main converter. There is no programmable
  source sequencer. Application firmware observes the result but cannot start
  AON, bypass its eFuse/POR or keep the main rail alive after protected AON
  PG/SENSE loss.
- The amended converter-control profile has ten physical resistor positions:
  the AON PG pull-up, POR pull-up, three application EN fail-low pulls, both
  optional PG pulls, both qualifier-base resistors and the common fault pull.
  Their values do not create a firmware setting, timing constant or retry
  path: runtime consumes the safe defaults and `EN AND NOT(PG)` truth table,
  then uses measured HIL deadlines.
- Main and voice each cross a physically separate `TPS25974LRPWR` latch-off
  boundary with fixed OVLO, circuit-breaker, dVdt, ITIMER and PGTH parts.
  Firmware consumes only protected-side PG as operational load-good evidence.
  Raw main/voice converter PG is fixture-only and must never grant a rail,
  lease, signal group or retry.
- `3V3_MAIN` is admitted by hardware after a valid battery or USB source and
  supplies the three compute domains. Protected `MAIN_3V3_PG_N` loss joins
  `POWER_FAULT_N`; firmware immediately revokes every lease and returns the
  logical signal group to `NONE`, but protection and reset do not wait for
  that reaction.
- Five independent `TPS22919DCKR` branches gate the complete nRF group,
  CC1101, microSD, ES8311 and Si4732. Every ON input has an external reset-off
  default. QOD discharges the disabled output; firmware may call a branch
  quiet only after its controller and pins are parked, the rail has completed
  the measured discharge interval and back-power/current evidence passes.
- The nRF branch is deliberately common to all three radios. Entering
  `SG-N24` powers all three plus their host/return Ioff buffers, waits at least
  100 ms, validates all three identities and only then enables independent buses;
  it never cycles a peer rail to implement `3R`, `1T+2R`, `2T+1R` or `3T`.
  Leaving the group parks all three interfaces and waits for three inactive
  forward-power bits before the common branch opens. Strong inbound RF may
  conservatively delay shutdown as a false positive; it never permits a false
  negative or automatic bypass.
- Voice sequencing asserts the STOP-dominant `VOICE_DOMAIN_EN_SAFE`, waits for
  qualified `POWER_FAULT_N` collector to release, keeps PTT forced RX and
  `AUDIO_ARM=0`, then qualifies the SA518/codec path before allowing
  selection. Hardware uses protected `VOICE_4V_PG_N` locally to hold the
  voice domain reset/PD. During the bounded start interval the qualified
  collector is expected low because `EN=1, PG=0`; it becomes a fault only if
  it does not release by the measured deadline. Disable occurs in the
  opposite order, and `EN=0` makes protected PG low a normal off state. A 4-V PG
  timeout or fault cannot fall back to the accessory rail.
- A main/voice protection trip is a latched hardware fault. Runtime first
  revokes every affected lease, forces the logical signal group to `NONE`,
  records protected PG/fault evidence and parks signal pins. Voice recovery is
  a new validated power session through its existing STOP-dominant enable; a
  latched main trip requires complete source removal and fresh hardware
  admission. AON overcurrent/thermal recovery attempts are owned and bounded
  by TPS25961 hardware; firmware cannot accelerate them, and main remains off
  until protected PG/SENSE/CT are continuously valid. Firmware has no direct
  eFuse reset/bypass API and never loops rail power against a persistent fault.
- Accessory sequencing asserts one branch request. The request OR enables the
  shared STOP-dominant 5-V converter, while the branch AND enables only that
  branch's `TPS259470LRPWR`. Runtime waits for the enable-qualified converter
  PG collector and exact branch supervisor READY, then enables only the
  corresponding U214 or native-Unit signal isolation and performs identity.
  `EN=1, PG=0` is a bounded pending state; failure to release is latched, while
  `EN=0, PG=0` is normal quiet state and must not create a fault. The nominal
  1.509-A eFuse limit is active immediately during startup: runtime must never
  claim that `ITIMER` defers it. The 4.7-nF `dVdt` profile admits at most 1 mF
  effective accessory input capacitance pending HIL. The port is 1.25 A
  continuous; 2.0 A is one bounded post-start excursion, approximately
  86.6…404 ms on the paper limits, not a startup or continuous budget. The
  Each eFuse always blocks reverse current. Its active-low `FLT` also joins
  `POWER_FAULT_N`; `ILM` is a protected factory/HIL test point, not an
  invented runtime ADC channel.
- OVLO recovery on the selected eFuse bypasses the normal `dVdt` ramp and
  restarts current-limited. Runtime treats that event as a new accessory
  admission: signal paths remain isolated until rail/evidence qualification
  completes, even if the request and enable never changed.
- On disable or fault, accessory signals isolate first, converter/eFuse enable
  clears, and the connector is allowed to reach its measured passive-discharge
  threshold before the UI reports it safe to remove. External 5-V injection,
  qualified-PG/FLT disagreement, expired post-start transient, timeout or
  unknown evidence remains a latched accessory fault and cannot be cleared by
  re-enabling in a loop. The exact `L` suffix
  also latches thermal/latched faults in hardware until EN is explicitly taken
  below shutdown or input power is cycled; the former 110-ms auto-retry suffix
  is not a target behavior.
- microSD follows the full `DEC-0085` clean/unexpected-removal state machine;
  SPI pins are parked before `SD_PWR_EN` clears, then firmware waits the
  HIL-qualified QOD interval because no card-rail ADC exists. A failed
  unmount/settle gate blocks the next session. ES8311 follows the stricter
  audio-arm sequence below. Si4732 and
  CC1101 similarly park reset/bus pins before their independent branches open.
  A failed settle, readback or discharge gate leaves the whole requested group
  unavailable rather than silently weakening the quiet-state contract.

## Exact IR runtime contract

- C5 owns all timing locally. GPIO0/RMT RX0 is the active-low 38-kHz
  demodulated envelope from `TSOP95238TT`; GPIO1/RMT RX1 is the active-low
  30–60-kHz carrier-cycle stream from `TSMP95000TT`. Only a validated GPIO1
  measurement can set carrier provenance to `measured`; GPIO0 never can.
- Entering IR receive/learn first parks GPIO6/RMT TX0 low, confirms optical
  evidence is dark, enables GPIO4 `IR_FRONTEND_PWR_EN`, waits the HIL-qualified
  rail rise and clears both capture channels before starting them together.
  A failed rise, stuck-low return or invalid carrier range makes the requested
  mode unavailable; it never falls back to inferred timing.
- A learned profile stores demodulated mark/space timing separately from
  carrier frequency, source provenance, tolerance and specimen/test identity.
  Reproduction is rejected when carrier provenance, frequency range or the
  profile's safety envelope is missing.
- Every IR TX lease binds target/profile identity, carrier, mark/space payload,
  repeat count, maximum mark, duty/repetition class, temperature class and
  expiry. Admission requires the receive rail off and discharged, both return
  paths isolated, GPIO6 low and a qualified dark evidence state. GPIO6 reaches
  the `VSMY14940` only through AON STOP-dominated gating and the fixed
  `RC1206FR-0733RL`/`DMN2056U-7` current-limited driver.
- GPIO24 is active-low physical optical evidence from the shielded
  `VEMD1060X01` and `TLV9061IDBVR`, not a mirror of GPIO6 or LED current.
  Evidence must assert and decay inside versioned HIL windows. Missing evidence
  revokes the lease, stops and parks RMT TX, waits for dark and records a fault.
  Ambient or coupled light may report `external_light_present` and delay quiet;
  evidence never creates or extends permission.
- IR shutdown stops RMT, forces GPIO6 low, waits for evidence high/dark, parks
  both capture inputs and keeps GPIO4 low until the switched rail has met its
  qualified QOD interval. `IR_QUIET` therefore means discharged RX power,
  high-impedance returns, GPIO0/GPIO1 idle-high, GPIO6 low and GPIO24 high.
  Any disagreement remains a fail-closed fault and blocks the next session.

## Hard STOP and actual-TX input

- The AON hardware latch, not firmware, owns the dominant stop path. STOP or an
  open normally-closed loop asynchronously blocks every reviewed TX/rail
  request and holds `S3.EN`, `C5.EN` and `RP.RUN` low. Firmware therefore cannot
  observe a live STOP session from those targets; it reconstructs the cause
  best-effort after a new physical RE-ARM and fresh TX-off boot.
- Releasing STOP does nothing. Only a new edge from the normally-open RE-ARM
  control permits the three processors to boot, and no target/profile/power/
  payload/lease state is restored.
- RP GPIO22 is direct active-low `RP_ANY_TX_N`. It is independent of software,
  I2C and the source-mask expander. Low means at least one qualified evidence
  channel asserts; high alone does not convert missing or faulty evidence into
  proof of no transmission.
- RP local I2C0 also reads TCA9534A address `0x38`: P0..P7 map exactly to
  `S3_RF`, `C5_RF`, `NRF0_RF`, `NRF1_RF`, `NRF2_RF`, `CC_RF`, `VOICE_RF` and
  `IR_OPTICAL`. Its interrupt is a test point, not a new RP GPIO dependency.
- NRF0/1/2 evidence specifically comes from separate
  `DC2337J5010AHF`→`AD8314ACPZ-RL7` forward samples, not command state or PA
  current. Qualification is versioned at channels 0, 100 and 125. A profile
  without valid threshold/temperature/lot calibration is
  `unknown/unavailable` and cannot satisfy a proof-mandatory TX lease.
- CC evidence comes from the high-impedance final-line
  `GJM1555C1HR47BB01D` sample into `AD8314ACPZ-RL7`, after both band switches
  and all populated matching. It is intentionally non-directional: assertion
  without a matching commanded-TX generation is `unexpected_rf`, never
  authorization. Absence during commanded TX is `evidence_missing`; either
  state blocks or expires the lease and enters the fail-closed quiet sequence.
- Voice evidence comes from the final SA518 external line through exact
  `RC0402FR-075K1L` + `RC0402FR-0752R3L` into a separate
  `AD8314ACPZ-RL7`. The nominal approximately-40-dB calculation is not a
  threshold: only versioned VHF/UHF and H/L-power HIL calibration enables a
  proof-mandatory profile. Assertion without the matching lease generation is
  `external_rf_present`/unexpected, never authorization.
- IR evidence comes from a light-tight optical path viewing the physical
  `VSMY14940` through `VEMD1060X01` and an AON TIA. It is interpreted only
  against the current IR lease generation and qualified assert/decay windows;
  missing light revokes TX, while unexpected light is never authorization.
- Firmware reports `commanded`, `device-reported`, `actual` and
  `unknown/unavailable` independently. All eight evidence lines low are
  sufficient positive observations; an impossible aggregate/mask combination,
  I2C failure or an unqualified accessory is a fault/unknown state and expires
  any proof-dependent lease.

## Firmware HIL that follows from this map

1. every simultaneous three-nRF `3R/1T2R/2T1R/3T` role mix with independent
   channel/rate/address/session, per-source latency, overflow, loss/gap and
   exact RF-profile evidence; before that matrix, prove 10-Mbit/s isolated
   SPI, 100-ms POR, three identity reads, QOD/no-backpower and forward-power
   thresholds at channels 0/100/125 over voltage, temperature and module lots;
2. RP IPC stress at accepted radio load while display, storage, audio and C5
   traffic run;
3. C5 1-bit IPC framed throughput/occupancy/control-priority/RTT, reset/link-loss
   visibility and TX lease expiry under Wi-Fi/802.15.4/IR load;
4. display+SD scheduling, hot removal and injected 250 ms card stalls;
5. both independent M5 branches through OFF/READY/IDENTIFY/ACTIVE/QUIETING and
   FAULT_LATCHED; U214 I²C stuck-low plus all SPI/UART/control no-back-power,
   native I²C/UART/GPIO and qualified 1-Wire, reverse-source/external-power,
   unknown/mismatch/hot-plug, combined-load and independent internal-bus proof;
6. independent programming/recovery/diagnostics for all three domains;
7. PIO instruction placement, DMA arbitration and SRAM-bank contention under
   the same simultaneous event load; static channel counts alone are not the
   timing proof;
8. every non-member quiet-state transition, no-back-power/fault injection and
   active-receiver desense under maximum valid system-plane traffic.
9. ES8311 address/readback, BCLK-derived simultaneous ADC+DAC, power-off
   no-backfeed and hardware-default analog bypass under reset/watchdog/fault,
   including stale P11/P12 after S3-only reset and proof that arm-low overrides
   both selector requests under accepted `DEC-0054`.
10. CC315/433/868/915 cold band entry, identity/config readback, prohibited hot
    switch, cross-domain generation mismatch/reset, evidence assert/decay and
    strong-inbound false-positive handling; then VNA/conducted output,
    sensitivity, spurious, feed-loss/EIRP and no-neighbour-stall coexistence.
11. simultaneous TSOP95238TT envelope plus TSMP95000TT carrier capture,
    carrier/mark-space accuracy across 30–60 kHz, RX rail discharge/no-backfeed,
    VSMY14940 current/range/duty/temperature and IEC 62471, optical-tunnel
    threshold/assert/decay plus missing-emitter/ambient faults, STOP/reset/
    brownout/stuck-carrier injection and no-neighbour-stall coexistence.

The fixture has two explicitly different evidence levels. Ordered ESP32-DIV
units form `L0 DIV↔DIV` pre-HIL: they validate the manifest/log workflow and
reproduce loss/self-desense, but cannot close Leshy2 RF, rail, antenna or
thermal acceptance. `T1 TARGET` uses two comparable Leshy2 revisions, or a
Leshy2 DUT plus a calibrated conducted/OTA peer, and is the only production
acceptance level.

Both levels use one shared test ID and explicit DUT/observer roles. They
exchange manifests and ordinary packet streams, never remote raw CE/GPIO.
Every device retains its own per-radio logs; results join by test ID, hardware
identity, packet sequence and timestamps with recorded synchronization error.
Role reversal on `L0` measures DIV asymmetry only; role reversal/reproducibility
on `T1` closes target evidence. The observer is HIL equipment, not a runtime
dependency of the base product.

`DEC-0048` makes antenna identity part of every manifest. All onboard paths
terminate at labelled external SMA; nRF0/1/2 map permanently to three distinct
SMA positions through compact IPEX modules and short feeds. Firmware must not
infer a correct antenna merely from connector presence: TX arming records the
selected band/path/antenna profile, permitted power and qualified feed loss.
External M5 accessories report their own antenna identity separately.

`DEC-0055` defines a 12-item field kit for nine simultaneous ports: one shared
exact MPN in quantity two for S3/C5, one in quantity three for nRF0/1/2,
separate CC 315/433/combined-868+915, separate VOICE VHF/UHF, FM/SW whip and
AM/LW loop/pod profiles. Every CC/VOICE profile change disarms TX. Unknown,
mismatched, expired or unqualified identities remain TX-disabled. Availability
is an exact-MPN-selection gate, not a continuously polled architecture input.

Hardware `RFH-0001/FND-0057` distinguishes the verified first-generation
U.FL/MHF I/AMC-compatible S3/C5 connectors from Ebyte's undocumented generic
`IPX` name. Firmware/test manifests must record exact module lot, harness MPN,
length and measured feed identity; they must not merge S3/C5/nRF feeds under
one generic pigtail SKU before the Ebyte specimen-fit/VNA gate. External
standard-versus-RP SMA choice changes assembly metadata, not the nine logical
path identities. Hardware `DEC-0050/REV-0004T` fixes RP-SMA jack/pin only for
`S3-2G4` and `C5-2G4/5`; the other seven use standard SMA jack/socket. The
detachable mates are respectively RP-SMA plug/socket and standard SMA
plug/pin. Exact qualified antenna MPN remains an upstream hardware gate.

## Exact Si4732 dual-input RF runtime contract

Hardware `DEC-0096/RXF-0001/FND-0102` completes the earlier antenna-domain
requirement with real base-side circuits and the corrected full SOIC-16 map.
Exact `Si4732-A10-GSR` physical contact 6 `FMI` owns FM/SW through
`LQW15AN56NJ00D` 56-nH matching,
`GRM1555C1H102JA01D` 1-nF C0G coupling and its own
`SESD0402X1UN-0020-090`. Physical contact 8 `AMI` owns AM/LW through
`GRM155R71A474KE01D` 0.47-uF coupling and a second separately placed SESD
body. Contact 7 is the short local RF return. No RF switch or TX path exists.
The 56-nH/1-nF circuit is an AN383 FM starting point: the exact data short
assigns SW to FMI, but firmware must not treat that FM network as proof of SW
sensitivity. AN383's separate SW-on-AMI example is Si4734/35-only and is not a
valid reason to remap Si4732 modes.

Firmware exposes four mode identities over two immutable physical ports:

| Mode identity | Physical port identity | Published tuning range | Required accessory profile |
|---|---|---|---|
| `rx_fm` | `rx_fmsw_fmi` | 64–108 MHz | qualified FM/SW whip/feed profile |
| `rx_sw` | `rx_fmsw_fmi` | 2.3–26.1 MHz | qualified SW-capable whip/feed profile; the current 25-MHz antenna-list edge does not qualify 2.3–25 MHz |
| `rx_am` | `rx_amlw_ami` | 520–1710 kHz | short direct ferrite-loop pod or qualified external loop/transformer pod |
| `rx_lw` | `rx_amlw_ami` | 153–279 kHz | short direct ferrite-loop pod or qualified external loop/transformer pod |

Only one of the four modes is active at a time. `rx_fmsw_fmi` and
`rx_amlw_ami` are never collapsed to generic `RX`. The AM/LW connector is
mechanically standard SMA but electrically `non_50_ohm_loop_pod`; arbitrary
long coax is rejected from a qualified manifest because its capacitance changes
the tuned input. Physical connector presence is not detectable, so firmware
must not infer the installed antenna or pod from successful I²C tuning.

The persistent profile record contains mode, physical port, antenna/pod MPN or
prototype identity, feed/cable identity, qualified band interval, qualification
lot, enclosure revision and HIL evidence revision. Unknown, expired or
out-of-range profiles remain usable only as explicitly unqualified receive
experiments in Laboratory UI; recording/scan metadata stays `unqualified` and
must not be promoted to target sensitivity or compatibility evidence. Because
the complete block is receive-only, profile failure never enters TX-arm logic.

Admission and shutdown are ordered:

1. acquire `SG-BROADCAST`, make every foreign signal group quiet and stop any
   old receiver scan/audio capture;
2. bind one mode to its immutable port/profile, then enable `RX_DOMAIN_EN`;
3. wait for receiver supervisor release, probe both specimen identities
   `0x11`/`0x63`, load only owner-authorized firmware components and configure
   the selected band before tune/scan/audio;
4. preserve mode, physical port and profile qualification on every result and
   recording; RDS or optional owner-supplied SSB metadata never changes the
   physical port identity;
5. on close/fault, stop tune/scan/audio and I²C traffic, mute the audio path,
   assert reset/isolation, remove receiver power, verify the qualified discharge
   interval and release `SG-BROADCAST` only after the digital branch is quiet.

The passive ESD/matching/coupling network has no runtime telemetry. Firmware
therefore cannot claim ESD integrity, antenna presence, loop inductance,
sensitivity or absence of desense. A band/profile becomes product-qualified
only after exact specimen HIL covers both ports, all four ranges, overload/noise,
pod parasitics, power cycling and every valid neighboring signal group under
maximum scheduled digital traffic. Any failed coexistence result invalidates
the affected profile evidence rather than silently lowering a product claim.

Hardware `FND-0056` also removes a false SA518 assumption: rev 1.1 has no
dedicated `SQ` contact. The runtime input is therefore neutral
`VOICE_ACTIVITY`; firmware may assign carrier/squelch meaning only after exact
pin-18 `AUDIO_ON` HIL. `PIN-0003` now terminates UART, PTT, activity and the
service breakout on exact SA518 contacts, including pin 17 `UPDATE`; driving
that contact remains forbidden until its documented direction/pull-down
ambiguity passes specimen proof. The same atlas terminates the Si4732 I²C,
reset, interrupt, clock, audio and separate `FMI`/`AMI` routes on exact package
contacts.

## Exact I5 audio and receiver runtime boundary

Hardware `AUDIO-0001/REV-0005B` instantiate exact Everest Semiconductor
`ES8311` QFN-20 digital contacts. The later direct arm made total S3 `32/3/1`
before the subsequent encoder allocation; current total is `33/3/0`:

- `GPIO1/SYS_I2C_SDA` ↔ codec `CDATA` pin 19;
- `GPIO2/SYS_I2C_SCL` → codec `CCLK` pin 1;
- `GPIO15/I2S_BCLK` → codec `SCLK` pin 6;
- `GPIO16/I2S_WS` → codec `LRCK` pin 8;
- `GPIO17/I2S_DOUT` → codec `DSDIN` pin 9;
- `GPIO18/I2S_DIN` ← codec `ASDOUT` pin 7;
- codec `MCLK` pin 2 is unconnected under the reviewed BCLK-derived-clock
  contract;
- codec `CE` pin 20 is fixed high through the documented `10 kΩ` reference
  strap for 7-bit address `0x19`.

`CE` is **not** enable or reset. Slow P10 is external `CODEC_PWR_EN` driving
the exact reset-off/QOD `TPS22919DCKR` codec branch. `TPS3839K33DBZR` keeps
dual-channel I2C isolation and four separate I2S direction buffers disabled
until the switched rail exceeds 3.08 V for about 200 ms. Firmware must never
toggle CE or drive through those physical gates, and it must not infer
readiness merely from elapsed software time.

Exact ADC `MIC1P/MIC1N` and DAC `OUTP/OUTN` are differential. Hardware
`AUDIO-0002/REV-0005C` reviews the complete path rather than treating the
codec as an isolated endpoint:

- ordinary Si4732/SA518 AFOUT analog bypass to PAM8302A remains available with
  the codec off or faulty;
- P00 chooses either the selected RX source or exact local electret microphone;
  the result reaches the ADC only through the high-impedance buffered capture
  branch, because a direct ES8311 tap can load the Si4732 bypass;
- both DAC legs reach both PAM8302A inputs through a dual selector; no central
  differential-to-single-ended amplifier is required;
- DAC-to-SA518 injection has its own selector and roughly 35–45 dB attenuation,
  while electret-to-SA518 remains the default and audio selection never asserts
  PTT;
- P27 selects the ordinary receive source. P01 is reset-off speaker enable and
  P02 reports headphone absence; insertion forces speaker shutdown. P11/P12
  request codec speaker/TX routing but can remain stale when only S3 resets.

`DEC-0054` accepted ES8311, `TLV9061IDBVR` active high-Z capture,
`TMUX1136DGSR` speaker selection, `TS5A63157DCKR` TX selection and
`SN74LVC2G08DCUR` gating of both P11/P12 requests by direct pulled-low GPIO6
`AUDIO_ARM`. I5 adds a second exact `TS5A63157DCKR` for P00 capture selection,
complete bias/coupling/attenuation, reset-off `PAM8302AASCR`, exact
`CMEJ-0413-42-SMT-TR` microphone, `AS02404PO` speaker and protected switched
`SJ1-3515-SMT-TR` headphone jack. Arm-low forces both codec selectors to
analog defaults independently of stale expander state.

The exact runtime modes are:

| Mode | Required controls | Result and invariant |
|---|---|---|
| receiver bypass | P27 chooses Si4732 or SA518; `AUDIO_ARM=0`; codec may be off | selected AFOUT reaches the speaker selector's bypass input; no codec dependency |
| receiver recording | chosen RX plus `P00=0`; admitted codec/I2S | selected receive audio reaches ES8311 capture without loading bypass |
| microphone recording / authorized host VOX | `P00=1`; admitted codec/I2S | local microphone is captured; VOX analysis never implies or requests PTT |
| codec playback | admitted codec/I2S; P11 request; direct `AUDIO_ARM=1`; P01 only if P02 says absent | codec reaches speaker; headphone insertion disables speaker |
| ordinary voice TX audio | TX selector default, `AUDIO_ARM=0` | electret feeds SA518; audio selection itself never asserts PTT |
| codec-injected voice TX audio | admitted codec/I2S; P12 request; direct `AUDIO_ARM=1` | attenuated codec output feeds SA518; separately armed AON-gated PTT is still required |

Si4732 has its own reset-off/QOD `TPS22919DCKR` branch. Its 3.08-V/200-ms
supervisor holds RST, dual I2C isolation and open-drain IRQ isolation until
valid power. Firmware first probes `0x11` and `0x63`; a successful address is
recorded as specimen evidence, not generalized to every BOM lot before HIL.

SA518 interface readiness is separate from rail enable. The AON supervisor
requires STOP permission, protected 4 V above about 3.73 V and about 57.6 ms
post-threshold delay before PD, local I/O power, PTT/UART and analog isolation
can open. Module PTT has a physical RX pull-up; H/L is driven low or released
through an open-drain stage, never driven high. RP-to-module UART RX is
physically disconnected and low while asleep. UPDATE is fixture-only and
standard VOXEN is not a runtime feature.

Normative firmware sequencing is disarm-first:

1. On boot/reset, never drive GPIO6 high; the external pull-down establishes
   speaker-bypass/electret defaults before firmware runs.
2. Keep `AUDIO_ARM=0` while setting P00/P27, enabling P10, waiting for physical
   codec readiness, reading ES8311 at `0x19`, starting/verifying I2S clocks,
   and writing/verifying P11/P12 requests.
3. Assert `AUDIO_ARM=1` last, only when the requested codec path is valid.
4. Before changing either request, codec power or clock state, clear
   `AUDIO_ARM`, verify analog defaults, update the request, then re-arm only if
   the complete path is healthy.
5. On any readback, DMA, I2C, watchdog, brownout, headphone insertion or
   shutdown fault, clear arm and P01 first; stop/mute/power-down follow. No
   audio selection or host-side VOX result may assert PTT.
6. Before disabling codec or receiver power, stop its DMA/transactions, clear
   requests, wait for physical interface isolation, then allow QOD discharge.
   Do not leave a host output driving a collapsing local domain.

Firmware may now freeze these control states and ordering, but must not freeze
unmeasured gain/mute delays, crystal trim, codec register values or claim
lossless/noiseless TX, recording or speaker routing before HIL closure.

## Explicitly open

Hardware `FND-0060/0066/0067/0079/0080/0081/0082/0083/0085/0086/0088/0089/0090/0092/0098/0100` list remaining electrical/HIL endpoints:
display standalone sourcing/final mate and display/touch/backlight HIL,
microSD socket access, real media/endurance, throughput/contention, hot removal,
fault injection and corruption recovery, audio gain/noise/pop/click/acoustic/
RF-immunity and concurrent-load HIL, IR optical/thermal/IEC 62471 and
coexistence HIL, TPS25751
raw-VBUS/SafeMode/CC-capacitance and bus-rise-time
HIL, exact-cell diagnostic thresholds and timer/load hot HIL,
source-transition, brownout, thermal/source-handover/fault HIL, Unit
protection and service-connector
mechanics. The active downstream converters, their 24 energy/configuration/
feedback parts, ten control resistors, direct AON EN strap, exact AON-PG/POR/main sequence, exact control switches/protection and
independent AON/main/voice post-buck cutoffs with protected PG, plus
external eFuse plus its eight profile passives, and the corrected dual-channel
pack diagnostic timer/load/divider/filter instances, plus the exact BQ25798 inductor, 19
capacitor instances, ten resistors and third NTC, plus the 17 exact TPS/EEPROM
support components and hardware SafeMode straps, plus exact polarized 1048P
holder contacts, two exact XTAR cell instances and the three-NTC physical roles,
are now reviewed paper inputs under `DEC-0082/PWR-0021`,
but firmware must not infer unmeasured delays, thresholds or safe states for
their still-open HIL boundaries.

The hard STOP latch, reset fanout, gate topology and digital evidence delivery
are paper-reviewed inputs from `DEC-0061`. `DEC-0091` additionally reviews the
three exact nRF directional taps, detector bodies and powered-off isolation at
paper level. `DEC-0092` does the same for independent S3/C5 native feeds, and
`DEC-0093` reviews the exact dual-ended CC three-band path and final-line
detector. `DEC-0094` reviews the direct protected SA518 feed plus exact
resistive AD8314 sample. `DEC-0095` reviews the exact dual-receiver IR path,
isolated RX rail, current-limited emitter and physical optical evidence.
`DEC-0096` then closes the separate protected Si4732 FMI FM/SW and non-50-Ohm
AMI AM/LW paper circuits. Pigtail/chassis mates, antenna/pod lots, thresholds,
CC/voice/Si4732 VNA/conducted results, IR optical/thermal proof and
fault-injection/T1 HIL remain open. `FND-0103/FND-0104/COX-0001/DEC-0097/
REV-0005BC` now close the consolidated paper integration gate without claiming
those measurements: cross-group injection cannot create runtime permission,
quiet boundaries are independent and one trace/fixture matrix carries every
group, transition, actual-TX channel and no-stall threshold. I6 paper scope is
reviewed; physical HIL can reopen its owning subblock and I7 is active upstream.

Hardware `DEC-0052/REV-0004X` close `FND-0061`: direct S3 QSPI GPIO41/42 and
the time-based arbitration contract are now runtime inputs. Hardware
`DEC-0053/REV-0004Z` additionally accept a 3.5-inch portrait `320×480` IPS
QSPI+touch class, with `ST77922` primary HIL and `AXS15231B` secondary HIL.
Hardware `FND-0063/DSP-0005/REV-0005A` additionally instantiate exact current
assembly candidate `HMX035CTFT-001`: GPIO41/42 are QSPI D2/D3 and slow P06/P07
are display/touch reset. `DEC-0086` later moves TP_INT through an open-drain
adapter into shared GPIO37 and assigns GPIO39/GPIO47 to PCNT0 encoder capture;
`DEC-0088` then fixes exact integrated ST77922/address `0x38`, active-low
polarity, 10-kOhm raw pull-up and non-inverting `SN74LVC1G07DCKR`. GPIO6
remains `AUDIO_ARM`.
Hardware `FND-0094/IOX-0001/DEC-0089/REV-0005AT` then closes the consolidated
I4 electrical input: exact TCA6424A `0x22`, pack target `0x2A`, shared IRQ and
recovery behavior, isolated P22/P23 observation polarity and the real GPIO4
microSD return are now consumable. Hardware
`FND-0095/AUDIO-0003/DEC-0090/REV-0005AU` then closes I5 and makes the exact
runtime contract above consumable. I6 paper scope is reviewed upstream; no
prototype or physical qualification is inferred.
`FND-0096/N24E-0001/DEC-0091/REV-0005AV` then reviews the first I6 nRF
electrical subblock and makes its sequence/evidence contract consumable here.
The I6 endpoint remains subject to physical HIL; no HAL, KiCad or target
implementation is authorized.
`FND-0097/NAT-0001/DEC-0092/REV-0005AW` and
`FND-0098/CCRF-0001/DEC-0093/REV-0005AX` next make the separate native feeds
and exact CC three-band state machine consumable.
`FND-0099/VRF-0001/DEC-0094/REV-0005AY` then makes the exact voice RF lease,
evidence and shutdown state machine consumable. `FND-0100/IRF-0001/DEC-0095/
REV-0005AZ` next makes the exact IR receive/learn/TX, provenance, optical
evidence and shutdown state machine consumable. Every separate I6 endpoint is
now reviewed at paper level. `FND-0103/FND-0104/COX-0001/DEC-0097/REV-0005BC`
close the consolidated paper qualification matrix and advance upstream work to
I7; no physical qualification is inferred.
Hardware `FND-0105/EXP-0001/DEC-0098/REV-0005BD` then closes the M5 expansion
paper subblock consumed above: separate U214/native-Unit power and readiness,
exact signal isolation, removal of fictitious presence and explicit connector/
hot-plug/profile HIL. I7 continues upstream with service endpoints.
Hardware `FND-0088/DSP-0006/DEC-0084/REV-0005AO` then instantiate the first
exact 40-contact ZIF candidate, separate reset-low pulls and the protected
backlight circuit. Firmware may freeze the reset/off/recovery ordering and
implement reusable scheduler plus distinct prototype driver profiles, but
cannot freeze a production-qualified assembly, final connector or vendor init
table before sourcing and specimen proof gates. Touch identity/address/
polarity are exact paper inputs; readback, IRQ timing/clear and reset recovery
remain HIL.
Hardware `FND-0089/STO-0001/DEC-0085/REV-0005AP` then instantiate exact
microSD switched power, card-side Ioff buffers, CS-gated DAT0/MISO, mandatory
pulls, source damping, full socket-contact/detect ESD and always-readable
detect. Firmware may freeze the session sequencing and error semantics above,
but cannot freeze a production media set, final clock/RC values, endurance or
corruption guarantees before physical and HIL evidence.
Hardware `FND-0090/UI-0001/DEC-0086/REV-0005AQ` then restore the complete
local-control inventory and its pin fit. `FND-0092/UI-0002/DEC-0087/REV-0005AR`
instantiate the exact low-current switches, fail-open COM+NC STOP loop,
matrix/encoder-PTT/safety ESD separation and pull/filter networks. Firmware may
freeze the physical-source identities, active levels and asynchronous STOP
dominance in `ARC-0003`; it cannot claim final debounce, ergonomics or ESD and
fault tolerance before physical/HIL evidence.

Independent digital buses do not prove RF coexistence. `SG-N24` nevertheless
requires real concurrent roles with no hidden time-sharing. What remains open
is the measured channel/power/rate/antenna/wanted-level envelope: same/adjacent
local TX can desensitize a weak peer RX, and same-channel packets also collide.
Firmware must publish the exact qualified profile selected by `DEC-0047` and
measured through `N24H-0001`;
it must neither claim isolated sensitivity nor synthesize RX continuity by
silently pausing peers. C5 protocols still share one native RF resource and use
visible vendor coexistence inside their own group.
