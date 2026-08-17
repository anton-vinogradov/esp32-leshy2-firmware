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
  проверяют единый exact-device/net source; теперь он имеет три structurally
  checked maps и ведущий `G2F-3I`.
  Hardware `DSP-0001/REV-0003Z` проверяют три реальные display/touch boundaries
  и один microSD socket. `FND-0051` отвергает старый generic 24-pin display
  mapping и доказывает, что ST7796S не выполняет унаследованный gate 4.5 MB/s;
  hardware `DEC-0043/REV-0004J` принимают task/dirty-region rendering,
  critical/menu first feedback `≤100 ms` и исправленный 256 B shared-U214
  display quantum; exact display/optics и HIL остаются открыты.
  Следующий hardware pass `CTL-0001/REV-0004K` обнаружил неполный slow plane.
  Владелец делегировал перебор компоновки; hardware `DEC-0044` принял
  `IMP-0037/A`, а `NIF-0001/REV-0004L` проверили ведущий `G2F-3I`:
  RP2354B/QFN80, пять независимых radio/accessory SPI paths, dedicated 4-bit
  SDIO S3↔C5, dedicated SPI3 S3↔RP, 23/24 slow endpoints и изолированный U214
  I²C. Единственная high-rate scheduled pair — display+SD на SPI2 с bounded
  quantum; radio FIFO/IPC её не ждут. C5 UART0+EN/BOOT/strap остаётся recovery
  path, потому что GPIO13/14 заняты SDIO. Firmware consequence зафиксирован в
  `ARC-0002`. Повторная exact-device проверка обнаружила и исправила crossing
  реального RP2354B PIO GPIO-window; теперь PIO data pins находятся в
  `GPIO30…46`, fixed mux закреплён контрактами, а RP оставляет 7/12 PIO SM и
  3/16 DMA в резерве. Последующие `DEC-0045/0046` принимают ровно одну
  top-level signal group, но внутри `SG-N24` требуют все три nRF одновременно
  полнофункциональными в любом PTX/PRX mix без standby/gaps. Неиспользуемые
  interfaces переходят в hardware/native power-down и digital quiet-state;
  это забирает RP GPIO15/GPIO23 и C5 GPIO4 под group-level power gates. Exact
  envelope policy теперь принята `DEC-0047`; заказанный второй ESP32-DIV
  становится `L0 DIV↔DIV` pre-HIL observer в `N24H-0001`, но target pass
  требует `T1` на exact Leshy2 revision. `DEC-0048` принимает external SMA для
  всех onboard antenna endpoints и три compact nRF IPEX→SMA paths. Exact
  Hardware `ANT-0001/REV-0004P` дополнительно подтверждают отдельные Si4732
  `FMI` FM/SW и `AMI` AM/LW antenna domains; `DEC-0049/REV-0004Q` закрывают
  `IMP-0041` вариантом A: 9 labelled SMA, отдельные runtime identities и
  только manifest-qualified loop/pod для AM/LW. Exact production lots/feeds,
  измеренные sensitivity points, power parts, physical
  RF/self-desense и target HIL открыты.
  Hardware `RFH-0001/REV-0004R` подтверждают first-generation U.FL/MHF I/AMC
  только для S3/C5; Ebyte пишет generic `IPX`, поэтому `FND-0057` требует
  specimen-fit/VNA gate. `RFH-0002/REV-0004S` проверяют реальные antenna
  ecosystems; `DEC-0050/REV-0004T` принимают ограниченный
  `2 native-Wi-Fi RP-SMA + 7 standard SMA`. Девять runtime identities от
  polarity не меняются. Hardware `ANT-0002/REV-0004U` провели ревью sourcing
  shortlist: общие MPN допустимы для S3/C5 и трёх nRF, common 868/915 можно
  объединить, но CC 315/433, VOICE VHF/UHF и Si4732 whip/loop требуют разных
  profiles. `FND-0058` оставляет exact two-source assemblies и target RF HIL
  открытыми.
  Та же hardware проверка фиксирует `FND-0056`: SA518 rev 1.1 не выводит
  dedicated SQ, поэтому firmware использует только квалифицированную
  семантику `VOICE_ACTIVITY`, а pin-17 UPDATE/recovery остаётся fixture gate.
- Target-specific firmware architecture: **переоткрыта/не выбрана**.
- Бывший three-domain `ARC-0001`: candidate/reference only.
- ⚠️ Предложение hardware `IMP-0043` ожидает решения: принять profiled antenna
  kit. Для firmware это означает explicit antenna MPN/profile, disarm при его
  смене и безусловный запрет TX при unknown/mismatch; SMA сам по себе identity
  не доказывает.
- Следующий upstream gate: решение `IMP-0043`, затем hardware закрывает
  `FND-0058`, выбирает exact production nRF MPN/lot и
  SMA/feed/protection/antenna-profile implementation, переводит `N24H-0001`
  из `L0` в target `T1`, затем закрывает
  measured full-mix points,
  quiet-state power controls, physical RF/self-desense,
  peripherals, signal integrity, power/service и HIL ведущего `G2F-3I`.
  Его reviewed paper ownership/pins/resources — вход, а не atomic target.
  `G2F-2R/3D` и `LAY-0001` P1/P2/P3 остаются references.

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

`G2F-3I` owners, RP2354B, 4-bit SDIO, SPI IPC и exact pins нельзя потреблять
как final firmware prerequisites до atomic package. Бывшие 1-bit SDIO,
RP2354A и three-USB/DBG10 assumptions тем более остаются reference evidence.

## Следующее firmware-действие

Target code/toolchain пока не создаются. Hardware сначала квалифицирует
physical RF, exact parts/power и HIL `G2F-3I`, затем адаптирует legacy physical
mockup и проходит whole-device optimality/conceptual placement/atomic
architecture. После этого firmware превратит `ARC-0002` input в normative
image/owner/IPC/HAL/update/test contract и начнёт implementation.
