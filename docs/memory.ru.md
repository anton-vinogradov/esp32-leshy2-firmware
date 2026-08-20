# Память, обновление и восстановление прошивки

[На главную](../README.ru.md) · [English](memory.md) · [Runtime-архитектура](architecture.ru.md) · [Аппаратные линии памяти](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/memory.ru.md)

Каждый физический контроллер владеет своим образом, inactive slot, boot health
и путём восстановления. Пользователь всё равно устанавливает один product
bundle: общий manifest не позволяет активировать новый образ одного домена
рядом с несовместимыми peer.

## Ёмкость всех доменов

| Образ | Точное устройство | Оперативная память | Хранилище кода | Разметка rollback |
|---|---|---:|---:|---:|
| S3 | `ESP32-S3-WROOM-1U-N16R8` | 8 МиБ octal PSRAM с ECC | 16 МиБ flash | два OTA slot по 7 МиБ; предел образа 6,75 МиБ |
| C5 | `ESP32-C5-WROOM-1U-N8R8` | 8 МиБ PSRAM | 8 МиБ flash | два OTA slot по 3,5 МиБ; предел 3,375 МиБ |
| RP | `SC1512-A4` (`RP2354B`) | 520 КиБ on-chip SRAM | 2 МиБ stacked flash | нативная A/B-пара по 896 КиБ; предел 864 КиБ |
| Pack | `MSPM0C1106SDGS20R` | 8 КиБ SRAM | 64 КиБ flash | protected 16 КиБ + A 22 КиБ + B 22 КиБ + state 4 КиБ |
| Safety | второй `MSPM0C1106SDGS20R` | 8 КиБ SRAM | 64 КиБ flash | независимая разметка 16/22/22/4 КиБ |

[`tools/check_image_size.py`](../tools/check_image_size.py) читает JSON-лимит
target и возвращает `ok`, `warning` или `reject`. Новая функция не может
незаметно занять второй slot.

## Один подписанный bundle

Машинный контракт находится в
[`config/update_policy.json`](../config/update_policy.json). Manifest связывает
hash каждого образа с Leshy2, диапазоном аппаратных ревизий, физическим target,
build ID и совместимостью протоколов. Штатная установка принимает release root
или локально добавленный owner root. Для общей подписи package выбран ECDSA
P-256 поверх SHA-256; выпуск заблокирован, пока полный verifier не помещён в
C1106 и не прошёл fault injection.

Update требует физического `RUN=KILL`, отсутствия actual-TX evidence и
стабильного допущенного питания. Сначала все inactive images записываются и
проверяются чтением. Pack, Safety, C5 и RP загружаются pending, не уничтожая
старые образы. S3 запускается последним и должен увидеть ожидаемые build ID и
локальные self-test четырёх peer в пределах окна RP2350 TBYB. Только после
этого выдаётся global commit. Crash, timeout, неверный target, плохая подпись,
несовместимый протокол или отсутствие подтверждения возвращают все pending
домены к предыдущим образам.

Так защищается штатный update path без закрытия устройства. По умолчанию не
прожигаются необратимые secure-boot, anti-rollback или debug lock. Человек с
физическим доступом к flash/debug может осознанно заменить прошивку и ключи:
это граница восстановления владельца, а не удалённый update path.

## S3: flash 16 МиБ и PSRAM с ECC

Оба application slot имеют размер 7 МиБ. CI предупреждает после 6 МиБ и
отвергает образ больше `0x6C0000`, оставляя по 256 КиБ на рост, выравнивание и
подписанные metadata.

| Partition | Offset | Size | Назначение |
|---|---:|---:|---|
| bootloader + table | `0x000000` | до `0x009000` | ROM/second-stage boot и таблица |
| `nvs` | `0x009000` | `0x006000` | ограниченные настройки и калибровка |
| `otadata` | `0x00F000` | `0x002000` | дублированное active/pending/rollback state |
| `phy_init` | `0x011000` | `0x001000` | начальная radio calibration |
| `coredump` | `0x012000` | `0x010000` | ограниченная запись crash |
| `nvs_keys` | `0x022000` | `0x003000` | ключи encrypted NVS |
| boot reserve | `0x025000` | `0x00B000` | запас boot/security, не product assets |
| `ota_0` | `0x030000` | `0x700000` | running/last-known-good S3 image |
| `ota_1` | `0x730000` | `0x700000` | inactive/pending S3 image |
| `rescue_fs` | `0xE30000` | `0x100000` | минимальные ресурсы fault viewer |
| `eventlog` | `0xF30000` | `0x080000` | ограниченное кольцо диагностики |
| future reserve | `0xFB0000` | `0x050000` | место миграции |

Источники: [`config/partitions_16m.csv`](../config/partitions_16m.csv),
[`config/s3_image_limits.json`](../config/s3_image_limits.json) и
[`config/sdkconfig.defaults.esp32s3`](../config/sdkconfig.defaults.esp32s3).
Production включает ESP-IDF rollback и ECC PSRAM через
`CONFIG_SPIRAM_ECC_ENABLE=y`. До обычного UI/radio startup
доказывает ECC, чтение/запись test block и не менее 7,5 МиБ (`0x780000` байт)
usable PSRAM.

