# Leshy2 Firmware — current engineering state

> Snapshot: 2026-08-17. Intended software behavior is in the
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
- Hardware `SAFE-0001/REV-0005M` review the `I2` safety prerequisites and open
  `FND-0071`: STOP must reset RP2354B together with S3/C5, while 3×nRF and
  CC1101 still lack source-specific physical TX evidence. **⚠️ Proposal
  `IMP-0050/A`** provides hardware `ANY_TX` on RP GPIO22 and an eight-bit source
  mask over local I2C without a new pin. Until the decision this is not a
  frozen HAL; firmware keeps commanded/current/actual/unknown distinct.
- The integrated mockup remains paused until the `INT-0001` chain closes.
  Hardware first accepts and propagates the `I2` safety/evidence topology, then
  closes power/UI/audio/RF/expansion internals. In parallel it keeps
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
starting with the open `I2` STOP/evidence package; the integrated physical
mockup resumes after the joint internal review. Whole-device optimality,
conceptual placement and atomic architecture follow. Firmware will then turn
the `ARC-0002` input into the
normative image/owner/IPC/HAL/update/test contract before implementation.

Documentation `FND-0072/IMP-0051/DEC-0060/REV-0005N` moves engineering
chronology out of all four target README files. The root firmware page now
describes the finished UI, radio services, data/privacy, STOP and
update/recovery behavior without narrating hardware decisions. Current maturity
and open inputs remain canonical here and in the hardware review ledger.
