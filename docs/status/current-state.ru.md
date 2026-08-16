# Прошивка Leshy2 — текущее состояние проработки

> Снимок: 2026-08-17. Образ software — в [target README](../../README.ru.md).
> Канонические decisions — в [hardware review ledger](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review).

## Текущая зрелость

- Firmware implementation: **не начата**.
- Product behavior/safety requirements: 125 leaves и competitor delta прошли
  повторное hardware G2 review (`REV-0002AS`).
- `W-EXTRA-11` закрыт external iButton profile `DEC-0033/REQ-IBTN-0001`;
  `DEC-0034/REQ-EXT-0001` принимает M5-first Unit/Cap, отдельный
  high-throughput tier и отсутствие native M5-Bus. `DEC-0039/REQ-SCOPE-0001`
  позже удаляют former FIDO target и reject generic USB host, сохраняя transport,
  выведенный конкретным RF/SDR profile. `AUD-0007` проверил haptic;
  `DEC-0036/REV-0002AJ` исключают product haptic, мотор и dedicated external
  profile. `AUD-0008/DEC-0037/REQ-IMU-0001/REV-0002AL` принимают optional
  external measurement-pose profile. `AUD-0009/REV-0002AM` завершили fact
  review physical-keyboard archetype; `DEC-0038/REV-0002AN` закрывают его как
  no integrated keyboard плюс bounded phone-assisted text. `AUD-0010/0011` и
  `REV-0002AP` завершают scope propagation. `AUD-0012/REV-0002AQ` проверяют
  факты 6 GHz/Wi-Fi 6E; `DEC-0040/REV-0002AR` полностью отклоняют его.
  `REV-0002AS` закрывает repeat G2; hardware `DEC-0041` вводит G2F logical/
  electrical feasibility до физического макета. Hardware `DEC-0042/REV-0003Y`
  проверяют единый exact-device/net source и две structurally checked draft-карты.
- Target-specific firmware architecture: **переоткрыта/не выбрана**.
- Бывший three-domain `ARC-0001`: candidate/reference only.
- Следующий upstream gate: hardware закрывает exact peripherals, controller
  concurrency, timing, power/service и HIL двух draft-карт `G2F-2R/G2F-3D`.
  Их machine-checked GPIO accounting — evidence, а не owner/architecture
  decision. `LAY-0001` P1/P2/P3 — reference; chip, owner, bus и pin не
  зафиксированы.

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
  iButton read/emulate/write level separation; two-tier expansion без blanket
  M5-Bus и без подмены raw-data path низкоскоростным command link.
- radio/key mission boundary; optional BadUSB — software-only Controlled-Zone
  exception поверх existing USB-device path и не блокирует core release.

## Отменённые target assumptions

S3/C5/RP ownership, exact variants, три images, 1-bit SDIO, SPI+alert, exact
pins, memory budgets и three-USB/DBG10 implementation нельзя потреблять как
final firmware prerequisites. Это только candidate evidence.

## Следующее firmware-действие

Target code/toolchain пока не создаются. Hardware сначала квалифицирует и
проверяет одну рабочую G2F-карту, затем адаптирует legacy physical mockup и проходит whole-device
optimality/conceptual placement/atomic architecture. После этого firmware
заново выведет image/owner/IPC/HAL/update/test contract и начнёт implementation.
