# Прошивка Leshy2 — текущее состояние проработки

> Снимок: 2026-08-16. Образ software — в [target README](../../README.ru.md).
> Канонические decisions — в [hardware review ledger](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review).

## Текущая зрелость

- Firmware implementation: **не начата**.
- Product behavior/safety requirements: прежние 125 leaves проверены; hardware
  G2 точечно переоткрыт для current competitor delta (`FND-0040/AUD-0004`).
- `W-EXTRA-11` закрыт external iButton profile `DEC-0033/REQ-IBTN-0001`;
  `AUD-0005` провёл ревью M5 coverage, а `IMP-0028` M5-first/high-speed boundary
  требует решения владельца.
- Target-specific firmware architecture: **переоткрыта/не выбрана**.
- Бывший three-domain `ARC-0001`: candidate/reference only.
- Следующий upstream gate: закрытие hardware G2 delta; G3 product-design
  research идёт параллельно без final review.

Hardware `FND-0039` обнаружил, что прежний процесс выбрал `SYN-3A`, exact
owners и CAD до product design, whole-product optimality и conceptual
placement. Владелец выбрал reopen option A в hardware `DEC-0032`.

## Действующие входы

- Main/Lab/Controlled Zone и non-aggression onboarding;
- консервативные TX defaults, hard STOP, отсутствие automatic re-arm и
  отдельное actual-TX evidence;
- полные capability/concurrency/failure requirements;
- owner-controlled signed updates, rollback и independent physical recovery/
  diagnostics каждого в итоге выбранного programmable target;
- no-loss cost и явные mismatch/proposal review rules;
- qualified accessory manifests, default-off unknown M5 profiles and external
  iButton read/emulate/write level separation.

## Отменённые target assumptions

S3/C5/RP ownership, exact variants, три images, 1-bit SDIO, SPI+alert, exact
pins, memory budgets и three-USB/DBG10 implementation нельзя потреблять как
final firmware prerequisites. Это только candidate evidence.

## Следующее firmware-действие

Target code/toolchain пока не создаются. После нового hardware G2 review,
hardware product design,
whole-device candidates, optimality, conceptual placement и atomic architecture
firmware заново выведет image/owner/IPC/HAL/update/test contract, проверит его
и только потом начнёт implementation.
