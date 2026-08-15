# Leshy2 Firmware

*Read this in: **English** · [Русский](README.ru.md)*

**Firmware for [Leshy2](https://github.com/anton-vinogradov/esp32-leshy2) — an open-source, portable, multiband RF handheld you build yourself.**

Leshy2 is a two-chip field tool: a mature **ESP32-S3** brain that runs everything, plus an **ESP32-C5** co-processor for native **5 GHz** Wi-Fi. This repository is its **firmware** — designed from the device's own capabilities, reusing proven code from [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy) (itself a fork of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV)) and other open-source, with a thin C5 5 GHz agent over the S3↔C5 link. The hardware — schematic, PCB, BOM — lives in the [esp32-leshy2](https://github.com/anton-vinogradov/esp32-leshy2) repo.

> 🛑 **Your own gear only.** An educational security-research and radio tool. Use it only on networks, devices, and radios you own or are explicitly authorized in writing to test. Radio law differs by country — it is on you to check and obey it.

---

## 📖 How this repo works — design first, then build

Like the hardware repo, this README is the project's **source of truth**. We **design the firmware in the doc before we write the code**: each stage sets a **Spec** (what and why), records the **Decisions** made in it, and only then produces **Artifacts** (code + docs) that implement exactly that design. Read it as *spec → decisions → implementation* — and every line of code should trace back to a decision written here.

**Status:** ⏳ planned → 🟡 in progress → ✅ done → 🔬 reviewed. A stage turns 🔬 only after its own self-review; edit it afterwards and it drops back to ✅. **Nothing is implemented yet — this is the design stage.**

| # | Stage | Status |
|--:|-------|:------:|
| 1 | [Vision & scope](#1-vision--scope) | ✅ |
| 2 | [Capability tree](#2-capability-tree) | ✅ |
| 3 | [Firmware tree](#3-firmware-tree) | 🔬 |
| 4 | [Target & toolchain](#4-target--toolchain) | ✅ |
| 5 | [System architecture](#5-system-architecture) | ✅ |
| 6 | [Peripheral & driver map](#6-peripheral--driver-map) | ⏳ |
| 7 | [UI/UX & control conventions](#7-uiux--control-conventions) | ⏳ |
| 8 | [Screen & feature design](#8-screen--feature-design) | ⏳ |
| 9 | [Emulation & test harness](#9-emulation--test-harness) | ⏳ |
| 10 | [Implementation](#10-implementation) | ⏳ |
| 11 | [On-hardware bring-up](#11-on-hardware-bring-up) | ⏳ |

---

## 1. Vision & scope

**✅ Spec.** Bring the [Leshy2 hardware](https://github.com/anton-vinogradov/esp32-leshy2) to life in firmware: **design it from the device's own capabilities**, add a thin **ESP32-C5 5 GHz agent** behind a narrow **S3↔C5 protocol**, and implement the device's control conventions and its two safety blockers. Working code from [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy) and other open-source is reused wherever it fits. The capability set is the one defined in the hardware repo's [stage 2](https://github.com/anton-vinogradov/esp32-leshy2#2-what-it-must-do--capabilities); nothing here promises radio behaviour the silicon can't do.

**In scope:** the S3 main firmware (UI, display + touch, all wired radios, buses, SD / PCAP, native 2.4 GHz Wi-Fi + BLE), the C5 agent (5 GHz Wi-Fi + nRF24 2.4-raw + IR), the S3↔C5 link, TX power / band / duty as user settings (default maximum, leshy1-style), and an emulation / test harness that runs before hardware exists.

**Out of scope (same ceilings as the hardware):** full 5 GHz monitor + injection, WPA-handshake capture, Linux-class analytics, HF transmit, wideband SDR, cellular, and wideband jamming. See the hardware repo's [stage 1](https://github.com/anton-vinogradov/esp32-leshy2#1-why-a-new-device--vision) for why each is out.

**Decisions.**

- **Design fresh from the device's capabilities; reuse code per capability, not wholesale.** Leshy2 is a different device (two chips, a link, a much richer radio set), so its architecture is designed top-down from a [capability tree](#2-capability-tree) → a [firmware tree](#3-firmware-tree), not inherited from any one project's skeleton. For each leaf we look at how open-source analogues (esp32-leshy, ESP32-DIV, Marauder, Bruce, Flipper, …) solve it and decide: **borrow the code, write it fresh, or take only the idea.** Nothing that works is thrown away — but nothing dictates the skeleton either.
- **The C5 is the co-processor for 5 GHz Wi-Fi, the 3× nRF24 (2.4 raw) and IR, behind a narrow S3↔C5 protocol.** They sit on the C5's own board, so the C5 drives them locally; the S3 stays the brain and owns the UI, commanding the C5 (and pushing its OTA) over a SPI3 + DRDY command / event link — the two codebases stay decoupled.
- **Orderly shutdown is a firmware feature, not the master switch.** The switch cuts the pack instantly, so an in-flight PCAP / log would corrupt; **OPTIONS → Shut down** (and a long-BACK) flushes SD, parks every radio, stops S3 + C5, then shows a "safe to flip" screen.
- **long-BACK / STOP kills all TX, over any screen.** One core handler — reached from the hardware STOP key or a long-BACK — stops every transmit chain without pulling power.
- **Long text is typed on a paired phone over BLE.** No room for an onboard keyboard; a BLE companion is the primary path, a Wi-Fi captive portal the fallback, the D-pad char-wheel the offline stopgap.

**Artifacts.** This README (the design). The firmware itself follows, stage by stage.

---

## 2. Capability tree

**✅ Spec.** Look at what open-source analogues do with hardware like ours (ESP32-DIV, Marauder, Bruce, Flipper, M5 tools, …) and enumerate **everything this device could do**, organised as a tree by subsystem. Each leaf records a reuse call — **borrow the code, write it fresh, or take only the idea** — plus the hardware / safety / legal gate on it. This is the menu the [firmware tree](#3-firmware-tree) is then built from.

**Decisions.**

- **Organised by subsystem; every leaf carries a reuse call and a gate.** The tree groups capabilities under 11 subsystems (2.4 GHz Wi-Fi, raw 2.4/nRF24, 5 GHz + 802.15.4/C5, BLE, sub-GHz/CC1101, LoRa+GPS, Si4732, SA868, NFC via an optional Grove unit, IR, system) plus a cross-cutting layer, each leaf tagged **borrow / write / idea** and gated by a hardware, safety, or legal limit — so "reuse per capability" is concrete, not a vibe.
- **License discipline drives the reuse call.** Our firmware is MIT, so code is *copied* only from permissive donors (ESP32-DIV, esp32-leshy, ESP-IDF, RadioLib, SparkFun, Arduino-IRremote, LVGL, miguelbalboa/rfid). The big copyleft analogues — **Marauder (GPL-3.0), Bruce (AGPL-3.0), Flipper (GPL-3.0)** — are **idea only** (reimplement clean); a capability *only* they implement is never "borrow".
- **The ceiling is the hardware's.** Every out-of-scope leaf (full 5 GHz monitor+inject, WPA-handshake capture, wideband jamming, BT-Classic, HF-TX, NFC emulation, Linux-class analytics) is marked `⛔` and matched to the hardware ceiling — the [out-of-scope list](https://github.com/anton-vinogradov/esp32-leshy2#1-why-a-new-device--vision), extended with firmware-level silicon limits (BT-Classic, NFC emulation) the list itself didn't enumerate. Narrowband single-target jam stays in; wideband jam is out.
- **The adversarial review surfaced real capabilities the first pass missed** and corrected licenses: **USB-HID BadUSB** (the S3's native USB-OTG makes DuckyScript-over-USB-C real), **Drone Remote-ID detection** (Wi-Fi + BLE, broadcast in the clear), **ESP-NOW** peer link, **GNSS jamming/spoofing detection**; plus the PMF/802.11w caveat on deauth and the DFS gate on active 5 GHz scanning.

**Artifacts.**

- **[docs/capability-tree.md](docs/capability-tree.md)** (+ [RU](docs/capability-tree.ru.md)) — the full tree: 11 subsystem branches + a cross-cutting layer + the out-of-scope ceiling, each leaf with its reuse call, donor + license, and gate.
- This menu feeds the [firmware tree](#3-firmware-tree), which selects and structures it into modes.

---

## 3. Firmware tree

**🔬 Spec.** Turn the [capability tree](#2-capability-tree) into the shape of the firmware — the home launcher, the apps, and every app's split — ordered by how often a user reaches for it. This is the map [§8](#8-screen--feature-design) then works out screen by screen. Full tree: **[docs/firmware-tree.md](docs/firmware-tree.md)**.

**Decisions.**

- **Organised as usage-ordered apps, not by chip.** 11 top-level apps ranked most-used-first (Wi-Fi, BLE, sub-GHz, NFC, IR, RF-spectrum, LoRa, Radio-RX, GPS, walkie, System); the user thinks "Wi-Fi," not "which chip," so 2.4 + 5 GHz sit under one app. Follows the [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy) / ESP32-DIV muscle memory a returning user already has.
- **Every app splits into main · Lab · Settings** (Lab before Settings in the menu). The **Lab rule** is not "does it transmit" — legitimate own-authority comms transmit too. **Lab = a transmit whose effect lands on gear or spectrum you don't own / aren't authorized to test** (attack, impersonation, jam, DoS, flood, inject, spam, replay of a 3rd-party signal); each Lab tool carries its own settings (power, target). Passive/receive and own-authority TX stay in main; receive-only apps carry an intentionally empty Lab.
- **An install-time harm agreement gates the whole device** (like leshy1): a first-boot pledge (scroll-to-end + hold-to-confirm) — and that is the whole gate, **no forced region wizard**. **TX defaults to maximum (leshy1-style)**; power / band / duty are plain settings (each Lab tool's own + a global default), since on your own gear in isolation you decide what to test. Re-shown after a factory reset and **whenever the Lab-tool set grows** vs the stored stamp; every Lab tool boots disarmed behind an ARM interlock; the hardware STOP / long-BACK kill all TX from any screen at all times.
- **A few sessions span apps** — Wardrive (one action → Wi-Fi + BLE + sub-GHz scanners + GPS-tag), HID Injection (BadBLE + BadUSB share one access point), quick-replay of own tagged signals. GPS, the TDD arbiter, the S3↔C5 link, and detection alerting run as always-on background services, not menu apps.

**Artifacts.**

- **[docs/firmware-tree.md](docs/firmware-tree.md)** (+ [RU](docs/firmware-tree.ru.md)) — the full tree: the Lab-boundary rule, the install agreement, global chrome + safety, the cross-app sessions, the 11 apps (main / Lab / Settings), and the deferred ceiling.
- This map feeds the per-screen, per-feature design of [§8](#8-screen--feature-design).

---

## 4. Target & toolchain

**✅ Spec.** Pick the base framework, the two-target build (S3 + C5), the repo layout, and CI. This is the first real fork and it shapes everything downstream — the [test harness](#9-emulation--test-harness) most of all — so each side is steelmanned before any code is written.

**Decisions.**

leshy and most of the open-source we'll draw on are **PlatformIO / Arduino** codebases (TFT_eSPI display, NimBLE, `WiFi.h` promiscuous, LittleFS), so the toolchain has to keep that **reuse surface** open. But the [harness](#9-emulation--test-harness) runs on **ESP-IDF** tools (Linux host-target + CMock, `idf.py qemu`), and the second chip — **ESP32-C5** — is new silicon whose first-class, current support lives in ESP-IDF (C5 v1.0 is production since IDF 5.5.2); stock PlatformIO's Espressif platform does not even carry the C5. Three ways to resolve the fork, each steelmanned:

- **(A) Stay on Arduino / PlatformIO.** *For:* fastest to a running device, keeps the Arduino reuse surface, the largest community. *Against:* stock PlatformIO's Espressif platform has stalled and ships no C5 (you lean on the community `pioarduino` fork), and the §9 stack (host-target, CMock, `idf.py qemu`) is IDF-native — bolted on here, not first-class.
- **(B) Pure ESP-IDF (no Arduino).** *For:* first-class, current C5 support for the 5 GHz agent; the cleanest dual-chip build; a native §9 harness. *Against:* drops the Arduino reuse surface — every module we'd borrow (TFT_eSPI, NimBLE, code from leshy / Marauder / Bruce) has to be rewritten against raw IDF.
- **(C) ESP-IDF build system, Arduino kept as a component.** *For:* build with `idf.py` / CMake (so the C5 is first-class and §9 is native) while the **S3 keeps the Arduino APIs as an ESP-IDF component** — so Arduino modules we borrow compile nearly as-is — and the **C5 agent is native ESP-IDF** (a thin radio agent, no Arduino). The standard path for a project that borrows from the Arduino ecosystem but needs IDF's toolchain and a new chip. *Against:* one-time build-system setup and a component pin to keep in step.

**Chosen: (C).** It is the only option that meets all the constraints at once — the Arduino reuse surface (Arduino-as-component on the S3), the C5 5 GHz agent on current silicon (native IDF), and the IDF-native harness. (A) leaves §9 and the C5 second-class; (B) throws the Arduino reuse surface away.

**Artifacts.**

- **Two ESP-IDF apps, one shared link component:** `firmware/s3/` (the main firmware, Arduino as a component), `firmware/c5/` (the native-IDF agent — 5 GHz Wi-Fi + nRF24 2.4-raw + IR; RF24 / Arduino-IRremote are S3-only Arduino libs, so these drivers are written against ESP-IDF), and `firmware/common/link/` — the [S3↔C5 protocol](#5-system-architecture), compiled into both firmwares *and* the host tests.
- **Toolchain pin:** ESP-IDF **5.5.x** (carries C5 v1.0 production support, maintained into 2028) with **arduino-esp32 3.3.x** as the S3 component (that line tracks IDF 5.5). One IDF, two targets — `esp32s3` and `esp32c5`.
- **CI:** GitHub Actions on the official `esp-idf` action — a matrix that builds the S3 app, builds the C5 app, and runs the host-target Unity + CMock suite, plus an `idf.py qemu` smoke boot. Nothing reaches copper on red (see [§9](#9-emulation--test-harness)).
- **PlatformIO** stays as an optional convenience env via the `pioarduino` fork, but `idf.py` is canonical so the harness and CI stay first-class.
- This section is the design; the two-app skeleton is stood up in [§10](#10-implementation) against exactly these pins.

---

## 5. System architecture

**✅ Spec.** The runtime shape on the S3 (RTOS tasks, dual-core split), the **S3↔C5 link protocol**, the top-level state machines, and the **HAL boundary** that lets every driver run against a test stub. The link is the novel, risky part, so it gets its own spec: **[docs/link-protocol.md](docs/link-protocol.md)**.

**Decisions.**

- **The S3↔C5 link: SPI Slave HD + DMA, master-pull, `DRDY` for push.** The S3 is master and initiates every transfer; the C5 raises a `DRDY` line to ask the S3 to read a queued event. 64-byte slots, an 8-byte framed header with sequence + CRC-16, `ACK` / retransmit / timeout on state-changing commands, best-effort ordered events, `PING` / reset resync. Frame + opcode tables and the state machines are in [docs/link-protocol.md](docs/link-protocol.md) — the C5 agent's 5 GHz, nRF24 (2.4-raw) and IR commands, and its OTA-over-link, all ride these opcodes. *(Pins are owned by the [hardware repo](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/hardware/c5-buses); the link never touches the shared SPI2, so a wedged C5 can't stall the UI or the wired radios.)*
- **Reliability is asymmetric — the master pulls anything that matters.** The C5 never has to guarantee a push: scan telemetry is best-effort, and anything the S3 truly needs it requests and waits for. That keeps the slave thin.
- **`STOP_ALL` + a C5-side dead-man put the TX-kill safety blocker in the protocol.** `STOP_ALL` is serviced ahead of everything; independently, the C5 self-stops TX if the link goes silent — so a dead S3 or a broken link can't leave the C5 transmitting. `C5_EN` low is the hard kill behind that.
- **Dual-core split on the S3: UI on one core, radios + link on the other.** Core 1 runs render / touch / input; core 0 runs the wired-radio drivers, the 2.4 GHz Wi-Fi/BLE stack, the SD/PCAP writer, and the **link task** — so a full-screen redraw never stalls radio or link servicing. This is the firmware side of the hardware's DMA-double-buffer + bus-arbiter decisions.
- **One task owns SPI3.** The link task is the sole owner of the S3↔C5 bus: it turns high-level mode requests into commands and dispatches incoming events to the mode handlers. Single owner ⇒ no bus contention and one home for the retry/timeout logic.
- **HAL boundary = a portable seam per driver.** Each driver (display, radios, storage, buttons, link transport) sits behind a thin interface with a real ESP backend and a host fake. The link **codec** is pure portable C in `common/link/`, compiled into both firmwares *and* the host tests — so the two chips can't drift apart, and [§9](#9-emulation--test-harness) can exercise loss / CRC / timeout in CI without hardware.

**Artifacts.**

- **[docs/link-protocol.md](docs/link-protocol.md)** (+ [RU](docs/link-protocol.ru.md)) — the full link spec: physical layer, 64-byte slots, frame + opcode tables, the DRDY handshake, reliability, versioning, timing defaults, and the two state machines.
- **`firmware/common/link/`** — the portable codec the doc specifies (framing, CRC, sequence/ACK, state machines), shared by the S3, the C5, and the host tests. Built in [§10](#10-implementation) against this design.
- This section is the design; the RTOS task map and the driver HAL headers land with the [§10](#10-implementation) skeleton.

---

## 6. Peripheral & driver map

**⏳ Planned.** Every chip to a driver: 3× **nRF24L01+** (shared-CE modes — parallel RX scan, mousejack, simultaneous multi-channel TX), **CC1101** + SP4T band select, **SX1262** LoRa, **Si4732** RX, **SA868** walkie, **PCA9555** ×2, **74HC138**, **ST7796** + capacitive touch, microSD, u-blox **GPS**, **WS2812**, encoder + buttons. Each driver is defined against the HAL boundary from [stage 5](#5-system-architecture) so it can be tested without hardware. *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

## 7. UI/UX & control conventions

**⏳ Planned.** Menu and navigation, the D-pad + encoder + side buttons, the locked control conventions, the safety handlers (long-BACK stops all TX; clean shutdown), and BLE text entry. *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

## 8. Screen & feature design

**⏳ Planned.** Take the [firmware tree](#3-firmware-tree) and work it out **screen by screen, feature by feature**: every screen's layout, controls, flow and states; every feature's behaviour, parameters, and its main / Lab / Settings placement; the install-agreement and Lab-arm screens; TX power / band / duty settings surfaced in the UI (default maximum). This is the detailed design the [implementation](#10-implementation) builds directly. *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

## 9. Emulation & test harness

**⏳ Planned.** Run the firmware on emulators before the board exists — **ESP-IDF Linux host-target + CMock** for drivers and the link protocol in CI, **Wokwi** for the UI and the buses (radios as behavioural custom chips), **Renode / QEMU** for boot and the two-node S3↔C5 link. Digital logic only; RF, analog, and power stay on hardware. This is the firmware half of the hardware repo's [emulation stage](https://github.com/anton-vinogradov/esp32-leshy2#10-firmware-validation-in-emulation). *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

## 10. Implementation

**⏳ Planned.** Build each module against the design above — driver by driver, mode by mode — each piece traceable to a decision in stages 2–9 and validated in the harness ([stage 9](#9-emulation--test-harness)) before it ever touches copper. *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

## 11. On-hardware bring-up

**⏳ Planned.** Flash the real board, bring up power / boot / the SPI3 link / each bus, prove the C5's 5 GHz, and tune. Ties into the hardware repo's [fabrication & bring-up](https://github.com/anton-vinogradov/esp32-leshy2#11-fabrication--bring-up). *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

*Get involved: [CONTRIBUTING.md](CONTRIBUTING.md).*

## License

MIT — see [LICENSE](LICENSE). Same as upstream ESP32-DIV and the [Leshy2 hardware](https://github.com/anton-vinogradov/esp32-leshy2).
