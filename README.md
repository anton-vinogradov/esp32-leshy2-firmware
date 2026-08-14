# Leshy2 Firmware

*Read this in: **English** · [Русский](README.ru.md)*

**Firmware for [Leshy2](https://github.com/anton-vinogradov/esp32-leshy2) — an open-source, portable, multiband RF handheld you build yourself.**

Leshy2 is a two-chip field tool: a mature **ESP32-S3** brain that runs everything, plus an **ESP32-C5** co-processor for native **5 GHz** Wi-Fi. This repository is its **firmware** — ported from [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy) (itself a fork of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV)), grown to drive the new radios and to run the C5 5 GHz agent over the S3↔C5 link. The hardware — schematic, PCB, BOM — lives in the [esp32-leshy2](https://github.com/anton-vinogradov/esp32-leshy2) repo.

> 🛑 **Your own gear only.** An educational security-research and radio tool. Use it only on networks, devices, and radios you own or are explicitly authorized in writing to test. Radio law differs by country — it is on you to check and obey it.

---

## 📖 How this repo works — design first, then build

Like the hardware repo, this README is the project's **source of truth**. We **design the firmware in the doc before we write the code**: each stage sets a **Spec** (what and why), records the **Decisions** made in it, and only then produces **Artifacts** (code + docs) that implement exactly that design. Read it as *spec → decisions → implementation* — and every line of code should trace back to a decision written here.

**Status:** ✅ done · 🟡 in progress · ⏳ planned. **Nothing is implemented yet — this is the design stage.**

| # | Stage | Status |
|--:|-------|:------:|
| 1 | [Vision & scope](#1-vision--scope) | 🟡 |
| 2 | [Target & toolchain](#2-target--toolchain) | ⏳ |
| 3 | [System architecture](#3-system-architecture) | ⏳ |
| 4 | [Peripheral & driver map](#4-peripheral--driver-map) | ⏳ |
| 5 | [UI/UX & control conventions](#5-uiux--control-conventions) | ⏳ |
| 6 | [Feature modes](#6-feature-modes) | ⏳ |
| 7 | [Emulation & test harness](#7-emulation--test-harness) | ⏳ |
| 8 | [Implementation](#8-implementation) | ⏳ |
| 9 | [On-hardware bring-up](#9-on-hardware-bring-up) | ⏳ |

---

## 1. Vision & scope

**🟡 Spec.** Bring the [Leshy2 hardware](https://github.com/anton-vinogradov/esp32-leshy2) to life in firmware: **port the mature esp32-leshy (S3) codebase** rather than rewrite it, grow it to drive the new radios, add a thin **ESP32-C5 5 GHz agent** behind a narrow **S3↔C5 protocol**, and implement the device's control conventions and its two safety blockers. The capability set is the one defined in the hardware repo's [stage 2](https://github.com/anton-vinogradov/esp32-leshy2#2-what-it-must-do--capabilities); nothing here promises radio behaviour the silicon can't do.

**In scope:** the S3 main firmware (UI, display + touch, all wired radios, buses, SD / PCAP, native 2.4 GHz Wi-Fi + BLE), the C5 5 GHz recon agent, the S3↔C5 link, per-region TX limits enforced in firmware, and an emulation / test harness that runs before hardware exists.

**Out of scope (same ceilings as the hardware):** full 5 GHz monitor + injection, WPA-handshake capture, Linux-class analytics, HF transmit, wideband SDR, cellular, and wideband jamming. See the hardware repo's [stage 1](https://github.com/anton-vinogradov/esp32-leshy2#1-why-a-new-device--vision) for why each is out.

**Decisions (locked coming in, from the hardware design's [Firmware stage](https://github.com/anton-vinogradov/esp32-leshy2#9-firmware)).**

- **Port the S3 leshy firmware, don't rewrite it.** Most of the S3 side already runs (UI, display, wired radios, buses, SD, 2.4 GHz Wi-Fi + BLE); reuse that lineage and grow the new peripherals around it instead of a clean-sheet start.
- **The C5 is a thin 5 GHz agent behind a narrow S3↔C5 protocol.** The S3 stays the brain and owns the UI; the C5 only does 5 GHz recon and answers a small command / event link over SPI3 + DRDY — the two codebases stay decoupled.
- **Orderly shutdown is a firmware feature, not the master switch.** The switch cuts the pack instantly, so an in-flight PCAP / log would corrupt; **OPTIONS → Shut down** (and a long-BACK) flushes SD, parks every radio, stops S3 + C5, then shows a "safe to flip" screen.
- **long-BACK / STOP kills all TX, over any screen.** One core handler — reached from the hardware STOP key or a long-BACK — stops every transmit chain without pulling power.
- **Long text is typed on a paired phone over BLE.** No room for an onboard keyboard; a BLE companion is the primary path, a Wi-Fi captive portal the fallback, the D-pad char-wheel the offline stopgap.

**Artifacts.** This README (the design). The firmware itself follows, stage by stage.

---

## 2. Target & toolchain

**⏳ Planned.** Choose the base framework — port esp32-leshy on **Arduino / PlatformIO** vs migrate to **ESP-IDF** — plus the dual-target build (S3 + C5), the repo layout, and CI. This is the first real fork, and it shapes everything downstream (including the [test harness](#7-emulation--test-harness)); it is weighed here with a steelman of each side before any code is written. *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

## 3. System architecture

**⏳ Planned.** The RTOS tasks and the dual-core split on the S3, the **S3↔C5 link protocol** (frame format, DRDY handshake, timeouts, loss handling), the top-level state machines, and the **HAL boundary** that lets each driver run against a test stub. *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

## 4. Peripheral & driver map

**⏳ Planned.** Every chip to a driver: 3× **nRF24L01+** (shared-CE modes — parallel RX scan, mousejack, simultaneous multi-channel TX), **CC1101** + SP4T band select, **SX1262** LoRa, **Si4732** RX, **SA868** walkie, **PCA9555** ×2, **74HC138**, **ST7796** + capacitive touch, microSD, u-blox **GPS**, **WS2812**, encoder + buttons. Each driver is defined against the HAL boundary from stage 3 so it can be tested without hardware. *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

## 5. UI/UX & control conventions

**⏳ Planned.** Menu and navigation, the D-pad + encoder + side buttons, the locked control conventions, the safety handlers (long-BACK stops all TX; clean shutdown), and BLE text entry. *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

## 6. Feature modes

**⏳ Planned.** Each capability as a mode: 2.4 GHz Wi-Fi (S3), 5 GHz recon (C5 agent), nRF24 scan / jam / mousejack, sub-GHz (CC1101), LoRa / Meshtastic (SX1262), FM / HF receive (Si4732), walkie (SA868), GPS, and PCAP logging — with the per-region TX caps enforced in firmware. *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

## 7. Emulation & test harness

**⏳ Planned.** Run the firmware on emulators before the board exists — **ESP-IDF Linux host-target + CMock** for drivers and the link protocol in CI, **Wokwi** for the UI and the buses (radios as behavioural custom chips), **Renode / QEMU** for boot and the two-node S3↔C5 link. Digital logic only; RF, analog, and power stay on hardware. This is the firmware half of the hardware repo's [emulation stage](https://github.com/anton-vinogradov/esp32-leshy2#10-firmware-validation-in-emulation). *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

## 8. Implementation

**⏳ Planned.** Build each module against the design above — driver by driver, mode by mode — each piece traceable to a decision in stages 2–7 and validated in the harness (stage 7) before it ever touches copper. *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

## 9. On-hardware bring-up

**⏳ Planned.** Flash the real board, bring up power / boot / the SPI3 link / each bus, prove the C5's 5 GHz, and tune. Ties into the hardware repo's [fabrication & bring-up](https://github.com/anton-vinogradov/esp32-leshy2#11-fabrication--bring-up). *Designed in the doc before it's implemented.*

**Decisions.** _TBD._

**Artifacts.** _TBD._

---

*Get involved: [CONTRIBUTING.md](CONTRIBUTING.md).*

## License

MIT — see [LICENSE](LICENSE). Same as upstream ESP32-DIV and the [Leshy2 hardware](https://github.com/anton-vinogradov/esp32-leshy2).
