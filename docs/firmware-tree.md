# Leshy2 Firmware Tree

*Read this in: **English** · [Русский](firmware-tree.ru.md)*

The deep-dive for [stage 3](../README.md#3-firmware-tree). It turns the [capability tree](capability-tree.md) (the menu of *what the device could do*) into the **shape of the firmware** — the home launcher, the apps, and every app's split into **main · Lab · Settings**, ordered by how often a user reaches for it. This is the map that [stage 8](../README.md#8-screen--feature-design) then works out screen-by-screen.

## The Lab boundary (the one rule)

Every app splits its features three ways — and in the menu **Lab comes before Settings** (main → Lab → Settings):

- **Main** — everything you can safely point at the world: passive scan / receive / decode / detect, reading and writing **your own** media, and **legitimate own-authority transmit** (LoRa / Meshtastic / APRS on your callsign, walkie voice, IR to your own gear, replay of a signal *you* captured from *your* device).
- **Lab** — **own-equipment / isolated-space only.** The rule is not "does it transmit" — legitimate comms transmit too. **Lab = a transmit whose effect lands on gear or spectrum you don't own and aren't authorized to test**: attack, impersonation, jam, DoS, flood, inject, spam, brute-force, and replay of a *third party's* signal. Each Lab tool carries **its own settings** (power, target, parameters) — on your gear in an isolated space, you decide what to test. Receive-only apps (Radio RX, GPS) carry an intentionally **empty Lab**, noted inline — never a silent gap.
- **Settings** — the app's config and infrastructure: drivers, band filters, identity / keys, DSP, per-app preferences.

Every Lab tool boots **disarmed** and is armed behind the [ARM interlock](#global-chrome--safety); the hardware **STOP** key and **long-BACK** panic kill are live from any screen at all times.

## Install-time harm agreement

A first-boot flow, before any radio is reachable — the way [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy) does it:

1. **Language pick.**
2. **Harm agreement** — a full-screen pledge (*do no harm; transmit only on equipment you own or are authorized in writing to test*). It must be **scrolled to the end** to unlock the buttons; **hold-to-confirm** OK = Accept, F1 = Decline. Decline → the device powers off; until acceptance is on record the home menu is locked to **Settings + Shut down** only.

That's the whole gate — **no forced region wizard.** **TX defaults to maximum, the way [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy) does** — on your own gear in an isolated space *you* decide what to test, so power / band / duty are plain **settings** (each Lab tool's own, plus a global default), never a compliance gate that blocks use. You are responsible for your local law, as the pledge says.

Acceptance is stored in NVS, **stamped with the firmware version and the set of Lab tools present**. It re-shows after a factory reset and — so consent tracks capability — **whenever the set of Lab / attack tools grows** versus the stored stamp. Each power cycle, the first entry into **any** Lab shows a one-line re-affirm (*"Authorized targets only — STOP kills TX"*, single OK). Every Lab tool boots **disarmed** behind the ARM interlock; the hardware STOP and long-BACK kill all TX from any screen always. Safe default after any reset / brownout: all radios off.

## Global chrome & safety

Always present, around every app:

- **Home launcher** — the usage-ordered app grid; encoder scroll, `F1`/`F2` quick-slots, `OPTIONS` context menu. Locked to *Settings + Shut down* until the harm agreement is accepted.
- **Status bar** — TX-power profile · TX-LIVE indicator · active-radio / TDD owner · battery + charge · GPS-fix · **clock (RTC)** · **SD / USB** icon.
- **STOP key** — cuts **all TX** from a high-priority path, any screen, any state — and **"all TX" includes unattended main-tab transmitters** (interval beacons, parrot repeater, cross-band relay), not only Lab tools. **Long-BACK** — all-TX off **+ every Lab tool disarmed** + safe state, from any screen.
- **`OPTIONS` menu (global, from any screen)** — incl. **Shut down** (clean); low-battery → forced clean shutdown; watchdog / brownout → safe-state (all radios off).
- **TX power / band / duty — settings, default maximum** ([esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy)-style). Editable per Lab tool and as a global default; the harm pledge + STOP are the mandatory safety, not a forced region gate.
- **BLE-keyboard text entry** (paired phone, NimBLE HID host) for long text in any field; on-screen keyboard fallback.
- **ARM / DISARM interlock** — every Lab tool boots disarmed; nothing transmits until armed.

**Always-on background services** (not menu apps): the **GPS service** (status-bar fix, RTC discipline, auto geo-tag of every capture), the **RF-coexistence TDD arbiter** (grants one exclusive different-band TX chain at a time — SA868 / LoRa / CC1101 / Wi-Fi; the 3× nRF24 stay one parallel 2.4 GHz set), the **S3↔C5 link IPC**, and **detection alerting** (WS2812 LED / buzzer / GPS-tag / toast; configured under *Settings → Alerts*).

## Cross-app sessions

A few things a user does span several apps, so they get one entry point instead of being scattered:

- **Wardrive** (`F1`/`F2` quick-slot) — one action turns on the Wi-Fi + BLE + sub-GHz scanners with GPS-tagging into one Wigle-style log. The single most common multi-hour session.
- **HID Injection (BadBLE + BadUSB)** — one shared DuckyScript tool (shared parser), reached from two natural Labs: BLE (BadBLE) or USB-C (BadUSB). Lab, disarmed, authorized-host-only.
- **Quick replay (own, tagged)** — a shortcut to re-transmit a signal *you* captured and tagged as your own (sub-GHz / IR). A **main / own-authority** action — STOP-gated like all TX, but *not* behind the Lab ARM interlock — a short path for the frequent own-remote case.

---

## The apps (in usage order)

Each app: **Main** (safe-to-aim) · **Lab** (own-equipment / isolated only) · **Settings**.

### 1. Wi-Fi (2.4 + 5 GHz)
*The first tool most people open; both bands unified so you pick the network view, not the chip.*
- **Main** — AP / station scan (2.4 + 5 GHz) + channel survey + RSSI · beacon / probe sniff + raw PCAP · congestion / packet-rate waterfall · deauth + rogue-AP / evil-twin **detector** (defensive) · client / hidden-SSID inventory + 5 GHz probe harvest · **Zigbee / Thread / 802.15.4 passive sniff + energy scan** (C5, RX-only) · **Drone Remote-ID detector** (Wi-Fi + BLE, GPS-tagged) · unified dual-band survey + cross-band client follow (track a station 2.4↔5 GHz).
- **Lab** — deauth / disassoc (targeted + broadcast; no-op vs 802.11w/PMF) · management-frame floods (beacon spam random/clone/Rickroll, probe / auth / assoc) · Evil Portal · Evil Twin / rogue AP / Karma · 802.11 frame-injection console · ESP-NOW sniff / spoof · **5 GHz deauth/spam — unproven until [bring-up](../README.md#11-on-hardware-bring-up); may fall back to passive.**
- **Settings** — STA connect (authorized nets; no credential entry by firmware) · MAC spoof / randomize · DFS channel policy (active non-DFS, passive 52–144 — the C5 has no radar detection) · ESP-NOW Leshy↔Leshy link pairing · SoftAP web-UI / OTA · C5 link status (SPI3) · scan-dwell / hop.

### 2. Bluetooth (BLE)
*Second-most-reached; adv scan and tracker detection are everyday.*
- **Main** — advertising scanner (ext-adv / Coded-PHY) · offline device DB (OUI + company-ID) + RSSI proximity radar · AirTag / Find My + personal-tracker (stalking) detector · Continuity / Flipper / device-type sniff · GATT enumeration *(own / authorized devices only — an active connect)* · wardriving / geo-log + raw adv PCAP.
- **Lab** — HID keyboard / media injection ([BadBLE](#cross-app-sessions)) · proximity-pairing spam (Apple / Android Fast Pair / Windows Swift Pair / Samsung) · Sour-Apple iOS crash spam (DoS) · Find My / AirTag beacon emulation · arbitrary adv broadcaster (impersonation) · BLE connection-flood / GATT DoS.
- **Settings** — HID-host pairing (phone keystrokes = text input) · scan filters / OUI + company-ID DB · adv TX power / interval / PHY.

### 3. Sub-GHz (CC1101)
*The classic daily-driver — gate / car remotes and 433 / 868 MHz sensors.*
- **Main** — RSSI frequency hunter (coarse + fine) + frequency counter · swept-RSSI spectrum / waterfall · Read RAW (OOK) + RSSI-squelch auto-record · multi-band hopper scan-and-log · decode static-code + rtl_433-style sensor telemetry · rolling-code recognise (no clone) · signal library (view / tag) · **[quick-replay own tagged](#cross-app-sessions)** shortcut.
- **Lab** — raw replay (RAW TX) / emulate decoded protocol *(of a 3rd-party signal)* · fixed-code brute-force / de Bruijn · signal-playlist replay · CW / carrier test tone · narrowband single-target jam / reactive jam.
- **Settings** — SP4T 4-band filter + PLL · arbitrary CC1101 register config · TX power (PATABLE).

### 4. NFC / RFID *(optional M5 RFID2 unit)*
*Headline access-card work — but the whole app is hidden until the optional Grove RFID2 (WS1850S) unit is detected. In the base config (no unit) the order below reflows 1,2,3,5,6…*
- **Main** — ISO14443A discovery + UID / ATQA / SAK recon + fingerprint · MIFARE Classic dump / read (keys known, own cards) · Ultralight / NTAG21x read · NDEF parse · Amiibo read / identify · DESFire / ISO14443-4 APDU transceive · magic-card (gen1a/gen2) detection · card library on SD.
- **Lab** — MIFARE Classic dictionary / nested attack · MIFARE write / restore · Ultralight / NTAG write (incl. PWD_AUTH) · NDEF build / write · UID clone to magic card · magic-card wipe / format · EMV contactless read (privacy-gated).
- **Settings** — unit-presence probe (WS1850S hot-plug) · key-dictionary + reader timing.

### 5. IR (TX + RX)
*A quick, frequent utility — capture, replay, universal remote.*
- **Main** — **universal remote — TV / media / AC / projector / audio** (top: the most common IR action) · IR receive + protocol decode + raw capture · IR transmit decoded command / raw replay *(own devices)* + carrier-freq select · `.ir` import / export + SD library · **[quick-replay own tagged](#cross-app-sessions)**.
- **Lab** — TV-B-Gone universal power-off (nuisance mass power-off) · IR brute-force code sweep.
- **Settings** — code-DB management (own build) · default carrier / protocol.

### 6. RF Spectrum (nRF24 ×3)
*Parallel 3-antenna 2.4 GHz energy waterfall + MouseJack recon.*
- **Main** — 3-radio RPD energy spectrum / waterfall / occupancy (parallel sweep) · Wi-Fi channel energy overlay · Zigbee / 802.15.4 energy view (energy-detect only) · ESB sniff + address discovery · MouseJack vulnerable-device scan · BLE advertising sniff (adv-only) · 3-antenna RSSI direction hunt.
- **Lab** — MouseJack keystroke injection · KeySniffer-class keystroke sniff (own-equipment only) · ESB replay / fake device / address brute-force · BLE adv spoof (via nRF24) · narrowband jam / reactive jam · carrier test tone / sweep-beacon / VSWR aid.
- **Settings** — nRF24 register / channel / antenna-map · CRC-validation filter (false-positive guard) · TX power.

### 7. LoRa & Mesh (SX1262)
*Very popular here — Meshtastic, APRS, range tests. Legitimate own-authority comms in main.*
- **Main** — LoRa P2P messaging (TX + RX) · Meshtastic-compatible mesh node *(phased to a later release)* · LoRa spectrum scan (passive) + promiscuous sniff / log · link / range test (RSSI / SNR) · LoRa-APRS beacon / RX / iGate / digipeater · LoRaWAN node (Class A/C) · generic (G)FSK / RTTY / CW / AX.25 beacon · LoRa OTA / inter-unit file transfer.
- **Lab** — narrowband single-target LoRa / carrier jam · reactive jam-on-detect.
- **Settings** — band-plan + duty + power · PHY defaults (SF / BW / CR) · keys / callsign / node config.

### 8. Radio RX (FM / HF / SW — Si4732)
*Everyday listening on the DSP receiver. No transmit path — Lab is empty.*
- **Main** — FM broadcast + RDS · AM (LW / MW / SW) · SSB (USB / LSB) + CW + sync-AM · bandscope / swept-RSSI spectrum · scanner + SD logging · RX audio record (WAV) · CW / RTTY / SSTV / WEFAX decode.
- **Lab** — *(empty — receive-only subsystem)*.
- **Settings** — tuning / DSP (bandwidth, seek, S-meter, AGC / attenuator, soft-mute, AVC, BFO / calibration) · presets / band-plans · SSB patch blob load (user-supplied) · audio-mux routing + calibration.

### 9. GPS & Navigation
*The GPS **service** runs always (status-bar fix, RTC, auto geo-tag) — this **app** is the navigation UI, opened less often.*
- **Main** — position / nav / satellite view · track / breadcrumb log (GPX / KML) · waypoints / geofence · **GNSS interference / spoofing indicator** (defensive) · wardriving log entry ([cross-app Wardrive](#cross-app-sessions)).
- **Lab** — *(empty — receive-only positioning)*.
- **Settings** — u-blox config (update rate, constellations, dynamic model) · AssistNow offline aiding · time-sync / RTC discipline (GPS + NTP).

### 10. UHF Walkie (SA868)
*Occasional half-duplex analog-FM voice / APRS — licence-gated legitimate comms, so no attack leaf.*
- **Main** — NFM voice RX + TX (≤2 W) · channel / CTCSS-DCS tone scan + carrier-busy / RSSI · manual PTT / VOX voice · UHF RX audio record (WAV) · 1750 Hz burst / DTMF encode + decode · APRS (AFSK1200) TX / RX / iGate + AX.25 KISS TNC · SSTV TX / fox-hunt beacon · **auto-retransmitters** — simplex parrot repeater, cross-band relay *(licensed / authorized use — ID + duty; they re-transmit third-party audio)*.
- **Lab** — *(empty — licensed voice comms; every TX inherits STOP)*.
- **Settings** — channel / tone / squelch / bandwidth / volume · roger-beep · TX power / duty / ID limits (PMR446 preset available).

### 11. System & Storage
*Setup and maintenance, opened rarely.*
- **Main** — SD file browser + config import / export + offline device DB · capture / replay store (sub-GHz + IR + ESB) with tagging / playlists · device info / self-test · battery gauge / charge status · Grove / M5 I²C-unit enumerate + hot-plug detect.
- **Lab** — USB HID keyboard injection ([BadUSB](#cross-app-sessions)).
- **Settings** — display / theme / status-bar · input (touch / encoder / buttons / on-screen keyboard) · **Alerts / Detection** (per-detector on/off + channel: LED / buzzer / GPS-tag / toast) · OTA (Wi-Fi / SD / C5 over SPI3) · USB serial CLI + mass-storage (SD-as-drive) · power / sleep / peripheral + C5 power gating · WS2812 LED + buzzer · analog audio routing (mux / PAM8302 / jack-detect via PCA9555) · RF-coexistence (TDD) policy · global TX-power / band / duty defaults (default max) · factory reset + crash / core-dump viewer + RTOS task mgmt · about.

---

## Beyond the tree (deferred / ceiling)

Not placed — the silicon or the law rules them out (mirrors the [capability tree ceiling](capability-tree.md#beyond-the-ceiling-out-of-scope)): WPA PMKID / EAPOL handshake capture · full 5 GHz monitor+inject / assoc-auth flood · **wideband / full-band jamming** on any radio (only narrowband single-target jam is kept, in Lab) · nRF24 as an 802.11 / full-BLE receiver · Bluetooth Classic / BLE-connection-following sniff / BLE jam · HF-TX, VHF airband + weather (~162 MHz), 30–64 MHz, DRM · NFC emulation / relay / ISO15693 / FeliCa / 125 kHz LF / hardnested-darkside · SA868 true-duplex repeater / digital voice · wideband SDR / Linux-class analytics / cellular. **Meshtastic full mesh** stays in scope but phased to a later release.

---

*Built from three usage-ordered designs, synthesised, then reviewed for completeness, Lab-boundary leaks, and priority/UX. It feeds the per-screen, per-feature design of [stage 8](../README.md#8-screen--feature-design).*
