# Прошивка Leshy2

> **Целевой документ продукта.** Страница описывает проверенное поведение ПО
> независимо от ещё не выбранной электронной архитектуры. Текущее состояние —
> в [current state](docs/status/current-state.ru.md).

- [English version](README.md)
- [Целевой hardware-продукт](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/README.ru.md)
- [Канонический межрепозиторный журнал](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review)

## Образ готового ПО

Firmware Leshy2 превращает будущую портативную hardware-платформу в автономный
all-in-one инструмент наблюдения, диагностики, связи, навигации, обслуживания
и разрешённых экспериментов. Hardware reachability не означает разрешение.

Compute count, target images, HAL ownership, IPC transports, pins и component
drivers открыты. Бывший three-domain `ARC-0001/PKG-0001/SYN-3A` после hardware
`DEC-0032` является только candidate study.

## Три уровня функциональности

1. **Основной режим** — повседневные инструменты, приём, диагностика,
   навигация, обслуживание и законная связь.
2. **Лаборатория** — пассивные, защитные и ограниченные security-инструменты.
3. **Лаборатория → Контролируемая зона** — dangerous active/disruptive tools.
   Каждый вход требует нового неснимаемого предупреждения, а каждое действие
   отдельно проверяет authorized target и/или isolated/conducted environment.

Выход, lock, timeout, reset, watchdog, update, STOP или потеря accessory
аннулируют affected arm/lease. Первичная установка отдельно требует принятия
акта о ненападении.

## Независимые от архитектуры software-контракты

- Каждый transmitter стартует выключенным после power/reset/brownout/watchdog/update.
- Первая TX использует консервативный per-path profile; максимум требует
  явного выбора текущего сценария и не восстанавливается как default.
- Commanded TX, observed current, device-reported TX и independent actual-TX
  evidence остаются разными состояниями.
- Physical STOP доминирует над UI/IPC/storage; отпускание не восстанавливает
  прежние target/channel/power/session.
- Каждый будущий physical radio owner локально обеспечивает timing, bounded
  queues, lease expiry и safe-off; IPC не становится remote raw GPIO.
- Штатные updates используют owner-authorized signed images, target validation
  и rollback. Keys, reproducible/offline build/signing и developer firmware
  остаются у владельца; irreversible lockdown optional и отделён.
- Каждый выбранный programmable target независимо recoverable/diagnosable без
  исправного peer или application image.
- Три полнофункциональных nRF24 сохраняют independent PTX/PRX, simultaneous RX
  и явные timestamp/drop/overflow evidence.
- Wi-Fi 2.4/5, IEEE 802.15.4, native BLE, packet Sub-GHz, analog voice,
  broadcast/audio, IR и qualified external GNSS/LoRa/NFC profiles сохраняют
  проверенные capability/safety boundaries.
- External iButton/1-Wire profile distinguishes ordinary owned devices, Lab
  credential reading and separately armed Controlled-Zone emulation/write;
  accessory presence never authorizes or auto-starts an operation.
- Unknown hardware/firmware/accessory identity видим и fails closed; firmware
  не включает скрытый permissive compatibility mode.

## Build boundary

Будущая architecture может породить один или несколько images. Обязателен
явный compatibility manifest с hardware/profile identities, protocol ranges,
hashes, rollback indices и migrations. Shared code может задавать policy
vocabulary/package formats/test vectors, но не стирает physical ownership или
safety boundaries.

## Состояние разработки

Firmware implementation не начата. Сначала закрывается current competitor
delta hardware G2; G3 product-design research может идти параллельно. Reviewed
hardware product design, несколько
whole-device alternatives, optimality, conceptual placement и новое atomic
architecture decision обязаны предшествовать target-specific runtime/HAL/
toolchain work. Бывший [`ARC-0001`](docs/architecture/ARC-0001-three-domain-runtime-contract.md)
сохранён только как candidate/reference evidence.
