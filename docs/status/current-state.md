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
  principled owner/net/pad atlas. Current budgets are S3 `33/3/0`, C5
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
  TCA9534A mask at local RP I2C address `0x38`; their diode-OR aggregate is
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
  and prequal disabled; a deep cell is refused. `DEC-0074/FND-0078` later
  correct midpoint/stack evidence to PA25/PA26 because PA24 permits no
  injection current, and external recovery research belongs only to an isolated
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
  thresholds. `PWR-0012/DEC-0073/REV-0005AD` first close the direct AON EN
  strap and nine converter EN/PG/qualifier/fault resistors.
  `FND-0084/PWR-0019/DEC-0080/REV-0005AK` amend this to ten positions and
  replace the abstract sequencer with exact AON-PG/MR, 3.07-V SENSE/CT/POR and
  main-EN wiring. Firmware cannot bypass delayed hardware POR. Its initial
  charge rule reserves system load from 85% of negotiated input power and
  requests zero charge on missing/DPM/thermal/fault evidence; transition and
  efficiency HIL remain upstream.
  `FND-0085/PWR-0020/DEC-0081/REV-0005AL` then add exact independent
  `TPS25961DRVR` AON and two `TPS25974LRPWR` main/voice post-buck cutoffs.
  Firmware trusts protected PG only, revokes affected leases and signal groups
  on a latch fault, exposes no bypass/reset API and never retries a persistent
  rail fault. Voice starts a fresh validated power session; main/AON require
  distinct recovery: latched main requires complete source removal, while AON
  owns bounded hardware auto-retry and cannot release main before stable
  PG/SENSE/CT. Trip energy, load-step and hot HIL remain upstream.
  `FND-0086/PWR-0021/DEC-0082/REV-0005AM` then review the consolidated I3
  source, heat, fault and recovery ledger. I3 paper electrical scope is now
  **«Проведено ревью»** and activates dependent I4 paper work at that point;
  procurement,
  received-lot, source-transition, rail, destructive-fault and thermal HIL
  remain explicit upstream gates and cannot become firmware constants.
  `FND-0087/USB-0001/DEC-0083/REV-0005AN` then close the first I4 endpoint:
  exact product USB-C and automatic four-line CC/USB2 protection preserve
  native S3 GPIO19/20 and, at that endpoint, leave GPIO47 free. Firmware closes the USB session
  on detach/PD fault/re-enumeration failure, exposes no protector bypass or
  Alt-Mode/source profile and does not claim fixture-only `FLT`. USB Full-Speed
  RC/SI, ESD, short-to-VBUS and physical placement remain upstream HIL.
  `FND-0088/DSP-0006/DEC-0084/REV-0005AO` then close the display paper
  electrical endpoint. Firmware holds display/touch reset low until protected
  logic power is stable, observes at least 120-ms/100-ms post-release waits,
  enables PWM last and never auto-retries a latched backlight fault. The
  `FAULT_N` point is fixture-only, so software does not fabricate a sensor.
  Final FPC mate, standalone panel sourcing and display/touch/backlight HIL
  remain upstream; this endpoint itself does not change the then-current S3
  `32/3/1` budget.
  `FND-0089/STO-0001/DEC-0085/REV-0005AP` then close the isolated microSD
  paper endpoint. Firmware admits a storage session only after stable detect,
  switched-rail rise and card SPI-mode entry with every other CS high; clean
  removal drains/unmounts before QOD power-off, while unexpected removal marks
  the unwritten tail possibly lost and enters checked recovery. Card-side Ioff
  buffers and CS-gated DAT0 make those states hardware-real without new GPIO.
  Socket access, media/endurance, throughput/contention, hot-removal,
  ESD/short/brownout and corruption-recovery HIL remain upstream.
  `FND-0090/UI-0001/DEC-0086/REV-0005AQ` then restore the complete physical
  control inventory. Dedicated TCA9534A P0…P6 gives
  D-pad/OK/BACK/OPT/F1/F2 and encoder push an interrupt-driven bounded 4x3
  scan, with P7 reserved; encoder A/B use direct PCNT0 on S3 GPIO39/GPIO47; touch IRQ joins
  shared GPIO37. PTT remains
  direct RP GPIO21, while STOP and RE-ARM remain asynchronous AON hardware.
  `FND-0092/UI-0002/DEC-0087/REV-0005AR` then select exact low-current
  `Y78B23214FP` switches for every ordinary position, PTT and RE-ARM, plus an
  exact gold-clad `AEQ10410` COM+NC STOP switch. Separate matrix,
  encoder/PTT and safety ESD arrays and exact pull/filter networks terminate
  every path. Firmware runtime details are in `ARC-0003`; cap/plunger and STOP
  guard/harness mechanics, SYS-I2C address scan and
  control/ESD/fault/concurrent-load HIL remain upstream.
  `FND-0093/DSP-0007/DEC-0088/REV-0005AS` then fix exact integrated ST77922,
  touch address `0x38`, active-low TP_INT, the 10-kOhm raw pull-up and fixed
  non-inverting `SN74LVC1G07DCKR`. Firmware therefore has no polarity profile
  or inverter alternative. Identity/readback, IRQ pulse/clear, reset recovery
  and shared-source HIL remain upstream.
  `FND-0094/IOX-0001/DEC-0089/REV-0005AT` then complete the consolidated I4
  audit. Firmware now consumes main TCA6424A at exact `0x22`, pack admission at
  `0x2A`, bounded shared-bus recovery, full-main-rail reset fallback and
  unchanged isolated P22/P23 STOP/evidence polarity. The microSD return is
  confirmed on real GPIO4. I4 paper electrical scope has **«Проведено
  ревью»**; physical/no-back-power/SI/HIL remains upstream.
  `FND-0095/AUDIO-0003/DEC-0090/REV-0005AU` then close I5 paper electrical
  scope. Firmware now consumes exact reset-off/supervisor-held ES8311,
  Si4732 and SA518 interfaces; P00/P01/P02 capture/speaker/headphone controls;
  receiver or microphone recording; bypass/codec playback; ordinary or
  explicitly armed codec-injected voice audio; and the rule that host VOX
  never implies PTT. I6 RF front ends are active upstream; acoustic, address/
  clock, RF-immunity and concurrent-load HIL remain open.
  `PWR-0013/FND-0078/DEC-0074/REV-0005AE` establish the exact diagnostic
  frontend. Firmware emits one PA22 rising edge; TPUL2G223 channel 1 limits
  the 10-Ohm load to about 34.4 ms typical with a 28.7-40.7-ms C0G paper
  window; production accepts only measured 25-50-ms pulses. PA25/PA26 use the internal 1.4-V reference through
  exact filtered dividers; baseline and loaded samples wait `>=10 ms` for
  settling. `PWR-0017/FND-0082/DEC-0078/REV-0005AI` correct the TPUL WQFN map,
  make channel 2 hold channel 1 clear for a measured 350-860 ms and split the
  load across two parallel 20-Ohm/2-W branches. Firmware waits `>=1 ms` after
  stable admission VDD and `>=10 s` between normal attempts. Droop thresholds
  and calibration remain exact-cell HIL inputs, and the 0.57-0.88-A screen is
  never reported as full-load proof.
  `PWR-0014/DEC-0075/REV-0005AF` then close the exact BQ25798 physical
  profile. Firmware consumes fixed 2S/750-kHz operation, 1-A reset charge,
  a 2.71-3.29-A hardware ILIM envelope, independent non-ignored BQ TS and
  open-drain CE sequencing: contract-derived IINDPM is written/read back
  before charge, and normal charge remains <=2 A. `FND-0079` returns product
  USB-C/USB2 protection to dependent I4. Hardware
  `FND-0080/PWR-0015/DEC-0076/REV-0005AG` then closes separate raw
  VBUS/VBUS_IN startup, hardware SafeMode, 17 exact TPS25751/CAT24 support
  parts, open-drain WP and complete local/host bus pulls. Firmware consumes the
  startup and write-protection ordering without claiming that TPS itself
  verifies the owner signature at every raw-VBUS boot.
  `PWR-0016/FND-0081/DEC-0077/REV-0005AH` then close the holder/thermal paper
  input: exact polarized `Keystone 1048P`, four functional independent
  contacts, protected-button-top exact-cell scope, two direct per-cell MAX NTC
  roles and one independent BQ TS worst-slot role. Firmware cannot infer an
  arbitrary cell identity or substitute modeled temperature for a missing
  channel. `PWR-0018/FND-0083/DEC-0079/REV-0005AJ` then replace both generic
  cells with exact `XTAR 18650 4000mAh` protected button-top instances:
  `28.8 Wh` nominal per pair, 10-A discharge class, 2-A standard/product
  charge ceiling and `18.7 × 69.7 mm` maximum envelope. Runtime blocks charge
  outside initial `0…45 °C`, rejects raw/USB-equipped/third-party variants and
  cannot infer missing certification/lot identity. Certification documents,
  specimen fit, droop/thermal-stack and continuity/thermal HIL stay upstream.
