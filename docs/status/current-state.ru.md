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
- бортовой mono ES8311 audio с аппаратным default-to-analog bypass (`DEC-0009`);
- целевое владение C5 для 3×nRF24 и IR (`DEC-0001`) без заявления, что межпроцессорный транспорт уже решён.

## Открытые инженерные зависимости

- `FND-0001`: единственный general-purpose SPI C5 не может одновременно выполнять legacy-роли nRF-master и S3↔C5-slave.
- `FND-0002`: владелец BLE расходится между legacy-репозиториями.
- `FND-0003`: audio-направление принято, но pins, electrical behavior, drivers, HIL и feature-level gates ещё не доказаны.
- `FND-0006`: предложенная матрица кнопок и принятые audio-control конфликтуют на `U13.P10..P17`.
- `FND-0007`: текущий STOP — только вход I²C-экспандера и не может независимо погасить TX.
- Legacy-документы и кандидаты source code firmware неканоничны до ревью производящих стадий.

## Текущий decision gate

[`IMP-0010`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/improvements/IMP-0010-hardware-stop-and-expander-consolidation.md) ждёт решения владельца:

- рекомендуемый A: независимый hardware STOP, безопасная перезагрузка, матрица 3×3, удаление `U14` и использование освобождённых LoRa-control pins для audio;
- B: сохранить `U14` и point-to-point кнопки, но всё равно добавить независимый hardware STOP.

System/UI-подэтап не получает статус **«Проведено ревью»**, пока выбор не принят и не распространён.
