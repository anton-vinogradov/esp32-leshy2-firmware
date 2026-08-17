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
  critical/menu first feedback `≤100 ms` и исправленный для прежней карты
  256 B shared-U214 display quantum. Hardware `DSP-0002/REV-0004W` фиксируют
  `FND-0061`: U214 уже находится на dedicated RP bus, поэтому limit устарел.
  `DEC-0052/REV-0004X` закрывают находку: принимают direct QSPI на S3
  GPIO41/42 и `≤1 ms` time-based arbitration. `DSP-0003/REV-0004Y` оставляют
  фактическую базу, а `DEC-0053/REV-0004Z` принимают 3.5-inch portrait
  `320×480` IPS QSPI+touch class. `DLE06235B/ES3C35P` (`ST77922`) — primary
  HIL, Waveshare SKU `31137` (`AXS15231B`) — secondary HIL. Hardware
  `FND-0063/DSP-0005/REV-0005A` устанавливают exact current assembly candidate
  `HMX035CTFT-001` и проводят ревью его 40-contact fit; production
  ordering/drawing/connector, optics, init table и HIL
  остаются открыты.
  Hardware `AUDIO-0001/REV-0005B` также вносят exact I2C/I2S contacts
  `ES8311` QFN-20. `CE` — fixed address strap `0x19`, P10 — внешний
  `CODEC_PWR_EN`. `FND-0065/0066` фиксируют differential/line-input constraints;
  exact passive и power implementation остаются открытыми.
  `AUDIO-0002/REV-0005C` проводят ревью всего capture/playback/TX/reset тракта.
  `FND-0067` исправляет пропущенный ordinary RX-source control на slow P27 и
  показывает, что P11/P12 могут остаться старыми при S3-only reset.
  Следующий hardware pass `CTL-0001/REV-0004K` обнаружил неполный slow plane.
  Владелец делегировал перебор компоновки; hardware `DEC-0044` принял
  `IMP-0037/A`, а `NIF-0001/REV-0004L` проверили ведущий `G2F-3I`:
  RP2354B/QFN80, пять независимых radio/accessory SPI paths, dedicated SDIO
  S3↔C5, dedicated SPI3 S3↔RP, тогдашние 23/24 slow endpoints и
  изолированный U214 I²C. Последующее audio review занимает последний контакт.
  Единственная high-rate scheduled pair — display+SD на SPI2 с bounded
  quantum; radio FIFO/IPC её не ждут. Hardware `DEC-0059` затем выбирает
  1-bit SDIO и восстанавливает C5 USB+UART и S3 USB+UART service; M5 Unit UART
  использует UART1. Firmware consequence зафиксирован в `ARC-0002`. Повторная
  exact-device проверка обнаружила и исправила crossing
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
  семантику `VOICE_ACTIVITY`. Новый hardware `PIN-0003/REV-0004V` провёл
  ревью machine-generated principle owner/net/pad atlas. Текущий бюджет:
  S3 `32/3/1`, C5 `14/6/1`, RP `48/0/0`, slow I/O `24/0/0`; прежние значения
  C5/RP были stale и исправлены через `FND-0059`. SA518 UART/PTT/activity и
  recovery breakout теперь заканчиваются на exact module contacts, а Si4732
  I²C/reset/interrupt/clock/audio/FMI/AMI — на exact package contacts. UPDATE
  нельзя драйвить до specimen proof его direction/timing ambiguity.
  `FND-0060` оставляет открытыми production display details, codec power/
  analog routing, exact IR, STOP/supervisor, load-switch/isolation, audio/Unit
  protection и service mechanics.
  Hardware `DEC-0051` теперь публикует эту карту в target README как visible
  principle-level working design для G3, не превращая её в frozen HAL/G7.
- Target-specific firmware architecture: **переоткрыта/не выбрана**.
- Бывший three-domain `ARC-0001`: candidate/reference only.
- Hardware `IMP-0043/A` принято как `DEC-0055`: 12-item profiled antenna kit
  требует explicit MPN/profile identity, disarm при каждой смене и безусловный
  запрет TX при unknown/mismatch; SMA сам по себе identity не доказывает.
  Availability проверяется при выборе exact MPN.
- Hardware `IMP-0046/A` принято как `DEC-0054`: сохранить ES8311, добавить
  active high-Z capture, differential speaker и отдельный attenuated TX
  selector, а direct S3 GPIO6 `AUDIO_ARM` использовать для возврата analog
  defaults при reset даже со старыми P11/P12. Firmware теперь считает GPIO6 и
  disarm-first sequencing нормативными; measured gain/mute/passive values открыты.
- Следующий upstream ход: reviewed `PIN-0003` уже позволяет начать G3 —
  адаптацию legacy physical/product mockup и проверку conceptual placement.
  Параллельно hardware закрывает `FND-0058/FND-0060/FND-0066/FND-0067`,
  выбирает exact production parts/feeds/protection/power и переводит `N24H-0001` из `L0` в
  target `T1`. Затем обязательны measured full-mix, quiet-state, RF/
  self-desense, signal-integrity, service и HIL gates. Paper pinout остаётся
  reopenable input, а не atomic target; `G2F-2R/3D` и `LAY-0001` P1/P2/P3 —
  references.

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

`G2F-3I` owners, RP2354B, 1-bit SDIO, SPI IPC и exact pins нельзя потреблять
как final firmware prerequisites до atomic package. 4-bit SDIO остаётся
только fallback evidence; RP2354A и прежние service-component assumptions —
references до своих downstream gates.

## Следующее firmware-действие

Target code/toolchain пока не создаются. Hardware использует reviewed
`PIN-0003` для адаптации legacy physical mockup, одновременно закрывая exact
electrical parts, power/RF и HIL; затем проходит whole-device optimality,
conceptual placement и atomic architecture. После этого firmware превратит
`ARC-0002` input в normative image/owner/IPC/HAL/update/test contract и начнёт
implementation.