- The integrated mockup remains paused until the `INT-0001` chain closes.
  Hardware has marked `I2` through I5 paper electrical scope reviewed;
  `FND-0096/N24E-0001/DEC-0091/REV-0005AV` additionally review the first I6
  three-nRF paper subblock. Runtime now consumes exact Ioff isolation,
  100-ms/three-identity admission, directional forward-power evidence and
  ordered common-rail shutdown. Ebyte mate, thresholds, T1 coexistence and all
  other I6 RF endpoints remain open before expansion internals.
  `FND-0097/NAT-0001/DEC-0092/REV-0005AW` then review separate native S3
  2.4-GHz and C5 2.4/5-GHz evidence feeds. Runtime keeps ANT1-only C5 routing,
  two evidence identities, exact-feed loss/EIRP profiles and fail-closed
  assertion/decay windows; inbound RF may delay quiet but never authorize TX.
  Jumper/chassis identities, thresholds and coexistence HIL remain upstream.
  `FND-0098/CCRF-0001/DEC-0093/REV-0005AX` next review the exact CC1101
  endpoint. Runtime consumes 315/433/868–915 cold selection, a versioned S3↔RP
  handoff, dual-ended isolation and final-line AD8314 evidence; `00` is safe
  isolation and P05 is the only free main slow-I/O contact. VNA/conducted
  tuning, thresholds, legal profiles, SMA mechanics and coexistence remain
  upstream; voice/IR RF endpoints are still active.
  In parallel it keeps
  the explicit I3 physical HIL gates and
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

No target code or toolchain is created yet. Hardware follows `INT-0001`, with
`I2` through I5 plus the I6 nRF, native S3/C5 and CC1101 paper electrical subblocks reviewed while
I6 remains the active dependent paper block; exact protected product-USB, display, isolated microSD, controls,
touch, slow-I/O/shared-interface and audio/receiver contracts are reviewed, while
their physical mechanics and HIL remain active. Specimen mechanics,
exact-cell droop and timer/load hot HIL plus
complete transition/rail/loss/thermal/fault evidence remain mandatory physical
I3 gates; they no longer masquerade as unresolved paper architecture. The
integrated physical mockup resumes after the joint internal review. Whole-device optimality,
conceptual placement and atomic architecture follow. Firmware will then turn
the `ARC-0002` input into the
normative image/owner/IPC/HAL/update/test contract before implementation.

Documentation `FND-0072/IMP-0051/DEC-0060/REV-0005N` moves engineering
chronology out of all four target README files. The root firmware page now
describes the finished UI, radio services, data/privacy, STOP and
update/recovery behavior without narrating hardware decisions. Current maturity
and open inputs remain canonical here and in the hardware review ledger.
