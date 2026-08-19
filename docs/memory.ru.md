# Контракт памяти прошивки

[На главную](../README.ru.md) · [English](memory.md) · [Runtime-архитектура](architecture.ru.md) · [Аппаратные линии памяти](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/memory.ru.md)

Образ S3 рассчитан на точный `ESP32-S3-WROOM-1U-N16R8`: 16 МБ flash и 8 МБ
octal PSRAM. В production обязательно включается ECC PSRAM: остаётся не менее
7,5 МБ usable RAM и сохраняется диапазон модуля −40…+85 °C.

Это требование закреплено в
[`config/sdkconfig.defaults.esp32s3`](../config/sdkconfig.defaults.esp32s3):
production-сборка обязана содержать `CONFIG_SPIRAM_ECC_ENABLE=y`, octal mode,
инициализацию PSRAM при загрузке и частоту 80 МГц. CI проверяет эти значения как
build inputs и отклоняет образ, если хотя бы одно из них отсутствует или
переопределено.

## Разметка flash 16 МБ

Оба исполняемых slot имеют размер 7 МиБ, поэтому неудачное обновление не
уничтожает последний исправный образ. CI предупреждает после 6 МиБ и отвергает
образ больше `0x6C0000` (6,75 МиБ), сохраняя по 256 КиБ запаса на slot для
роста, выравнивания и служебных данных подписи.

| Partition | Offset | Size | Назначение |
|---|---:|---:|---|
| bootloader + table | `0x000000` | до `0x009000` | подписанный ROM boot path и таблица разделов |
| `nvs` | `0x009000` | `0x006000` | ограниченные настройки и калибровка |
| `otadata` | `0x00F000` | `0x002000` | дублированное состояние active/pending/rollback |
| `phy_init` | `0x011000` | `0x001000` | начальная radio calibration |
| `coredump` | `0x012000` | `0x010000` | ограниченная запись аварии |
| `nvs_keys` | `0x022000` | `0x003000` | ключи encrypted NVS, когда режим включён |
| boot reserve | `0x025000` | `0x00B000` | запас boot/security; не используется для assets продукта |
| `ota_0` | `0x030000` | `0x700000` | текущий или last-known-good образ S3 |
| `ota_1` | `0x730000` | `0x700000` | inactive update/rollback образ S3 |
| `rescue_fs` | `0xE30000` | `0x100000` | минимальные шрифты fault viewer, schema и recovery resources |
| `eventlog` | `0xF30000` | `0x080000` | ограниченное кольцо диагностики |
| future reserve | `0xFB0000` | `0x050000` | место миграции; не расходуется молча |

Машинным источником этой таблицы служит
[`config/partitions_16m.csv`](../config/partitions_16m.csv); документация не
является отдельной конкурирующей разметкой.

Update записывается только в inactive slot, проверяется по target и ключу
владельца/release, запускается как pending и подтверждается лишь после
ограниченных health checks. Ошибка, watchdog reset или несовместимый протокол
между доменами вызывают rollback. Native USB, UART0 и keyed service header не
зависят от обоих OTA slot.

## Runtime RAM

- Internal SRAM в первую очередь закрепляется за ISR code/data, DMA-capable
  buffers, scheduler state, междоменными link и stack, которые должны работать
  даже при занятой PSRAM.
- ECC-защищённая PSRAM хранит UI scene, dirty rectangles, историю водопада,
  рабочие наборы decoder, audio queue и cache.
- У каждого крупного pool есть явный максимум и путь отказа allocation; radio,
  safety и fault viewer не зависят от случайно свободного cache.
- RF captures, recordings, maps, dictionaries и сменные UI asset pack хранятся
  на microSD. Это versioned data, а не часть executable image.

До запуска UI и радио startup-проверка подтверждает включённый ECC, не менее
`0x780000` байт доступной PSRAM и успешную запись/чтение тестового блока. Ошибка
не переводится в обычный режим: S3 сохраняет диагностическую причину и входит в
ограниченный fault/recovery path.

Приёмка прототипа проверяет production-конфигурацию, startup self-test, не менее
7,5 МБ usable PSRAM, одновременные
full-duplex audio и display/storage/radio-event stress, принудительный отказ
allocation, rollback обоих slot и recovery при стёртых либо повреждённых
application slot.
