# Leshy2 Firmware — current engineering state

> Snapshot: 2026-08-18. Intended software behavior is in the
> [target README](../../README.md). Canonical decisions live in the
> [hardware review ledger](https://github.com/anton-vinogradov/esp32-leshy2/tree/main/docs/review).

## Current maturity

- Firmware implementation: **not started**.
- Product behavior/safety requirements: the 125 leaves and competitor delta
  have received repeated hardware G2 review (`REV-0002AS`).
- `W-EXTRA-11` is closed by external iButton profile
  `DEC-0033/REQ-IBTN-0001`; `DEC-0034/REQ-EXT-0001` accepts M5-first Unit/Cap,
  a separate high-throughput tier and no native M5-Bus. `DEC-0039/REQ-SCOPE-0001`
  later remove the former FIDO target and reject generic USB host while keeping
  transport derived by a concrete RF/SDR profile. `AUD-0007` reviewed haptic;
  `DEC-0036/REV-0002AJ` reject product haptic, motor and a dedicated external
  profile. `AUD-0008/DEC-0037/REQ-IMU-0001/REV-0002AL` accept the optional
  external measurement-pose profile. `AUD-0009/REV-0002AM` complete the
  physical-keyboard archetype fact review; `DEC-0038/REV-0002AN` close it as
  no integrated keyboard plus bounded phone-assisted text. `AUD-0010/0011` and
  `REV-0002AP` complete the scope propagation. `AUD-0012/REV-0002AQ` review
  6 GHz/Wi-Fi 6E facts; `DEC-0040/REV-0002AR` fully reject it. Repeated G2 is
  closed by `REV-0002AS`; hardware `DEC-0041` inserts G2F logical/electrical
  feasibility before the physical mockup. Hardware `DEC-0042/REV-0003Y` now
  review one exact-device/net source; it now has three structurally checked
  maps and leading `G2F-3I`.
  Hardware `DSP-0001/REV-0003Z` verify three real display/touch boundaries and
  one microSD socket. `FND-0051` rejects the old generic 24-pin display mapping
  and proves that ST7796S cannot meet the inherited 4.5 MB/s gate. Hardware
  `DEC-0043/REV-0004J` accept task/dirty-region rendering, `≤100 ms` critical/
  menu first feedback and a 256 B quantum corrected for the former shared-U214
  map. Hardware `DSP-0002/REV-0004W` record `FND-0061`: U214 is already on a
  dedicated RP bus, so that limit is stale. `DEC-0052/REV-0004X` close it by
  accepting direct QSPI on S3 GPIO41/42 and `<=1 ms` time-based arbitration.
  `DSP-0003/REV-0004Y` retain the factual basis, while `DEC-0053/REV-0004Z`
  accept a 3.5-inch portrait `320×480` IPS QSPI+touch class.
  `DLE06235B/ES3C35P` (`ST77922`) is primary HIL and Waveshare SKU `31137`
  (`AXS15231B`) secondary HIL. Hardware `FND-0063/DSP-0005/REV-0005A`
  identify exact current assembly candidate `HMX035CTFT-001` and review its
  40-contact fit; production ordering/drawing/
  connector, optics, init table and HIL remain open.
  Hardware `AUDIO-0001/REV-0005B` also instantiate exact `ES8311` QFN-20
  I2C/I2S contacts. `CE` is fixed address strap `0x19`; P10 is external
  `CODEC_PWR_EN`. `FND-0065/0066` record the ES8311/PAM differential and
  line-input constraints; exact passive/power implementation remains open.
  `AUDIO-0002/REV-0005C` now review the complete capture/playback/TX/reset
  path. `FND-0067` corrects the omitted ordinary RX-source control on slow P27
  and identifies that P11/P12 can stay stale through S3-only reset.
  The next hardware pass `CTL-0001/REV-0004K` found an incomplete slow plane.
  The owner delegated layout search; hardware `DEC-0044` accepts
  `IMP-0037/A`, while `NIF-0001/REV-0004L` review the leading `G2F-3I`:
  RP2354B/QFN80, five independent radio/accessory SPI paths, dedicated SDIO
  S3↔C5, dedicated SPI3 S3↔RP, the then-current 23/24 slow endpoints and
  isolated U214 I²C. The later audio review closes the last slow contact.
  The only high-rate scheduled pair is display+SD on SPI2 with bounded quanta;
  radio FIFO/IPC never waits for it. Hardware `DEC-0059` subsequently selects
  1-bit SDIO and restores C5 USB+UART and S3 USB+UART service; M5 Unit UART
  uses UART1. Firmware consequences are recorded in `ARC-0002`. A repeated
  exact-device check found and fixed an RP2354B PIO
  GPIO-window crossing; PIO data now stays on `GPIO30..46`, fixed mux groups
  are contracted, and the RP retains seven of twelve PIO state machines plus
  three of sixteen DMA channels. Later `DEC-0045/0046` accept one top-level
  signal group, while `SG-N24` still requires all three nRF concurrently
  full-function in every PTX/PRX mix with no peer standby/gaps. Unused
  interfaces enter hardware/native power-down and digital quiet states; RP
  GPIO15/GPIO23 and C5 GPIO4 become group-level power controls. Exact mixed-RF
  envelope policy is now accepted by `DEC-0047`; the ordered second ESP32-DIV
  becomes the `N24H-0001` `L0 DIV↔DIV` pre-HIL observer, but target pass
  requires `T1` on the exact Leshy2 revision. `DEC-0048` accepts external SMA
  for all onboard antenna endpoints and three compact nRF IPEX→SMA paths.
  Hardware `ANT-0001/REV-0004P` additionally prove separate Si4732 `FMI`
  FM/SW and `AMI` AM/LW antenna domains; `DEC-0049/REV-0004Q` close `IMP-0041`
  with option A: 9 labelled SMA, distinct runtime identities and only a
  manifest-qualified loop/pod for AM/LW. Exact production lots/feeds, measured
  sensitivity points, power parts,
  physical RF/self-desense and target HIL remain open.
  Hardware `RFH-0001/REV-0004R` prove first-generation U.FL/MHF I/AMC only
  for S3/C5; Ebyte says generic `IPX`, so `FND-0057` requires a
  specimen-fit/VNA gate. `RFH-0002/REV-0004S` review the real antenna
  ecosystems; `DEC-0050/REV-0004T` accept bounded
  `2 native-Wi-Fi RP-SMA + 7 standard SMA`. Polarity does not change the nine
  runtime identities. Hardware `ANT-0002/REV-0004U` now review the sourcing
  shortlist: shared MPNs are viable for S3/C5 and the three nRF paths, common
  868/915 can be combined, but CC 315/433, VOICE VHF/UHF and Si4732 whip/loop
  require distinct profiles. `FND-0058` leaves exact two-source assemblies and
  target RF HIL open.
  The same hardware pass records `FND-0056`: SA518 rev 1.1 exposes no
  dedicated SQ pin, so firmware consumes only qualified `VOICE_ACTIVITY`
  semantics. New hardware `PIN-0003/REV-0004V` reviews the machine-generated
  principled owner/net/pad atlas. Current budgets are S3 `32/3/1`, C5
  `14/6/1`, RP `48/0/0` and slow I/O `24/0/0`; `FND-0059` corrects the stale
  prior C5/RP figures. SA518 UART/PTT/activity and recovery now terminate on
  exact module contacts, while Si4732 I²C/reset/interrupt/clock/audio/FMI/AMI
  terminate on exact package contacts. UPDATE must not be driven before
  specimen proof resolves its direction/timing ambiguity. `FND-0060` leaves
  display production details, codec power/analog routing, exact IR,
  STOP/supervisor, load-switch/isolation, audio/Unit
  protection and service mechanics open.
  Hardware `DEC-0051` now publishes this map in its target README as the visible
  principle-level working design for G3 without making it a frozen HAL/G7.
- Target-specific firmware architecture: **reopened/not selected**.
- Former `ARC-0001` three-domain contract: candidate/reference only.
- Hardware `IMP-0043/A` is accepted as `DEC-0055`: the 12-item profiled antenna
  kit requires explicit MPN/profile identity, disarm on every change and
  unconditional TX denial for unknown/mismatch; SMA itself proves no identity.
  Availability is checked when the exact MPN is selected.
- Hardware `IMP-0046/A` is accepted as `DEC-0054`: retain ES8311, add active
  high-Z capture, differential speaker and separate attenuated TX selectors,
  and use direct S3 GPIO6 `AUDIO_ARM` to force analog defaults across reset even
  if P11/P12 remain stale. Firmware now treats GPIO6 and the disarm-first
  selector sequence as normative; measured gain/mute/passive values remain open.
- Hardware `DEC-0061/SAFE-0002/REV-0005O` accept and review `I2`: an always-on
  non-programmable latch resets S3, C5 and RP, independently gates all nine
  TX/rail requests and requires a fresh physical RE-ARM. Eight active-low
  actual-TX states (`S3`, `C5`, `nRF0..2`, `CC`, voice and optical IR) reach a
  TCA9534A mask at local RP I2C address `0x20`; their diode-OR aggregate is
  direct active-low `RP_ANY_TX_N` on RP GPIO22 and drives a physical red LED.
  A low evidence line is actual TX; inconsistent, missing or unqualified
  evidence is `unknown/unavailable`, never inferred safe. RF taps, thresholds
  and HIL remain `I6`, while the exact AON source/hold-up is now an `I3` input.
- Hardware `PWR-0002/FND-0073/REV-0005P` review the `I3` prerequisites from
  the current device/scenario set. They preserve the 2.5/3-A 3.3-V floor and
  separate 4-V voice rail, but reject the legacy power sheet as a target:
  no system power path, no real fuel gauge, no justified Type-C current
  detection, obsolete rail sizes and no current quiet-state/safety branches.
  The owner accepted `IMP-0052/B` as `DEC-0062`: two 18650 slots remain
  individually replaceable behind fail-closed admission. Firmware exposes
  distinct cell and set/bus state, cannot override the hardware-open
  charge/discharge boundary, and treats mismatch, removal/contact bounce and
  incomplete identity as blocked/unknown. `REV-0005Q` reviews propagation.
  The owner accepted `IMP-0053/B` as `DEC-0063`: sink-only USB-PD supports
  5-V fallback, 9 V/3 A and 15 V/2 A up to 30 W, while source/power-bank/
  20-V/PPS/OTG stay disabled and S3 USB2 remains direct. `PWR-0004/REV-0005R`
  review exact TPS25751D/BQ25798, mandatory recoverable CAT24C512 EEPROM,
  TVS2200, shared SYS-I2C0/IRQ behavior, signed dual-region policy updates and
  reset-default charge disable. ARC-0002 now consumes that runtime contract.
  Hardware `DEC-0064/PWR-0006/FND-0076/REV-0005S` then reopened and compared
  supervised 2S, controlled two-slot 1S and a one-slot 1S variant. The owner
  selected supervised 2S in `DEC-0065/REV-0005T`: both admitted cells are
  required, while direct parallel stays rejected. `PWR-0005/REV-0005U` then
  revalidate the exact candidates; `DEC-0066/REV-0005V` accept
  `MAX17320G20+T` as gauge/protector and `MSPM0C1104SDGS20R` as local admission
  owner. The latter becomes a fourth independently recoverable firmware image
  domain; S3 sees bounded read-only state and cannot release a refused pair.
  A replaced cell invalidates pair SOC/SOH and starts admission/relearning.
  `DEC-0067/REV-0005X` then accept no in-device deep-cell recovery and the
  exact fully-switching surrounding path. The protected image keeps zero-volt
  and prequal disabled; a deep cell is refused, PA24/PA25 provide midpoint/
  stack evidence, and external recovery research belongs only to an isolated
  Controlled-Zone fixture.
  `DEC-0068/PWR-0008/REV-0005Y` then review the exact active downstream rail
  tree: low-IQ autonomous 3.3-V AON, independent fixed 3.3-V compute, 4.0-V
  voice and protected 5.0-V accessory converters, five reset-off quiet-state
  load switches and a reverse-blocking/current-limited external eFuse.
  ARC-0002 now consumes their fixed-voltage, PG/fault, shutdown/discharge and
  nRF common-branch sequencing rules. Converter passives were still open at
  that checkpoint; charger/diagnostic-load passives plus rail/thermal/fault
  HIL remain in I3.
  `DEC-0069/REV-0005Z` then replace the early external auto-retry eFuse suffix
  with exact latch-off `TPS259470LRPWR`; runtime retry loops are forbidden and
  a new explicit action is required after physical fault removal.
  `PWR-0009/DEC-0070/REV-0005AA` then correct optional-rail PG semantics:
  hardware qualifies each voice/accessory PG with its safe EN, so runtime
  accepts `EN=0, PG=0` as normal off and treats `EN=1, PG=0` as bounded pending
  followed by a latched timeout rather than an immediate or permanent false
  fault.
  `PWR-0010/DEC-0071/REV-0005AB` then correct the external-eFuse runtime input:
  its 1.509-A limit applies immediately at startup, the exact `dVdt` passive
  controls ramp admission, and 2 A is only a bounded post-start excursion.
  OVLO recovery bypasses the normal ramp and is therefore a fresh admission;
  signals remain isolated until the rail is requalified. The exact eight-part
  profile is consumed without inventing unmeasured thresholds or retry paths.
  `PWR-0011/DEC-0072/REV-0005AC` then close the 24 converter energy,
  configuration and feedback parts. Firmware consumes fixed nominal
  3.318/4.000/5.000-V rail identities and qualification results but exposes no
  voltage-setting API and does not reinterpret their paper limits as measured
  thresholds. Converter EN/PG pulls and all timing/load-step/HIL evidence stay
  upstream hardware inputs.
- The integrated mockup remains paused until the `INT-0001` chain closes.
  Hardware has marked `I2` reviewed and is now closing `I3` power, then
  UI/audio/RF/expansion internals. In parallel it keeps
  `FND-0058/FND-0060/FND-0066/FND-0067` explicit and selects
  exact production parts/feeds/protection/power and advances `N24H-0001` from `L0` to target
  `T1`. Measured full-mix, quiet-state, RF/self-desense, signal-integrity,
  service and HIL gates still follow. The paper pinout remains a reopenable
  input, not an atomic target; `G2F-2R/3D` and `LAY-0001` P1/P2/P3 remain
  references.

Hardware `FND-0039` found that the prior process selected `SYN-3A`, exact owners
and CAD before product design, whole-product optimality and conceptual
placement. The owner chose reopen option A in hardware `DEC-0032`.

## Valid inputs

- Main/Lab/Controlled-Zone behavior and non-aggression onboarding;
- conservative TX defaults, hard STOP, no automatic re-arm and distinct
  actual-TX evidence;
- complete capability/concurrency/failure requirements;
- owner-controlled signed updates, rollback and independent physical recovery/
  diagnostics for every eventually selected programmable target;
- no-loss cost and explicit mismatch/proposal review rules;
- qualified accessory manifests, default-off unknown M5 profiles and separate
  level gates for external iButton read/emulate/write; two-tier expansion with
  no blanket M5-Bus or low-rate/raw-data equivalence claim.
- radio/key mission boundary; optional BadUSB is a software-only Controlled-Zone
  exception over the existing USB-device path and cannot block core release.

## Invalidated target assumptions

`G2F-3I` owners, RP2354B, 1-bit SDIO, SPI IPC and exact pins cannot be consumed
as final firmware prerequisites before the atomic package. Four-bit SDIO is
fallback evidence only; RP2354A and former service-component assumptions
remain references until their downstream gates.

## Next firmware action

No target code or toolchain is created yet. Hardware follows `INT-0001`,
with `I2` reviewed and the I3 source, battery-manager, active rail topology,
eFuse and converter energy/feedback passives reviewed; the remaining
charger/EN/PG/diagnostic values and complete rail/loss/thermal/fault evidence
are the active I3 work. The integrated physical
mockup resumes after the joint internal review. Whole-device optimality,
conceptual placement and atomic architecture follow. Firmware will then turn
the `ARC-0002` input into the
normative image/owner/IPC/HAL/update/test contract before implementation.

Documentation `FND-0072/IMP-0051/DEC-0060/REV-0005N` moves engineering
chronology out of all four target README files. The root firmware page now
describes the finished UI, radio services, data/privacy, STOP and
update/recovery behavior without narrating hardware decisions. Current maturity
and open inputs remain canonical here and in the hardware review ledger.
