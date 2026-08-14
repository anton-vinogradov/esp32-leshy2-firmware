# Contributing to Leshy2 Firmware

*Read this in another language: [Русский](CONTRIBUTING.ru.md)*

## Welcome

This is the **firmware** for [Leshy2](https://github.com/anton-vinogradov/esp32-leshy2), an open, two-chip (ESP32-S3 + ESP32-C5) multiband RF handheld. It is ported from the [esp32-leshy](https://github.com/anton-vinogradov/esp32-leshy) codebase (itself a fork of [ESP32-DIV](https://github.com/cifertech/ESP32-DIV)). We are at the **design stage**: nothing is implemented yet, so this is a great time to shape it.

Collaboration is very welcome — **especially from the ESP32-DIV community**. You do not need to be an RF expert to help; there is room for firmware people, driver writers, testers, and doc writers.

## How we work — design first, then build

The [README](README.md) is the **source of truth**. We **design each stage in the doc before writing the code**: a stage sets a *Spec*, records its *Decisions*, and only then produces *Artifacts* (code + docs) that implement that design. So the best first step is to read the README pipeline.

- **Propose in the doc.** If you want to change how something works, propose the **decision** first (a PR to the README stage, or a Discussion). Code follows an agreed design.
- **Trace code to a decision.** Every module should map back to a stage decision. If there is no decision yet, that stage is still open — help design it.
- **Test before hardware.** The firmware is built to run in emulation ([stage 7](README.md#7-emulation--test-harness)) so logic, drivers, and the S3↔C5 protocol can be validated without a board. New code should come with host tests where it can.

## Ways to help

- **Firmware & drivers.** Port the S3 leshy code, write the C5 5 GHz agent, and the S3↔C5 link protocol. Drivers: 3× nRF24L01+, CC1101 (+ SP4T band select), SX1262, Si4732, SA868-U, u-blox GPS, ST7796 + touch, microSD.
- **Emulation & CI.** Help stand up the host-target + Wokwi + Renode harness so firmware runs before the board exists.
- **Testing.** Once there is hardware, build it, run it, and report what works and what does not. Clear bug reports are gold.
- **Docs & translations.** Improve the design docs; help translate them so more people can join.

## How we discuss

- **GitHub Discussions** for ideas, design questions, and open talk.
- **GitHub Issues** for bugs and concrete tasks — include steps, expected result, and what you saw.

Keep it in the open when you can, so others can learn and join in.

## Licensing

Leshy2 firmware is **MIT licensed**, the same as upstream ESP32-DIV. By sending a contribution (code, docs, or other work), you agree that it is licensed under **MIT**. Please only submit work you have the right to share.

## Ground rules

- **Be respectful.** Be kind and patient. We are all here to learn and build.
- **Keep RF legal — in firmware.** No wideband jamming; it is illegal (US Communications Act section 333; EU RED). Honor the power and duty-cycle caps enforced per region **in the firmware itself**, for example: LoRa EU433 +10 dBm, EU868 +14 dBm, the 869.4–869.65 MHz sub-band +27 dBm at 10% duty cycle, US915 +30 dBm with frequency hopping. SA868 TX is region / licence limited (446 PMR max 0.5 W ERP; 5 W only on ham 70 cm with a licence).
- **Do not add or ask for features that break these rules**, or that remove the safety handlers (all-TX stop, orderly shutdown).

Thank you for helping build Leshy2 in the open.
