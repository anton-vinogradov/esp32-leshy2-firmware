# Leshy2 Capability Tree

*Read this in: **English** · [Русский](capability-tree.ru.md)*

The deep-dive for [stage 2](../README.md#2-capability-tree). This is the **menu of everything the Leshy2 hardware could do** — enumerated from what open-source analogues do with hardware like ours, organised by subsystem. The [firmware tree](../README.md#3-firmware-tree) is then built *from* this menu; it does not have to implement every leaf.

Each leaf carries a **reuse call** and a **gate**, so "design fresh, reuse per capability" is a plan, not a vibe.

## How to read a leaf

- **Reuse** — how we get the code:
  - **borrow** — a permissively-licensed donor exists; copy/adapt it.
  - **write** — no good donor; write it fresh (often a thin wrap over an ESP-IDF/driver primitive).
  - **idea** — the concept is proven, but the only donor is copyleft; **reimplement clean, do not copy**.
- **Gate** — what limits the leaf: a **hardware** ceiling, a **safety** interlock, or a **legal/region** rule. `⛔` marks a leaf **beyond the silicon ceiling** (out of scope; listed at each branch's end).

## The license discipline (why so many "idea")

Our firmware is **MIT**. Code may only be *copied* from permissive sources — **MIT / BSD / Apache-2.0 / Unlicense / public-domain**. The three biggest ESP32 analogues are copyleft: **ESP32 Marauder is GPL-3.0**, **Bruce is AGPL-3.0**, **Flipper Zero firmware is GPL-3.0**. So a capability that *only* those implement is **idea** (reimplement clean), never **borrow** — copying it would force our firmware to GPL. Where a permissive donor also exists (**ESP32-DIV** and **esp32-leshy**, both MIT; **ESP-IDF** Apache-2.0; **RadioLib**, **SparkFun** libs, **Arduino-IRremote**, **LVGL** MIT; **miguelbalboa/rfid** Unlicense), we **borrow** from it and treat the copyleft project as a reference only.

---

## 1. 2.4 GHz Wi-Fi (ESP32-S3, native)

The S3 radio does management-frame work directly. Full monitor+injection / WPA-handshake capture is on the ceiling.

| Capability | Reuse | Gate |
|------------|-------|------|
| AP scan, station/client enumeration | borrow — ESP32-DIV, ESP-IDF `esp_wifi` scan (MIT/Apache) | — |
| Beacon / probe sniff, raw promiscuous PCAP | borrow — ESP-IDF promiscuous + `pcap` (Apache), ESP32-DIV | one channel at a time (hop); encrypted payloads opaque |
| Packet-rate / congestion / channel-activity monitor | borrow — ESP32-DIV waterfall (MIT) | — |
| Deauth-attack detector (defensive) | borrow — ESP32-DIV Deauth Detector (MIT) | — |
| Targeted + broadcast deauth / disassoc | borrow — ESP32-DIV Deauther (MIT); Marauder/Bruce = idea-ref | legal: authorized-only, region caps + STOP · **no-ops against 802.11w/PMF (WPA3, most modern WPA2)** |
| Management-frame floods (beacon spam random/clone/Rickroll, probe flood, auth/assoc flood) | borrow beacon/probe (ESP32-DIV MIT); auth/assoc flood = **idea** (Bruce AGPL) | legal: spectrum abuse / DoS — authorized-only, duty cap + STOP |
| Evil Portal (captive-portal credential capture) | borrow — ESP32-DIV Captive Portal (MIT) | legal: phishing — strictly authorized; firmware never exfiltrates captures |
| Evil Twin, rogue/honeypot AP, Karma/probe-response | borrow twin/rogue (ESP32-DIV MIT); Karma = **idea** (MANA/Bruce) | legal: impersonation + DoS — authorized-only, STOP |
| MAC spoof / randomize; STA join | write — `esp_wifi_set_mac` / STA (Apache) | — |
| 802.11 frame-injection primitive (the TX engine) | write — ESP-IDF `esp_wifi_80211_tx` (Apache) | legal: gate every caller (own-equipment, caps, STOP) |
| **ESP-NOW** — Leshy↔Leshy link; sniff / spoof | borrow link (ESP-IDF Apache); sniff/spoof = write over the injection primitive | link none; sniff/spoof TX-gated. Faster short-range alternative to LoRa P2P |
| Web-UI config / OTA over SoftAP | borrow — WiFiDuck web UI, ESP32-DIV (MIT) | — |
| ⛔ WPA PMKID / EAPOL-handshake capture | idea | **ceiling:** handshake capture is out of scope; crack off-device from PCAP |

---

## 2. Raw 2.4 GHz (3× nRF24L01+PA/LNA)

Three independent nRF24 on separate antennas — energy sensing and ShockBurst tricks, no 802.11 demod. **They sit on the C5 board and are driven by the C5 agent** (behind the [SPI3 link](link-protocol.md#4-opcodes-v1) — `NRF_*` opcodes); the S3 commands them over the link. The `RF24` library is GPLv2 *and* Arduino, so on the native-IDF C5 the driver is written clean against ESP-IDF SPI.

| Capability | Reuse | Gate |
|------------|-------|------|
| nRF24 register/SPI driver | write — TMRh20/RF24 (GPLv2) = idea-ref | — |
| RPD energy spectrum: parallel 3-radio sweep, waterfall, occupancy | borrow — ESP32-DIV scanner, esp32-leshy (MIT) | RPD is a coarse ~−64 dBm carrier flag, **not** RSSI; energy only |
| Wi-Fi channel energy overlay; Zigbee/802.15.4 energy view | borrow — ESP32-DIV (MIT) | energy-detect only — cannot demodulate 802.11 or O-QPSK |
| ESB (Enhanced ShockBurst) sniff + address discovery | borrow — ESP32-DIV ESB Sniffer (MIT) | high false-positive; validate CRC in SW |
| MouseJack: vulnerable-device scan + keystroke injection | borrow — ESP32-DIV MouseJack (MIT); JackIt = idea-ref | legal: written-authorization only; TX caps + STOP |
| KeySniffer-class unencrypted keystroke sniff | idea — Bastille research (GPLv3) | own-equipment / authorized only |
| ESB replay / fake device / address brute-force | borrow replay (ESP32-DIV MIT); rest write | authorization; TX caps + STOP |
| BLE advertising sniff / spoof via nRF24 | idea — Dmitry Grinberg nRF24-BLE (write-up) | lossy: nRF24 has no true BLE PHY; adv-only |
| Single-channel narrowband jam; reactive jam-on-detect | borrow jam (ESP32-DIV Protokill, esp32-leshy MIT) | legal: narrowband single-target only, authorization + duty cap + STOP |
| Sweep-beacon / carrier test tone / VSWR aid; 3-antenna RSSI hunt | borrow — esp32-leshy (MIT) | TX caps; brief use |
| ⛔ Full-band sweep jammer · BLE-connection sniff · 802.11 capture | idea | **ceiling/ethos:** wideband jam illegal; nRF24 can't follow BLE connections or demod 802.11 |

---

## 3. 5 GHz Wi-Fi + 802.15.4 (ESP32-C5 agent)

The C5's 5 GHz agent over the [SPI3 link](link-protocol.md) — one duty of the C5 co-processor, which also drives the 3× nRF24 (§2) and IR (§10), not a 5 GHz-only agent. Scan / SoftAP / STA are native ESP-IDF (Apache); deauth/disassoc ride a patched `libnet80211` blob that permissive C5 forks (maxbrito500 Apache; AnvilBrain, MIT + ethical-use restriction) demonstrate on their silicon — **unverified on our production C5 until bring-up ([§11](../README.md#11-on-hardware-bring-up))**. The C5 also carries a native **802.15.4** radio (Zigbee / Thread), used here for passive recon only.

| Capability | Reuse | Gate |
|------------|-------|------|
| AP scan (active non-DFS / passive), channel survey, RSSI meter | borrow — ESP-IDF `esp_wifi` scan (Apache), AnvilBrain/maxbrito500 | **active probing only on non-DFS UNII-1/3; passive-only on DFS 52–144** (C5 has no radar detection) |
| Promiscuous sniff (partial monitor) + probe harvest | borrow — ESP-IDF promiscuous (Apache) | lossy, single-channel, no radiotap; privacy: authorized-only |
| Client enumeration; beacon / hidden-SSID inventory | idea (Marauder GPL) / write | authorized-only |
| Deauth-detector, rogue-AP/evil-twin detector (defensive) | write | — |
| Deauth / disassoc | borrow — maxbrito500 (Apache); AnvilBrain = idea-ref (MIT + ethical-use restriction) | legal: authorized-only, region caps + STOP · **unproven on production C5 — verified at bring-up ([§11](../README.md#11-on-hardware-bring-up)); patched blob may fail → fall back to passive recon** · no-ops against PMF |
| Beacon / probe spam | borrow beacon (AnvilBrain MIT); probe = write | legal: spectrum abuse — authorized/lab, caps, STOP |
| Evil-twin SoftAP, evil portal, Karma | borrow SoftAP (ESP-IDF Apache); portal/Karma = idea (GhostESP/Marauder) | legal: authorized-only, non-DFS AP channel, STOP |
| STA connect | borrow — ESP-IDF STA (Apache) | authorized nets; no credential entry by firmware |
| **802.15.4 / Zigbee / Thread passive sniff + energy scan** | borrow — ESP-IDF `ieee802154` promiscuous (Apache); Thread parse = OpenThread (BSD-3) | RX / sniff only — no joining a Zigbee/Thread network (a full stack, out of scope) |
| ⛔ Full 5 GHz monitor+injection · PMKID/EAPOL · assoc/auth flood · wideband jam | idea | **ceiling:** all need full 5 GHz injection / handshake capture / wideband — out of scope |

---

## 4. BLE (ESP32-S3)

S3 BLE 5.0, LE-only. Scan/GATT/HID/beacon come from Apache **NimBLE**; proximity-spam has permissive donors (AppleJuice Apache, EvilAppleJuice WTFPL).

| Capability | Reuse | Gate |
|------------|-------|------|
| Advertising scanner (+ BLE-5 ext-adv / Coded-PHY long-range) | borrow — NimBLE (Apache), esp32-leshy | — |
| Offline device DB (OUI + company-ID) + RSSI radar / proximity | borrow — esp32-leshy (MIT), Bluetooth-SIG numbers (public) | — |
| AirTag / Find My detector + personal-tracker (stalking) detection | write — Apple/Google tracker spec | — |
| Continuity / Flipper / device-type sniff | idea — hexway Apple_BLE (research) | — |
| Wardriving / geo-log + raw adv PCAP to SD | write | — |
| GATT service/characteristic enumeration (central) | borrow — NimBLE gattc (Apache) | authorized/own devices only |
| HID host (receive phone keystrokes) + HID keyboard/media injection (BadBLE) | borrow — NimBLE HID host/device (Apache); Bruce = idea-ref | inject only to a host you own/are authorized to test; STOP |
| iBeacon / Eddystone / custom arbitrary-payload broadcaster | borrow — NimBLE (Apache) | impersonating a real device may be unlawful — authorized-only |
| Proximity-pairing spam (Apple / Android Fast Pair / Windows Swift Pair / Samsung / all) | borrow Apple (AppleJuice Apache, EvilAppleJuice WTFPL); rest = idea (Bruce/simondankelmann GPL) | legal: nuisance to third parties — authorization only, caps + duty + STOP |
| Sour-Apple iOS crash spam | idea — ESP32-Sour-Apple (unclear) | legal/safety: **DoS that crashes devices** — strong authorization gate + STOP |
| Find My / AirTag beacon emulation | idea — OpenHaystack (AGPL/research) | legal: impersonating a tracker enables stalking — authorization only |
| BLE connection-flood / GATT DoS | idea — Bruce (AGPL) | legal/safety: DoS — authorization mandatory |
| ⛔ Bluetooth-Classic (BR/EDR) · connection-following sniffer · BLE jam | idea | **ceiling:** S3 has no BT-Classic radio; the LE controller can't follow connections; jam illegal |

---

## 5. Sub-GHz (CC1101, 300–928 MHz, SP4T 4-band)

One narrow-channel CC1101 behind a 4-band filter. RX/RSSI/raw-capture come from esp32-leshy/DIV (MIT) + **RadioLib** (MIT). Protocol *decode* libraries (Flipper, rtl_433) are copyleft → idea.

| Capability | Reuse | Gate |
|------------|-------|------|
| RSSI frequency hunter (coarse+fine); frequency counter | borrow — esp32-leshy, ESP32-DIV, RadioLib (MIT) | PLL covers ~300–348 / 387–464 / 779–928 MHz only; near-field |
| Sequential-RSSI spectrum / waterfall | borrow — esp32-leshy, ESP32-DIV (MIT) | single narrow channel, no IQ — swept view, not real-time |
| Read RAW (OOK timing) + RSSI-squelch auto-record | borrow — esp32-leshy, ESP32-DIV (MIT) | RX only; storage bounded by RMT/SD |
| Multi-band hopper scan-and-log | borrow — esp32-leshy (MIT) | sequential dwell misses brief signals between hops |
| Decode static-code protocols · rtl_433-style sensor telemetry · rolling-code recognise (no clone) | idea — Flipper (GPL), rtl_433 (GPL-2) | RX/decode only; rolling codes are single-use, not cloneable |
| Raw replay (RAW TX) · emulate decoded protocol | borrow raw replay (esp32-leshy MIT); emulate = idea (Flipper GPL) | TX: authorized-only, region PATABLE caps + STOP |
| Fixed-code brute-force / de Bruijn | idea — Flipper/Bruce (GPL/AGPL) | active TX attack — strictly own-equipment/authorized |
| Signal library / tagging / playlist replay | borrow — esp32-leshy (MIT) | replay inherits the TX gate |
| Arbitrary CC1101 config; CW test tone | borrow — RadioLib (MIT) | freq limited to CC1101 bands; TX caps + STOP |
| SP4T band-filter management (infra) | write | 4 filtered bands + PLL gaps bound coverage |
| Single-channel narrowband jam; reactive jam-on-detect | write — RadioLib carrier/CW TX (MIT) | legal: narrowband single-target only, authorization + duty cap + STOP |
| ⛔ Full-band / wideband sub-GHz jam · true wideband real-time SDR | idea | **legal/ceiling:** wideband jam illegal; CC1101 is single-channel, not an SDR |

---

## 6. LoRa / Meshtastic (SX1262) + GPS (u-blox)

**RadioLib** (MIT) covers nearly all PHY / LoRaWAN / APRS / RTTY. Meshtastic and the u-blox lib split into copyleft-vs-MIT.

| Capability | Reuse | Gate |
|------------|-------|------|
| Raw LoRa P2P messaging (TX+RX) | borrow — RadioLib (MIT) | per-region ISM band + power/duty caps + STOP |
| Meshtastic-compatible mesh node | idea — Meshtastic (GPL-3.0) + RadioLib | large effort; must track upstream protocol version |
| LoRa-APRS beacon / RX / iGate / digipeater | borrow — lora-aprs, RadioLib (MIT); iGate/digi = idea (CA2RXU GPL) | amateur licence to TX; own callsign; region caps |
| LoRaWAN node (Class A/C) | borrow — RadioLib LoRaWAN (MIT) | region band-plan + duty by stack; own keys |
| LoRa spectrum scan (passive) + promiscuous sniff/log | borrow scan (RadioLib MIT); sniff/log = write | RX only; can't decode private/Meshtastic payloads without keys |
| Link / range test (RSSI/SNR) | write — RadioLib (MIT) | TX duty/power caps + STOP |
| Generic (G)FSK TX/RX; RTTY / CW / AX.25 beacon | borrow — RadioLib (MIT) | amateur licence; region caps; STOP |
| LoRa OTA / inter-unit file transfer | write — RadioLib (MIT) | slow at LoRa rates; duty caps |
| GPS position/nav + module config + time-sync/RTC discipline | borrow — SparkFun u-blox GNSS (MIT) | — |
| Track / breadcrumb logging (GPX/KML) + waypoints / geofence | write — SparkFun lib (MIT) | — |
| AssistNow offline aiding (fast fix) | borrow — SparkFun lib (MIT) | needs occasional Wi-Fi to refresh aiding |
| **GNSS interference / spoofing indicator** | borrow — SparkFun lib (MIT), UBX-MON-HW `jamInd` / NAV-STATUS `spoofDetState` | passive defensive read-out — optionally alerts |
| Narrowband single-target LoRa / carrier jam; reactive jam-on-detect | write — RadioLib carrier/CW TX (MIT) | legal: narrowband single-target only, authorization + duty cap + STOP |
| ⛔ Wideband / full-band LoRa-band jam | idea | **legal/ethos:** deliberate wideband interference is illegal |

---

## 7. HF / FM receive (Si4732)

A DSP receiver. All RX borrows from **pu2clr/SI4735** and the **ats-mini / ats20_ats_ex** firmwares (MIT). Decoders that need the audio need it tapped to an MCU ADC/I²S.

| Capability | Reuse | Gate |
|------------|-------|------|
| FM broadcast + RDS | borrow — ats-mini, ats20_ats_ex (MIT) | — |
| AM (LW / MW / SW) | borrow — ats20_ats_ex (MIT) | — |
| SSB (USB/LSB) + CW + synchronous-AM | borrow — pu2clr/SI4735 (MIT) | **needs the Silicon-Labs SSB patch blob** (user-supplied at runtime) |
| Tuning + DSP controls (bandwidth, seek, S-meter, AGC/attenuator, soft-mute, AVC, BFO/calibration, presets, band-plans) | borrow — ats20_ats_ex, ats-mini (MIT) | — |
| Bandscope / swept-RSSI spectrum | borrow — ats-mini (MIT) | swept RSSI, not a real FFT |
| Scanner logging to SD | write | — |
| RX audio record (WAV) · CW / RTTY / SSTV / WEFAX decode | write; WEFAX = idea | **need the Si4732 line-out tapped to an MCU ADC/I²S input** |
| ⛔ VHF airband/weather AM (~118–137, ~162 MHz) · 30–64 MHz gap · DRM | idea | **ceiling:** Si4732 tunes AM/SSB ≤30 MHz, FM ≥64 MHz (so airband, NOAA weather radio and 30–64 MHz are uncovered); DRM needs wide-IF COFDM DSP the chip lacks |

---

## 8. UHF walkie (SA868-U, 400–480 MHz NFM, RX + TX ≤2 W)

Half-duplex analog-FM module over an AT-style UART. Module settings are written clean; audio modes (APRS/SSTV/DTMF-decode) need the RX/TX audio wired to the MCU.

| Capability | Reuse | Gate |
|------------|-------|------|
| NFM voice RX + TX | write — SA818/APRS-ESP (reference) | legal/safety: ham licence, or licence-free PMR446 ≤0.5 W fixed-channel; region caps + STOP |
| Tone / squelch / channel controls (CTCSS, DCS, squelch, bandwidth, volume) | write | — |
| Channel scan · CTCSS/DCS tone scan · carrier-busy/RSSI detect | write | — |
| Simplex parrot repeater; roger-beep; VOX; 1750 Hz burst; DTMF encode | write | legal: TX gating (ID + duty limits); needs mic feed for VOX |
| DTMF decode | write | needs RX audio to MCU |
| APRS (AFSK1200) TX / RX / iGate; AX.25 KISS TNC; SSTV TX; fox-hunt beacon | idea — APRS-ESP (GPL-family) | ham licence; UHF-only (no 2 m 144.39 APRS); needs audio paths to MCU; STOP |
| Cross-band audio relay (Si4732 → SA868) + UHF RX audio record | write | legal: retransmission often restricted; TX gating |
| ⛔ True duplex cross-band repeater · digital voice (DMR/C4FM/dPMR) · wideband jam | idea | **ceiling/legal:** one half-duplex module can't RX+TX at once; SA868 is analog-FM only (no vocoder); jam illegal |

---

## 9. NFC / RFID (optional M5 Grove RFID2 unit, WS1850S, 13.56 MHz)

Unlike the ten soldered subsystems, NFC comes from an **optional M5 RFID2 unit (WS1850S) plugged into a Grove I²C port** (see the [Grove/M5 expansion](#11-system--ui--storage--input--power--indicators) leaf) — so the whole branch is gated on runtime unit-presence detection (probe the WS1850S; hide the branch if absent). It is an MFRC522-class **reader/writer** — ISO14443A only, **no card emulation**. Read/write/dump/clone borrow from **miguelbalboa/rfid** (Unlicense); nested/EMV/NDEF logic is copyleft → idea/write.

| Capability | Reuse | Gate |
|------------|-------|------|
| ISO14443A discovery + UID/ATQA/SAK recon + tech fingerprint | borrow — miguelbalboa/rfid (Unlicense) | read range < 2 cm |
| MIFARE Classic: dictionary attack, full dump, write/restore | borrow — miguelbalboa/rfid (Unlicense) | legal: own cards / authorization only |
| MIFARE Classic nested attack | idea — crapto1 / mfoc (GPL/LGPL) | CPU-heavy (minutes/key); own cards only |
| **Magic-card (gen1a/gen2) detection + card wipe / format to blank** | borrow — miguelbalboa/rfid raw transceive (Unlicense) | own cards only |
| Ultralight / NTAG21x read + write (incl. PWD_AUTH) | borrow — miguelbalboa/rfid (Unlicense) | own tags only |
| NDEF parse / build / write | write — Bruce/Flipper NDEF (AGPL/GPL) = idea-ref | — |
| UID clone to magic card | borrow — miguelbalboa/rfid (Unlicense) | legal: cloning credentials needs authorization |
| Amiibo (NTAG215) read/identify | write — Bruce (AGPL) = idea-ref | read-only (write/emulate needs proprietary keys) |
| ISO14443-4 / DESFire APDU transceive · EMV contactless read | borrow transceive (Unlicense); EMV = idea (Bruce AGPL) | T=CL flaky on WS1850S; EMV privacy/legal |
| Card library on microSD | write | — |
| ⛔ Card emulation / relay · hardnested/darkside · ISO15693 · FeliCa · 125 kHz LF | idea | **ceiling:** WS1850S has no emulation, no ISO15693/FeliCa, no 125 kHz; darkside/hardnested are Linux-class |

---

## 10. IR (TX + RX)

38 kHz demodulated RX + IR-LED TX, **on the C5 board, driven by the C5 agent** (behind the [link](link-protocol.md#4-opcodes-v1) — `IR_SEND` / `IR_LEARN`). **Arduino-IRremote** (MIT) is an S3-only reference — on the native-IDF C5 the codec is written clean against the **ESP-IDF RMT** peripheral (so the "borrow" rows below read as "write against IDF RMT"). The *code databases* (TV-B-Gone, universal remotes) are copyleft → build our own.

| Capability | Reuse | Gate |
|------------|-------|------|
| IR receive + protocol decode + raw capture | borrow — Arduino-IRremote (MIT) | demod RX yields envelope only (carrier freq not measured) |
| IR transmit decoded command + raw replay + carrier-freq select | borrow — Arduino-IRremote (MIT) | consumer IR — none |
| TV-B-Gone universal power-off | idea — irdb/Flipper tv.ir (GPL) | build own code DB; nuisance-use legality |
| Universal remote — TV / media / AC / projector / audio | idea — Flipper (GPL), IRremoteESP8266 (LGPL) | build own code DB; AC state-machines are effort |
| IR brute-force code sweep; `.ir` import/export; SD signal library | write | — |

---

## 11. System / UI / storage / input / power / indicators

The non-safety platform layer — mostly MIT/Apache/BSD (LVGL, ESP-IDF, FastLED, M5Stack-SD-Updater, esp32-leshy).

| Capability | Reuse | Gate |
|------------|-------|------|
| Launcher / home menu + GUI toolkit + status bar + theme/settings | borrow — esp32-leshy/DIV, LVGL, ArduinoJson (MIT) | — |
| Capacitive touch + encoder/button input + on-screen keyboard | borrow — GT911/FT6x36, ESP32Encoder, LVGL (MIT) | — |
| **USB HID keyboard injection (BadUSB / DuckyScript over USB-C)** | borrow — ESP-IDF/TinyUSB HID device (Apache/MIT); Ducky parser shared with BadBLE | S3 has **native USB-OTG** — real capability; authorized host only + STOP |
| USB serial CLI + USB mass-storage (SD-as-drive) | borrow — ESP-IDF console + TinyUSB MSC (Apache/MIT) | — |
| OTA over Wi-Fi + OTA from SD + C5 co-processor OTA (over SPI3) | borrow — ESP-IDF `esp_https_ota`, M5Stack-SD-Updater; C5 side writes the link-delivered image via ESP-IDF `esp_ota_ops` (Apache/MIT) | C5 OTA rides the SPI3 link, not ROM serial — no UART bridge / BOOT strap |
| SD file browser + config import/export + offline device DB | borrow — ESP-IDF FatFs, esp32-leshy (BSD/MIT) | — |
| Battery gauge + charge status + sleep/power-management + peripheral & C5 power gating | borrow gauge/sleep (SparkFun, ESP-IDF `esp_sleep`); gating = write | — |
| WS2812 status LED + buzzer feedback | borrow LED (FastLED MIT); buzzer = write | — |
| **Grove / M5 I²C-Unit expansion** — enumerate + hot-plug-detect the 2× Grove ports; drivers for M5 RFID2 (the NFC path, [§9](#9-nfc--rfid-optional-m5-grove-rfid2-unit-ws1850s-1356-mhz)), RTC, IMU, sensors | write — thin drivers over ESP-IDF I²C (Apache) | 3.3 V I²C units only |
| **Analog audio routing** — select the mux source (Si4732 / SA868 / off), enable/mute the PAM8302 amp, read 3.5 mm jack-detect | write — over the PCA9555 control lines | hardware: mux + amp SD on the I²C expander |
| Device info / self-test + crash/core-dump + factory reset + RTOS task mgmt | borrow — ESP-IDF `esp_core_dump`, FreeRTOS (Apache/MIT) | — |

---

## Cross-cutting (spans subsystems)

| Capability | Reuse | Gate |
|------------|-------|------|
| **Safety interlocks** — hardware STOP-key kills all TX, long-BACK panic kill, TX-live indicator, clean shutdown, low-battery→forced shutdown, watchdog/brownout safe-state | write; watchdog borrows ESP-IDF (Apache) | **mandatory** — cut TX from a high-priority path regardless of UI state; safe default after reset = all radios off |
| **Harm / authorization gate** + **TX limits as settings** — the harm agreement is the mandatory consent gate; TX power / band / duty are user settings, **default maximum** (leshy1-style), not a forced compliance gate | write | consent mandatory; power/band/duty default max, user-set |
| **Radio-chain TDD arbitration / RF coexistence** — one owner grants exclusive TX per band at a time (SA868 / LoRa / CC1101 / 2.4 GHz Wi-Fi / C5 nRF24); arbitration is **by band and spans both chips** — the S3's 2.4 GHz Wi-Fi TX and the C5-driven nRF24 2.4-raw set are the **same band, mutually exclusive**, so the 3× nRF24 are one 2.4 GHz TX chain (parallel only among themselves) | write | **mandatory** — keying two chains in one band at once desenses the receivers (RF coexistence, not the SPI bus) |
| S3↔C5 command/telemetry IPC | write — the [link protocol](link-protocol.md) | — |
| Cross-mode target follow (2.4 GHz → 5 GHz); dual-band unified survey; unified spectrum/waterfall | write; unified view = idea-ref (Flipper/Bruce) | TX side inherits deauth/spam gates |
| GPS-tag every RF capture; wardriving (Wigle CSV/KML); cross-mode PCAP logging | write Wigle CSV/KML + tag; borrow PCAP (ESP-IDF `pcap`, Apache) | passive metadata — store/publish per local privacy law |
| RTC / timekeeping (GPS + NTP) | borrow — SparkFun, ESP-IDF SNTP (MIT/Apache) | — |
| Capture/replay store (sub-GHz + IR + ESB) | idea — Flipper (GPL); esp32-leshy (MIT) | replay is TX — gated behind auth + caps + STOP |
| BLE keyboard text entry (primary input) | borrow — esp32-leshy, NimBLE HID host (MIT/Apache) | — |
| **Drone Remote-ID detection** (Wi-Fi beacon/NAN + BLE adv, GPS-tagged) | write / idea — open FAA/EU spec, GPL reference parsers | passive, in the clear; reuses the detection-alert layer |
| Detection alerting (LED / buzzer / GPS) | write | — |

---

## Beyond the ceiling (out of scope)

Consolidated from the `⛔` leaves above — capabilities the silicon (or the law) rules out, matching the hardware repo's [out-of-scope list](https://github.com/anton-vinogradov/esp32-leshy2#1-why-a-new-device--vision):

- **Full 5 GHz monitor + injection**, and any **WPA PMKID/EAPOL handshake capture** (2.4 or 5 GHz) — no ESP32 has the Linux Wi-Fi stack; capture off-device from PCAP instead.
- **Wideband / full-band jamming** on any radio — illegal (US §333, EU RED). Narrowband single-target jam (nRF24/CC1101/SX1262) stays in scope, authorized + STOP-gated.
- **BLE connection-following sniff** and **Bluetooth Classic (BR/EDR)** — the S3 LE controller can't; no Classic radio.
- **nRF24 as an 802.11 or full-BLE receiver** — energy-detect only.
- **HF/CB/shortwave transmit** — Si4732 is receive-only. **VHF airband / NOAA weather (~162 MHz)**, the **30–64 MHz gap**, and **DRM** are outside its tuning/DSP.
- **NFC card emulation / relay**, ISO15693, FeliCa, 125 kHz LF, and hardnested/darkside key recovery — WS1850S is an ISO14443A reader only; the crypto attacks are Linux-class.
- **SA868 true duplex repeater** and **digital voice (DMR/C4FM/dPMR)** — one half-duplex analog-FM module.
- **Continuous wideband SDR / arbitrary TX (HackRF-class)**, **on-device aircrack/Kismet-class analytics**, **cellular/GSM** — a different, far pricier class of device.

---

*This tree was built from a parallel survey of the open-source analogues, then adversarially reviewed for completeness, gate correctness, and license/disposition sanity. It feeds the [firmware tree](../README.md#3-firmware-tree).*
