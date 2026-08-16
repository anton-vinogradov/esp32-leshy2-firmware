# Leshy2 Firmware — current engineering state

> Snapshot: 2026-08-17. Intended software behavior is in the
> [target README](../../README.md). Canonical decisions live in the
> [hardware review ledger](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review).

## Current maturity

- Firmware implementation: **not started**.
- Product behavior/safety requirements: the 125 leaves and competitor delta
  have received repeated hardware G2 review (`REV-0002AS`).
- `W-EXTRA-11` is closed by external iButton profile
  `DEC-0033/REQ-IBTN-0001`; `DEC-0034/REQ-EXT-0001` accepts M5-first Unit/Cap,
  a separate high-throughput tier and no native M5-Bus. `DEC-0039/REQ-SCOPE-0001`
  later remove the former FIDO target and reject generic USB host while keeping
  transport derived by a concrete RF/SDR profile. `AUD-0007` reviewed haptic;
  `DEC-0036/REV-0002AJ` reject product haptic, motor and a dedicated external
  profile. `AUD-0008/DEC-0037/REQ-IMU-0001/REV-0002AL` accept the optional
  external measurement-pose profile. `AUD-0009/REV-0002AM` complete the
  physical-keyboard archetype fact review; `DEC-0038/REV-0002AN` close it as
  no integrated keyboard plus bounded phone-assisted text. `AUD-0010/0011` and
  `REV-0002AP` complete the scope propagation. `AUD-0012/REV-0002AQ` review
  6 GHz/Wi-Fi 6E facts; `DEC-0040/REV-0002AR` fully reject it. Repeated G2 is
  closed by `REV-0002AS`; hardware `DEC-0041` inserts G2F logical/electrical
  feasibility before the physical mockup.
- Target-specific firmware architecture: **reopened/not selected**.
- Former `ARC-0001` three-domain contract: candidate/reference only.
- Next upstream gate: hardware builds at least two complete owner/bus/GPIO maps
  from `DEM-0001/SRC-0002`, checking SoC→package→exact device/module→actual
  exposed contact. `LAY-0001` P1/P2/P3 is reference-only; no chip, owner, bus
  or pin is fixed.

Hardware `FND-0039` found that the prior process selected `SYN-3A`, exact owners
and CAD before product design, whole-product optimality and conceptual
placement. The owner chose reopen option A in hardware `DEC-0032`.

## Valid inputs

- Main/Lab/Controlled-Zone behavior and non-aggression onboarding;
- conservative TX defaults, hard STOP, no automatic re-arm and distinct
  actual-TX evidence;
- complete capability/concurrency/failure requirements;
- owner-controlled signed updates, rollback and independent physical recovery/
  diagnostics for every eventually selected programmable target;
- no-loss cost and explicit mismatch/proposal review rules;
- qualified accessory manifests, default-off unknown M5 profiles and separate
  level gates for external iButton read/emulate/write; two-tier expansion with
  no blanket M5-Bus or low-rate/raw-data equivalence claim.
- radio/key mission boundary; optional BadUSB is a software-only Controlled-Zone
  exception over the existing USB-device path and cannot block core release.

## Invalidated target assumptions

S3/C5/RP ownership, exact variants, three images, 1-bit SDIO, SPI+alert, exact
pins, memory budgets and three-USB/DBG10 implementation cannot be consumed as
final firmware prerequisites. They remain useful candidate evidence only.

## Next firmware action

No target code or toolchain is created yet. Hardware first completes G2F maps,
then adapts the legacy physical mockup and completes whole-device optimality,
conceptual placement and atomic architecture. Firmware will then derive and
review the new image/owner/IPC/HAL/update/test contract before implementation.
