# Прошивка Leshy2

> **Целевой документ продукта.** Эта страница собирается из принятых и проверенных решений и описывает будущее готовое ПО, а не текущую реализацию. Зрелость, блокеры и открытые предложения находятся в [текущем состоянии проработки](docs/status/current-state.ru.md).

- [English version](README.md)
- [Целевой документ hardware](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/README.ru.md)
- [Канонический межрепозиторный журнал ревью](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review)

## Целевое готовое ПО

Прошивка Leshy2 превращает портативную двухпроцессорную платформу в автономный all-in-one полевой инструмент для наблюдения, диагностики, связи, навигации, обслуживания и разрешённых экспериментов. Возможности открываются через явные эксплуатационные и safety-контракты: техническая доступность hardware сама по себе не означает разрешение на действие.

## Три уровня функциональности

1. **Основной режим** — повседневные инструменты, приём, диагностика, навигация, обслуживание и законная связь вне security-сценария.
2. **Лаборатория** — пассивные, защитные и ограниченные инструменты исследования безопасности.
3. **Лаборатория → Контролируемая зона** — действительно опасные active/disruptive инструменты. Каждый вход требует нового неснимаемого предупреждения и hold-to-confirm, а конкретная функция — изолированной среды, явно авторизованной цели либо обоих оснований.

После входа каждый инструмент третьего уровня остаётся отдельно разоружённым и применяет собственные target-, environment-, frequency-, power-, duty-, destructive-action- и STOP-гейты. Выход из раздела, reset, watchdog, блокировка устройства, session timeout, STOP или потеря требуемого аксессуара разоружают уровень; при новом входе banner обязателен снова. Канонический контракт — [`DEC-0010`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0010-three-functional-levels.md).

## Первичная установка и безопасная передача

- При первичной установке пользователь явно принимает акт о ненападении. Это отдельный первый гейт, который не заменяет технические interlock и применимое право.
- После power-on, reset, brownout, watchdog или обновления все передатчики выключены; каждый Lab-инструмент разоружён.
- Первая передача использует консервативный профиль конкретного радиотракта. Максимальная доступная мощность требует явного действия для текущего сценария и никогда не восстанавливается как общий дефолт.
- Активный TX и выбранная мощность видимы пользователю. Сохранённая настройка или восстановленный экран не могут скрытно вооружить передачу.
- Штатные пути обновления S3/C5 требуют owner-authorized подписанных образов, независимой проверки целевым MCU и rollback на рабочий image. Ключи, offline build/signing tools и собственная developer firmware остаются под контролем владельца; hardware Secure Boot, Flash Encryption и eFuse lockdown требуют отдельного добровольного решения после recovery proof ([`DEC-0013`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0013-owner-controlled-signed-updates.md)).

## Принятая интеграция устройства

- ESP32-C5 — целевой владелец всех трёх nRF24 и IR TX/RX; прошивка использует финальный транспорт только после принятия его архитектуры и аппаратного доказательства.
- Три тракта nRF24 дают одновременное измерение энергии 2.4 ГГц и калиброванное сравнение секторов по бинарной доле RPD. Записи сохраняют sampling и calibration state; UI/exports никогда не выдумывают RSSI/dBm, пеленг, угол или VSWR. Пассивный ESB discovery относится к «Лаборатории», активная проверка одной авторизованной цели — к «Контролируемой зоне», а interference/carrier tests требуют одновременно разрешения и проводной либо RF-экранированной среды ([`DEC-0019`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0019-calibrated-rpd-three-antenna-hunt.md)).
- Навигация поддерживает внешний M5Stack Unit GPS v1.1 и GNSS-backend квалифицированного комбинированного расширения; одновременно активен только один GNSS-backend. NMEA-навигация является baseline, а assistance и receiver-reported помехи/подмена доступны только для доказанной revision/firmware. Unsupported, timeout и parser error дают `unknown`, никогда не ложное «угроз нет»; host heuristics показываются отдельно ([`DEC-0014`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0014-casic-gnss-profile.md)).
- LoRa поддерживает M5Stack U214 как первый backend `EXT-RF14` для общепринятых профилей 868/915 в пределах модуля и региональных правил; одновременно активен только один LoRa-backend.
- Бортовой mono-тракт ES8311 даёт prerequisite для цифровых capture, playback, routing и level control, а обычное прослушивание и голос через микрофон сохраняют аппаратный default-to-analog путь при reset или failure MCU либо codec.
- Бортовой Si4732 даёт FM/RDS и обычный приём LW/MW/SW. SSB USB/LSB и CW через BFO доступны после локального импорта владельцем совместимого volatile patch через открытый bounded loader; сторонний blob не входит в release без доказанных provenance и права распространения. Synchronous-AM не обещается до отдельного proof ([`DEC-0015`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0015-open-si4732-ssb-patch-loader.md)).
- Предпочтительный voice-radio backend — half-duplex analog-FM SA518 с VHF 136–174 и UHF 400–470 МГц, 0.5/1 W и явными региональными/licence-профилями. До проверки цены, поставки и RF сохраняется UHF-only SA868S fallback; он никогда не называется dual-band. Падение пика 2 W-class→1 W принято ради одного VHF+UHF модуля, а внешний SMA не выдаётся за licence-exempt PMR446 ([`DEC-0016`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0016-conditional-sa518-dual-band-voice.md)).
- HF NFC/RFID использует внешний M5 Unit NFC U216 через квалифицированный 5-вольтовый `PORT.A-NFC`; обычная работа с NFC-A/B/F/V метками находится в основном режиме. Анализ credentials относится к «Лаборатории», а recovery, credential write/clone, emulation и relay с двумя frontend — к «Контролируемой зоне» и требуют авторизованной цели. RFID2 остаётся limited compatibility, custom PN7160 — только fallback при провале qualification. Поддержка зависит от проверки точной revision/lifecycle U216; universal clone, payment compliance и LF 125 kHz не обещаются ([`DEC-0017`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0017-u216-hf-nfc-backend.md)).
- Consumer IR использует два приёмных тракта C5: TSOP38238 для надёжного demodulated 38 kHz приёма и TSMP95000 для обучения с измерением несущей 30–60 kHz; TSAL6200 — первый условный кандидат 940 nm emitter. Provenance несущей сохраняется в typed records. Пульт/replay собственного устройства находится в основном режиме, пассивный анализ — в «Лаборатории», unknown/security replay требует авторизованной цели в «Контролируемой зоне», а disruptive multi-code sweep — одновременно изоляции и авторизации. Автоматическое обучение 455 kHz/out-of-band отложено ([`DEC-0018`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0018-dual-path-consumer-ir.md)).

## Как развивается эта страница

Здесь кратко отражаются только принятые продуктовые контракты. Открытые находки, зрелость реализации и непринятые предложения остаются в [текущем состоянии](docs/status/current-state.ru.md) и hardware-журнале ревью. По мере появления проверенных `REQ-*` и архитектурных артефактов эта страница станет полным стартовым документом готового firmware-продукта.
