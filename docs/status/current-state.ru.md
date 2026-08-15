# Прошивка Leshy2 — текущее состояние проработки

> Снимок: 2026-08-16. Эта страница описывает, что доказано сейчас. Образ готового ПО находится в [целевом firmware README](../../README.ru.md), а готового устройства — в [целевом hardware README](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/README.ru.md).

- Канонические доказательства: [hardware-журнал ревью](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review)
- English version: [current-state.md](current-state.md)
- Legacy только для справки: [`drafts/legacy-2026-08-15/`](../../drafts/legacy-2026-08-15/README.md)

## Ход ревью и реализации

| Слой | Состояние |
|---|---|
| Межрепозиторные этапы 0–1 | Проведено ревью |
| Этап 2: возможности и исключения | В работе |
| Этапы 3–6: от архитектуры до проверки hardware | Не начато |
| Этап 7: проектирование firmware | Не начато |
| Этап 8: UI, safety и legal controls | Не начато |
| Реализация firmware | Не начата |

Каноническая таблица стадий — [`docs/review/stages.md`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/stages.md). Архитектура прошивки, toolchain, протокол, структура каталогов и реализация пока не приняты.

## Принятые целевые ограничения

- all-in-one профиль, акт о ненападении при установке и три уровня функциональности (`DEC-0002`, `DEC-0010`);
- консервативные TX-дефолты и явный выбор максимальной доступной мощности (`DEC-0003`);
- повторная проверка технически и юридически допустимых legacy-исключений (`DEC-0004`);
- снижение стоимости только с доказательством отсутствия потерь продукта (`DEC-0005`);
- внешний M5 GNSS и внешний U214 LoRa+GNSS (`DEC-0006`, `DEC-0008`);
- NMEA baseline и условный per-revision advanced CASIC profile без дополнительного GNSS (`DEC-0014`);
- бортовой mono ES8311 audio с аппаратным default-to-analog bypass (`DEC-0009`);
- целевое владение C5 для 3×nRF24 и IR (`DEC-0001`) без заявления, что межпроцессорный транспорт уже решён.
- owner-controlled подписанные обновления S3/C5 с rollback и открытым developer lifecycle (`DEC-0013`) без включения необратимого hardware lockdown.

## Открытые инженерные зависимости

- `FND-0001`: единственный general-purpose SPI C5 не может одновременно выполнять legacy-роли nRF-master и S3↔C5-slave.
- `FND-0002`: владелец BLE расходится между legacy-репозиториями.
- `FND-0003`: audio-направление принято, но pins, electrical behavior, drivers, HIL и feature-level gates ещё не доказаны.
- `FND-0006`: предложенная матрица кнопок и принятые audio-control конфликтуют на `U13.P10..P17`.
- `FND-0007`: текущий STOP — только вход I²C-экспандера и не может независимо погасить TX.
- Legacy-документы и кандидаты source code firmware неканоничны до ревью производящих стадий.

## Текущая работа ревью

System/UI/storage capability-срез завершён статусом **«Проведено ревью»** в `REV-0002I`.

GNSS/navigation срез [`REQ-GNSS-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/requirements/REQ-GNSS-0001-navigation-integrity.md) получил статус **«Проведено ревью»** в `REV-0002K`. Владелец принял `IMP-0012/A` как [`DEC-0014`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0014-casic-gnss-profile.md): NMEA — обязательный baseline квалифицированного профиля, а assistance и receiver-reported jamming/spoofing условны proof точной revision/firmware. Unsupported/timeout/parser error означают `unknown`, не «угроз нет»; host heuristics отделяются от статуса receiver.

`FND-0009` закрыт на requirement-level. UART/power hardware, parser, assistance source, поддержка advanced messages конкретными Unit/U214, RF self-desense и HIL ещё не реализованы и проверяются на последующих этапах.

## Отложенный архитектурный gate

[`IMP-0010`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/improvements/IMP-0010-hardware-stop-and-expander-consolidation.md) остаётся открытым, но [`DEC-0012`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0012-defer-imp-0010-to-pin-budget.md) переносит выбор A/B на этап 3. Новый ответ владельца не запрашивается, пока сводный pin/GPIO/resource budget не учтёт оба MCU, экспандеры, fixed-function pins, межпроцессорный transport, audio, UI/touch, внешние модули и действительно освободившиеся линии onboard GNSS/LoRa.

`FND-0006` и `FND-0007` остаются открытыми. Перенос не выбирает `U14`/матрицу 3×3 и не доказывает аппаратный STOP.