Internal SRAM в первую очередь закрепляется за ISR code/data, DMA buffers,
stack и междоменными link. ECC PSRAM хранит ограниченные UI scene, историю
водопада, decoder workspace и audio queue. Captures, recordings, maps,
dictionaries и сменные UI pack являются версионированными данными microSD, а
не содержимым executable image.

## C5: dual OTA на 8 МиБ

C5 локально содержит native Wi-Fi/802.15.4 и IR. Каждый OTA slot равен 3,5 МиБ;
CI предупреждает после 3 МиБ и отвергает образ больше `0x360000`, оставляя
128 КиБ в каждом slot.

| Partition | Offset | Size | Назначение |
|---|---:|---:|---|
| bootloader + table | `0x000000` | до `0x009000` | C5 ROM/second-stage boot и таблица |
| `nvs` | `0x009000` | `0x006000` | ограниченная radio configuration |
| `otadata` | `0x00F000` | `0x002000` | дублированное ESP-IDF pending/rollback state |
| `phy_init` | `0x011000` | `0x001000` | RF calibration seed |
| `coredump` | `0x012000` | `0x010000` | ограниченный crash record |
| `nvs_keys` | `0x022000` | `0x003000` | ключи encrypted NVS |
| boot reserve | `0x025000` | `0x00B000` | boot/migration reserve |
| `ota_0` | `0x030000` | `0x380000` | running/last-known-good C5 image |
| `ota_1` | `0x3B0000` | `0x380000` | inactive/pending C5 image |
| `eventlog` | `0x730000` | `0x050000` | ограниченная диагностика C5 |
| future reserve | `0x780000` | `0x080000` | место миграции |

Источники: [`config/partitions_8m_c5.csv`](../config/partitions_8m_c5.csv),
[`config/c5_image_limits.json`](../config/c5_image_limits.json) и
[`config/sdkconfig.defaults.esp32c5`](../config/sdkconfig.defaults.esp32c5).
ESP-IDF rollback обязателен. В отличие от S3, C5 PSRAM не заявляется как
ECC-защищённая; deadline-critical buffers и state остаются во внутренней RAM.

## RP2354B: нативные A/B и Try Before You Buy

Первые 8 КиБ занимают два стандартных boot slot таблицы разделов RP2350.
Оставшиеся 2040 КиБ описаны в
[`config/rp2354b_partitions.json`](../config/rp2354b_partitions.json), который
служит входом `picotool partition create`.

| Region | Offset | Size | Назначение |
|---|---:|---:|---|
| partition-table slots | `0x000000` | `0x002000` | два boot slot RP2350 по 4 КиБ |
| RP image A | `0x002000` | `0x0E0000` | bootable image A |
| RP image B | `0x0E2000` | `0x0E0000` | linked bootable image B |
| owned data A | `0x1C2000` | `0x010000` | данные версии image A |
| owned data B | `0x1D2000` | `0x010000` | linked data для image B |
| fault log | `0x1E2000` | `0x018000` | ограниченная retained diagnostics |
| service reserve | `0x1FA000` | `0x006000` | миграция partition/schema |

Каждый candidate содержит IMAGE_DEF hash и TBYB flag. После flash-update boot
ROM RP2350 запускает его под фиксированным watchdog 16,7 с. Новый S3 выдаёт
commit лишь после identification и self-test всех доменов; RP вызывает
`explicit_buy()`. Без этого вызова ROM возвращается в предыдущий partition.
Лимит задаёт
[`config/rp2354b_image_limits.json`](../config/rp2354b_image_limits.json).

## Pack и Safety: независимые карты 64 КиБ

Оба C1106 используют одинаковую геометрию, но разные target ID и images. Package
одного никогда не принимается другим.

| Region | Offset | Size | Назначение |
|---|---:|---:|---|
| protected boot manager | `0x0000` | `0x4000` | ROM-invoked flash BSL, проверка подписи/target и выбор slot |
| application A | `0x4000` | `0x5800` | running/last-known-good image с manifest/signature |
| application B | `0x9800` | `0x5800` | inactive/pending image с manifest/signature |
| duplicated boot state | `0xF000` | `0x1000` | version, compatibility, pending state и bounded fault metadata |

CI предупреждает при linked application больше 20 КиБ и отвергает packaged
slot больше 22 КиБ. Точный источник —
[`config/mspm0c1106_memory.json`](../config/mspm0c1106_memory.json). Boot manager
читает обратно inactive slot, локально проверяет его, запускает pending под
watchdog и подтверждает только после собственного self-test и global commit S3.
Blank flash, recovery и update failure оставляют pack release и все TX permits
в fail-closed состоянии.

## Физическое восстановление

- S3: product USB и UART0/RESET/BOOT.
- C5: data-only USB и UART0/RESET/BOOT.
- RP2354B: data-only USB и SWD/RUN/USB_BOOT.
- каждый C1106: NRST, SWDIO/SWCLK, UART1 и изолированное fixture-питание.

Service USB не питает продукт. Recovery может стереть firmware и заменить
owner keys, но не может синтезировать `RUN`, обслужить независимый TPS3435 или
снять аппаратную защёлку `FAULT_KILL`.

Release qualification проверяет потерю питания во время каждого erase/write и
перехода state, wrong-target и повреждённые signatures, несовместимые протоколы,
pending timeout, повреждение обоих slot, принудительный allocation failure и
физическое восстановление полностью стёртых устройств.
