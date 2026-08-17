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
  menu first feedback and a corrected 256 B shared-U214 display quantum; exact
  display/optics and HIL remain open.
  The next hardware pass `CTL-0001/REV-0004K` found an incomplete slow plane.
  The owner delegated layout search; hardware `DEC-0044` accepts
  `IMP-0037/A`, while `NIF-0001/REV-0004L` review the leading `G2F-3I`:
  RP2354B/QFN80, five independent radio/accessory SPI paths, dedicated 4-bit
  SDIO S3↔C5, dedicated SPI3 S3↔RP, 23/24 slow endpoints and isolated U214 I²C.
  The only high-rate scheduled pair is display+SD on SPI2 with bounded quanta;
  radio FIFO/IPC never waits for it. C5 UART0+EN/BOOT/strap is the recovery
  path because GPIO13/14 carry SDIO. Firmware consequences are recorded in
  `ARC-0002`. A repeated exact-device check found and fixed an RP2354B PIO
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
  The same hardware pass records `FND-0056`: SA518 rev 1.1 exposes no
  dedicated SQ pin, so firmware consumes only qualified `VOICE_ACTIVITY`
  semantics and treats pin-17 UPDATE/recovery as an unresolved fixture gate.
- Target-specific firmware architecture: **reopened/not selected**.
- Former `ARC-0001` three-domain contract: candidate/reference only.
- Next upstream gate: hardware selects the exact production nRF MPN/lot and
  SMA/feed/protection/antenna-profile implementation, advances `N24H-0001`
  from `L0` to target `T1`, then closes
  measured full-mix points, quiet-state power controls,
  physical RF/self-desense,
  peripherals, signal integrity, power/service and HIL for leading `G2F-3I`.
  Its reviewed paper ownership/pins/resources are inputs, not an atomic target.
  `G2F-2R/3D` and `LAY-0001` P1/P2/P3 remain references.

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

`G2F-3I` owners, RP2354B, 4-bit SDIO, SPI IPC and exact pins cannot be consumed
as final firmware prerequisites before the atomic package. Former 1-bit SDIO,
RP2354A and three-USB/DBG10 assumptions remain reference evidence only.

## Next firmware action

No target code or toolchain is created yet. Hardware first qualifies physical
RF, exact parts/power and HIL for `G2F-3I`, then adapts the legacy physical
mockup and completes whole-device optimality, conceptual placement and atomic
architecture. Firmware will then turn the `ARC-0002` input into the normative
image/owner/IPC/HAL/update/test contract before implementation.
