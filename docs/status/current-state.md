# Leshy2 Firmware — current engineering state

> Snapshot: 2026-08-16. Intended software behavior is in the
> [target README](../../README.md). Canonical decisions live in the
> [hardware review ledger](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review).

## Current maturity

- Firmware implementation: **not started**.
- Product behavior/safety requirements: reviewed at hardware stages 1–2.
- Target-specific firmware architecture: **reopened/not selected**.
- Former `ARC-0001` three-domain contract: candidate/reference only.
- Next upstream gate: hardware target physical/product design.

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
- no-loss cost and explicit mismatch/proposal review rules.

## Invalidated target assumptions

S3/C5/RP ownership, exact variants, three images, 1-bit SDIO, SPI+alert, exact
pins, memory budgets and three-USB/DBG10 implementation cannot be consumed as
final firmware prerequisites. They remain useful candidate evidence only.

## Next firmware action

No target code or toolchain is created yet. After hardware product design,
whole-device candidates, optimality, conceptual placement and atomic
architecture are reviewed, firmware will derive the new image/owner/IPC/HAL/
update/test contract and review it before implementation.
