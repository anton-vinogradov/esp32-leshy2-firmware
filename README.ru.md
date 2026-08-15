# Прошивка Leshy2

Проектирование прошивки начинается заново вместе с аппаратной частью Leshy2.

- Предыдущая документация сохранена в [`drafts/legacy-2026-08-15/`](drafts/legacy-2026-08-15/README.md) и не является канонической.
- Межрепозиторный журнал ревью ведётся в hardware-репозитории, в `docs/review/`.
- Архитектура прошивки, toolchain, протокол, структура каталогов и набор функций не считаются принятыми до ревью соответствующего этапа.
- Принят all-in-one профиль: security-функции идут от простых к наиболее серьёзным и находятся только в разделе **«Лаборатория»**; при первичной установке обязателен акт о ненападении. Каноническое решение — [`DEC-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0002-project-vision.md).
- Принят безопасный TX-дефолт: все передатчики стартуют выключенными, Lab-инструменты разоружены, первая передача использует консервативный профиль, а максимум требует явного выбора. Каноническое решение — [`DEC-0003`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0003-safe-tx-defaults.md).
- Для трёх nRF24 и IR принято только **целевое требование владения C5**, а не готовая архитектура. Его реализуемость не подтверждена: legacy-топология требует от единственного GP-SPI C5 одновременно ролей nRF-master и S3↔C5 slave. Блокер зафиксирован в [`FND-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0001-c5-single-gp-spi.md).
- Legacy-возможности сведены в [`INV-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/inventories/INV-0001-legacy-capabilities.md) только как кандидаты. Инвентаризация выявила неопределённого владельца BLE ([`FND-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0002-ble-owner-conflict.md)) и отсутствие MCU audio-path для обещанных цифровых audio-функций ([`FND-0003`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/findings/FND-0003-missing-mcu-audio-path.md)).
- По [`DEC-0004`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0004-reconsider-legacy-exclusions.md) все отвергнутые legacy-возможности проходят повторную техническую и правовую проверку; ограничение старого компонента больше не считается ограничением продукта.
- По [`DEC-0005`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0005-zero-loss-cost.md) полная стоимость продукта снижается только через доказанно эквивалентные реализации без потери функций, характеристик, безопасности, надёжности, автономности, ремонтопригодности и тестируемости.
- По [`DEC-0006`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0006-external-m5-gnss.md) бортовой GNSS удалён из базовой платы. GPS-функции условны внешним M5Stack Unit GPS v1.1 через отдельный защищённый 5-вольтовый UART Grove-порт; `FND-0004` закрыта.
- По [`DEC-0007`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0007-dual-external-lora-profiles.md) бортовой LoRa удалён из базовой платы и приняты оба внешних профиля через единый `EXT-RF14`: M5Stack U214 LoRa+GNSS Cap и сменная широкополосная LoRa-carrier с обязательным reference-вариантом E22-900M22S на 850–930 МГц. Одновременно активны один LoRa backend и один GNSS backend.

Текущий статус реализации: **не начато**.

*English version: [README.md](README.md).*
