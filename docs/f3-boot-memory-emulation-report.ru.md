# Итог F3 — boot, память и эмуляция

[English](f3-boot-memory-emulation-report.md) · [На главную](../README.ru.md) ·
[Роадмап прошивки](roadmap.ru.md) ·
[Машинное закрытие](../config/f3_4_review.json)

F3 прошла ревью. Точные ESP32-S3 debug и release target binaries загрузились в
Espressif QEMU, инициализировали и проверили выбранную 8-МиБ octal PSRAM, а
также исполнили portable paths self-test, retained-first-fault и failed-update
в RAM. Все пять targets дважды пересобраны из чистых каталогов: 52/52 artifacts
воспроизвелись побайтно, все актуальные image/RAM/static rollback gates прошли.

Это не заявление о физической плате. F3 не приписывает себе реальный flash
rollback, периферию, radio, watchdog или переход `FAULT_KILL`.

## Результат кратко

| Evidence | Результат ревью |
|---|---|
| Точный target emulator | ESP32-S3 QEMU `esp_develop_9.2.2_20250817` |
| S3 boot runs | Debug + release; по шесть последовательных boot/PSRAM markers |
| S3 scenario runs | Debug + release; по девять последовательных markers |
| Portable fault suite | 24/24 сценария под ASan/UBSan |
| Актуальные target builds | 10 конфигураций; 52/52 побайтно воспроизводимых artifacts |
| Resource gates | 10/10 image и linked-memory gates проходят |
| Rollback topology | 5/5 статических A/B layouts помещаются; физических transitions заявлено 0 |
| Аппаратные действия | Закупка, PCB layout и fabrication не разрешены |

## Актуальный запас ресурсов

В таблице взят больший application image из debug/release каждого target.
«Запас до maximum» — остаток принятого policy budget, а не вся свободная flash
слота.

| Target | Самый большой image | Policy maximum | Запас до maximum | Результат linked memory |
|---|---:|---:|---:|---|
| S3 | 187 040 Б | 7 077 888 Б | 6 890 848 Б | в DIRAM свободно 280 715 Б; 8-МиБ PSRAM проверена в runtime |
| C5 | 172 224 Б | 3 538 944 Б | 3 366 720 Б | в HP SRAM свободно 263 010 Б; external PSRAM ожидает железа |
| RP2354B | 18 484 Б | 884 736 Б | 866 252 Б | в main + scratch SRAM свободно 526 008 Б |
| Pack | 3 168 Б | 22 528 Б | 19 360 Б | в application SRAM свободно 7 880 Б |
| Safety | 3 296 Б | 22 528 Б | 19 232 Б | в application SRAM свободно 7 880 Б |

Точные debug/release записи, hashes, partitions и linker regions находятся в
[boundary evidence F3.3](../config/f3_3_boundary_review.json).

## Что исполнялось, а что нет

| Target | Принято в F3 | Явное физическое закрытие |
|---|---|---|
| S3 | Точный boot chain, `app_main`, UART, тест 8-МиБ PSRAM и три изолированных RAM-model сценария | Leshy2 H7/H8 + firmware F10: display, touch, microSD, audio, radio, GPIO timing, первая OTA-запись и настоящий rollback |
| C5 | Воспроизводимые target artifacts, portable contracts, image/RAM/A-B fit | `ESP32-C5-DevKitC-1-N8R8`, затем H7/H8: boot, PSRAM, Wi-Fi/BLE/802.15.4, IR, SDIO и rollback |
| RP | Воспроизводимые Arm-secure artifacts, portable contracts, image/SRAM/A-B fit | SC1512-A4 carrier или H7 через SWD/UART: boot, TBYB, PIO/DMA, radio и timing Cap-Bus |
| Pack | Воспроизводимые boot/application artifacts, safety model, flash/SRAM/A-B fit | `LP-MSPM0C1106`, затем H7/H8: boot, ADC/I2C, admission timing и flash rollback |
| Safety | Воспроизводимые boot/application artifacts, safety model, flash/SRAM/A-B fit | `LP-MSPM0C1106`, затем H7/H8: watchdog, thermal ADC, `FAULT_KILL`, TX-lease timing и flash rollback |

Пустой ESP OTA-data sector выявил реальное ограничение доступной QEMU flash
model. Проверенный runner создаёт детерминированную начальную OTA entry только
для QEMU и полностью оставляет первую boot-запись, последующие flash mutations
и rollback вне принятых claims. Production ELF не патчится.

## Цепочка evidence

- [Матрица возможностей исполнения](../config/f3_execution_capability_matrix.json)
  фиксирует одну точную virtual SoC и четыре честных физических target gate.
- [Runtime plan](../config/f3_runtime_plan.json) фиксирует QEMU, размер PSRAM,
  timeout, markers, diagnostics и границу OTA fixture.
- [F3.1 debug](../config/f3_1_s3_debug_runtime_review.json) и
  [release](../config/f3_1_s3_release_runtime_review.json) evidence доказывают boot.
- [Сводный evidence F3.2](../config/f3_2_runtime_review.json) доказывает target
  execution трёх RAM paths и sanitized host suite.
- [Boundary evidence F3.3](../config/f3_3_boundary_review.json) связывает
  актуальные build inputs, artifacts, linked memory, partitions и rollback topology.
- [Закрытие F3](../config/f3_4_review.json) назначает каждый остаток конкретному
  dev-board/HIL gate.

## Выход и следующая граница

Все exit criteria F3 выполнены на честном уровне evidence. Прошивка продолжает
с `F4.0.0`: до реализации фиксируются поддержка transport и end-to-end план
evidence IPC/scheduler. Железо может использовать этот отчёт как закрытый
пререквизит `H4.0.1` и начать объединённое read-only ревью H4.1; заказы, PCB
placement и routing всё ещё не разрешены.
