# Прошивка Leshy2

> **Целевой документ продукта.** Страница описывает проверенное поведение ПО
> независимо от ещё не выбранной электронной архитектуры. Текущее состояние —
> в [current state](docs/status/current-state.ru.md).

- [English version](README.md)
- [Целевой hardware-продукт](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/README.ru.md)
- [Канонический межрепозиторный журнал](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review)

## Образ готового ПО

Firmware Leshy2 превращает будущую portable hardware-платформу в автономный
all-in-one radio/wireless инструмент связи, наблюдения, диагностики и
разрешённых исследований, включая wireless/contact credential tools.
Навигация, storage, maintenance и compute поддерживают эти результаты, а не
образуют general-purpose peripheral-computer scope. Hardware reachability не
означает разрешение.

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
- Три полнофункциональных nRF24 сохраняют independent PTX/PRX и поддерживают
  любой одновременный mix `3R/1T2R/2T1R/3T` без automatic peer standby или
  скрытых RX gaps; exact mixed-RF sensitivity остаётся measured profile gate.
- Wi-Fi 2.4/5, IEEE 802.15.4, native BLE, packet Sub-GHz, analog voice,
  broadcast/audio, IR и qualified external GNSS/LoRa/NFC profiles сохраняют
  проверенные capability/safety boundaries.
- External iButton/1-Wire profile distinguishes ordinary owned devices, Lab
  credential reading and separately armed Controlled-Zone emulation/write;
  accessory presence never authorizes or auto-starts an operation.
- Accessory manager считает M5 Unit A/B/C/custom и полный U214-compatible Cap
  основным low-rate tier, а принятые raw SDR и external RF/credential-analysis
  workloads могут вывести отдельный high-throughput tier. Он не объявляет
  generic host или blanket M5-Bus compatibility и не выдаёт command link за
  raw-data path.
- Unknown hardware/firmware/accessory identity видим и fails closed; firmware
  не включает скрытый permissive compatibility mode.
- В base нет постоянной text keyboard. Заявленный редкий/длинный text workflow
  может использовать локально сопряжённый owner phone с authenticated, visible
  и revocable session. Входной текст и последствия показываются на Leshy2;
  телефон не принимает pledge, не входит в Controlled Zone, не arm/confirm TX
  или destructive actions и не меняет trust/recovery authorization.
- Renderer использует dirty/tiled preemptible updates, а не video-like
  full-frame target. Critical state и первый menu feedback видимы за `≤100 ms`
  при admitted concurrent load; waterfall coalescing/drop явно учитывается и
  никогда молча не обменивается на потерю raw radio/audio capture.
- Optional external IMU profile записывает timestamped raw accel/gyro,
  pitch/roll, short-term relative rotation и motion quality только при
  qualified indexed mount/axis transform. Missing/stale IMU invalidates pose
  metadata, но не raw RF records или safety; six-axis не называется absolute
  heading или RF bearing.
- Generic USB host, personal FIDO/U2F authentication и 6 GHz/Wi-Fi 6E находятся
  вне product mission. High-throughput transport появляется только из
  конкретного принятого RF/SDR profile.
- BadUSB/DuckyScript — release-optional Controlled-Zone software exception
  поверх существующего USB device/service path. Он не добавляет hardware/
  architecture requirement и не блокирует radio/key release, но до поставки
  требует fresh authorization, isolated execution, parser/USB review и HIL.

## Build boundary

Будущая architecture может породить один или несколько images. Обязателен
явный compatibility manifest с hardware/profile identities, protocol ranges,
hashes, rollback indices и migrations. Shared code может задавать policy
vocabulary/package formats/test vectors, но не стирает physical ownership или
safety boundaries.

## Состояние разработки

Firmware implementation не начата. Повторное hardware G2 review закрыто;
hardware `DEC-0044/NIF-0001/REV-0004L` выбрали `G2F-3I` ведущей reviewed paper
map с независимыми radio buses/IPC и bounded display+SD sharing. Hardware
`DEC-0045/0046` дополнительно требуют одну active top-level signal group,
three-radio `SG-N24` full mix и verified quiet states всех неиспользуемых
interfaces. `DEC-0047/N24H-0001` используют второй device как reversible HIL
observer/peer qualified internal RF envelope, а не как зависимость base
product. Firmware consequences записаны в
[`ARC-0002`](docs/architecture/ARC-0002-g2f-3i-runtime-input.md), но physical
RF, exact peripherals, power и HIL должны закрыться до адаптированного legacy
physical mockup. Physical co-design, whole-device optimality, conceptual
placement и новое atomic architecture decision обязаны предшествовать
target-specific runtime/HAL/toolchain work. Бывший
[`ARC-0001`](docs/architecture/ARC-0001-three-domain-runtime-contract.md)
сохранён только как candidate/reference evidence.
