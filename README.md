# Leshy2 firmware

[Русский](README.ru.md) · [Hardware](https://github.com/anton-vinogradov/esp32-leshy2)

> **Firmware status: F2-R2.5 — reproducibility qualification is next.** The R1
> F0–F4 work remains regression evidence, but its five-domain topology is no
> longer current. Follow the [firmware roadmap](docs/roadmap.md).

## Firmware roadmap and current position

This block stays on the firmware landing page through firmware release.
Detailed exit criteria and the explicit intersections with the separate
[hardware roadmap](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/roadmap.md)
are kept in the [firmware roadmap](docs/roadmap.md).

| Stage | Status | Result |
|---|---|---|
| F0 · Product contracts | ✅ **Reviewed:** [F0-R2 result](docs/f0-product-contracts-report.md) | six domains, identities, independent rollback, S3-last update and honest execution gates |
| F1 · Portable cores | ✅ **Reviewed:** [F1-R2 result](docs/f1-portable-cores-report.md) | 34 scenarios pass normal and ASan/UBSan; six-domain update, rear-RP Airband and integrated faults |
| **F2 · Target projects and build system** | **▶️ Current: F2-R2.5**; all 12 R2 debug/release builds, 60 artifacts, 16 maps and 16 size gates [passed F2-R2.4](config/f2_r2_build_qualification.json), R1 [report retained](docs/f2-target-build-system-report.md) | prove two byte-identical clean passes and publish the bilingual F2-R2 closure report |
| F3 · Boot, memory and emulation | ⏳ R1 [report retained](docs/f3-boot-memory-emulation-report.md); waiting for F2-R2 | requalified six-target memory, boot, emulator and physical gates |
| F4 · IPC and scheduling | ⏳ R1 work paused; waiting for F3-R2 | Hub-centered transports, typed messages, credits and priority isolation |
| F5 · BSP and drivers | ⏳ Waiting for F4 and current R2 schematic | all device, control, sensor and power-state drivers |
| F6 · UI, display, storage and audio | ⏳ Waiting for F5 | responsive menu/waterfall, recording, audio and fault viewer |
| F7 · Radio, IR and expansion | ⏳ Waiting for F5/F6 | receive/TX profiles, full 3×nRF24 operation and quiet inactive paths |
| F8 · Functional levels and safety UX | ⏳ Waiting for F7 | Normal, Laboratory and Controlled Zone workflows |
| F9 · Signed update and recovery | ⏳ Waiting for F1/F3 | owner-controlled six-target bundle, rollback and physical recovery |
| **F-PO · First-unit order gate** | 🔒 [Planned and locked](config/first_spin_preorder_gate.json) until current H2/H6 and diagnostic evidence exist | reproducible six-domain images, S3 QEMU, host/fake HAL, available development-board runs, recovery bundle and first-power-on script |
| F10 · HIL and system qualification | 🔒 Waiting for F4–F9 and hardware H7 | prototype fault, RF, power, thermal and endurance evidence |
| F11 · Firmware release | 🔒 Waiting for F10 and hardware H8 | reproducible signed images, installer, recovery kit and release tag |

Every completed top-level `F*` phase receives a separate result report linked
from this table; internal substeps only move the exact marker.

The project may order **exactly one** fully assembled `R2-EVT1` only after the
[F-PO gate](config/first_spin_preorder_gate.json) is bound to the final H2/H6
hashes and all seven `FPO1`–`FPO7` diagnostic evidence gates pass. The routed H6
release candidate becomes the immutable order release only after that gate
closes. Complete F6–F8 product features are not an order prerequisite, but the
order-critical F5 diagnostic-driver slice must cover every fitted endpoint from
the exact H2 manifest, including present/missing fake-HAL behavior and smoke
evidence on every available target-development-board path. The remaining
pre-order package is six reproducible diagnostic images, S3 QEMU, one
flash/recovery bundle and a reviewed safe bring-up script. Factory powered
Function Test is optional and is
considered only when the final quote makes it near-free. The factory
deterministically manufactures and assembles that single unit, including the
exact production display; the owner performs the first full power-on after
delivery under the reviewed procedure.

**Firmware is at F2-R2.5.** The [reviewed F0-R2 result](docs/f0-product-contracts-report.md)
closes the contract foundation without claiming an implemented target. The generated
[`h0_r2_hardware_contract.json`](config/h0_r2_hardware_contract.json) binds the
firmware repository by SHA-256 to the functional source, exact C5 service mux
and exact dual-RP working pin map. R2 has six
targets: S3, C5, RF RP, Hub RP, Pack and Safety. UI, buttons and display remain
front-local. Hub RP owns microSD and all three nRF24 paths; rear RF RP owns
CC1101, voice, audio, `BROADCAST_RX`,
M5 and exactly one signed U214/U219 Cap profile.
The retained [`hardware_bsp_contract.json`](config/hardware_bsp_contract.json)
and [`hardware_integration_contract.json`](config/hardware_integration_contract.json)
are explicitly historical R1 single-RP imports and cannot authorize R2. The
[R2/H2 authority gate](config/r2_h2_sync_gate.json) remains fail-closed until a
new H2 export contains all six domains, both `SC1512-A4` instances, the exact
H1-R2.31 RP maps and the exact H0-R2 M1 map. The working BSP contains all 48
GPIO positions for each RP and the six fixed C5 SDIO contacts, but this is
pre-H2 authority, not ECAD, target-build, emulator or HIL closure.
The reviewed [target-project structure](config/f2_r2_target_projects.json)
establishes six production-SDK roots, six unique application images and two
protected-controller boot images. RF RP and Hub RP have separate Pico SDK
trees, entry sources and image identities. The hash-bound
[R2 BSP](config/f2_r2_bsp_generation.json) now generates six deterministic
domain descriptors and [binds each](config/f2_r2_bsp_consumption.json) to one
SDK project. The atomic [F2-R2.4 qualification](config/f2_r2_build_qualification.json)
records 12 successful configure/build jobs, 60 artifacts, 16 maps and 16 passed
size gates. It proves compilation, linkage and static image fit, not boot,
peripheral execution, reproducibility, emulation or physical hardware.
The reviewed [memory and rollback contract](config/f0_r2_memory_rollback_contract.json)
keeps six independent dual-slot domains: both RP2354B and both MSPM0 devices
share geometry only, never target identity, state or flash contents. No physical
rollback transition or production signature-verifier fit is claimed yet.
The reviewed [update policy](config/update_policy.json) stages all six images,
boots and commits Pack → Safety → C5 → RF RP → Hub RP → S3, persists a
power-loss-safe journal and requires a signed bridge bundle for breaking IPC
changes. Its 16.7-second RP TBYB budget remains explicitly unmeasured.
The reviewed [execution matrix](config/f0_r2_execution_gate_matrix.json) keeps
five evidence layers distinct. Only S3 has an exact official QEMU machine. S3,
C5, Pack and Safety have exact selected-module/MCU development-board paths;
Pico 2 is explicitly only a non-exact RP2350A surrogate for both RP2354B
targets. No R2 build, dev-board or Leshy2 HIL run is claimed.
The [reviewed F1-R2 result](docs/f1-portable-cores-report.md) adds independent
RF-RP/Hub-RP update state, five rear-RP Airband receive-only states and integrated
Hub/Pack/Safety faults. Its 34 scenarios pass normal and ASan/UBSan host runs;
that remains portable evidence, not a target build.
Mandatory receive-only Airband uses rear-RP GP35/36, a fixed 112-MHz LO and the
existing Si4732 audio path. Airband TX is absent. Physical hardware completed
and reviewed `H1-R2.37`; H2 and the complete H3-R2.1 DC/source workstream are
reviewed; H3-R2.2.1 reviewed 14 startup, shutdown, reset and recovery scenarios,
and H3-R2.2.2 reviewed 7,316 USB/pack/DPM/brownout/source-loss transitions with
zero unsafe admissions or automatic restarts. H3-R2.2.3/.4 then reviewed five
protected-rail starts, four load-step envelopes and ten watchdog/fault-display
cases with zero analytical failures or automatic restarts. Its exact firmware-facing
[sequence](config/h3_r2_transition_contract.json) and
[handover](config/h3_r2_handover_contract.json) and
[watchdog/fault-display](config/h3_r2_inrush_watchdog_contract.json) contracts
are imported fail-closed. The [H3-R2.3 analog result](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/analog-electrical-verification.md), [H3-R2.4 digital result](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/digital-electrical-verification.md), [H3-R2.5 RF result](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/rf-electrical-verification.md) and [H3-R2.6 thermal/fault result](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/thermal-fault-electrical-verification.md) are reviewed; the exact [RF/coexistence](config/h3_r2_rf_coexistence.json) and [thermal/fault](config/h3_r2_thermal_fault.json) contracts are imported fail-closed, and the current hardware point is `H3-R2.7` for the final cross-check and physical-residual register.
H3-R2.1.2 reviewed explicit binding for 613 fitted powered instances—597 direct
and 16 indirect—and six external loads, and H3-R2.1.3 reviewed 224
passing profiles across all four rails with 30.560% minimum current reserve and
24.706 °C minimum junction-temperature reserve. H3-R2.1.4 reviews all 75
source/pack lines and safely admits all 2,266 states; maximum pack current is
3.516 A and charging always yields before system load. H3-R2.1.5 reconciles all
619 loads, 224 rail profiles and 2,266 states through 15 passing checks. The exact H3-R2.0.1 input freeze, H3-R2.0.2
parameter/model provenance register, H3-R2.0.3 method contract and H3-R2.1.1
register of 2,266 legal power states are reviewed,
while the exact imported pin/config authority remains the reviewed
`H1-R2.31` artifact:
the locality-first two-board placement, matched outer/turned-over inner faces
and service access are generated. The 226-body physical register includes all
eight exact TX detectors, five required couplers and eight bounded local
evidence islands; the accepted AD8314 package and exact Hirose U.FL packaging-route changes save hardware cost without altering any
firmware-visible net or behavior. The 2026-08-30 cost decision retains every current top-20 hardware group and permanently assigns separate
`ANT-433-CW-QW-SMA` units to SUB-GHz and UHF VOICE; firmware must never treat those antenna loads as a manually shared resource. S3 keeps the direct exact 20-MHz i8080-8 path to
exact `ER-TFT035IPS-6` + `ER-TPC035-6`, ordinary UI, encoder and USB. Six S3
GPIOs remain uncommitted after reset/service closure. M1 has an exact 80-contact
map with 9 true NC reserves, latched `FAULT_KILL` for the front indicator on
contact 35, an independent S3 fault-UI reset on contact 36 and
a separate enclosure load path.
The display is physically oriented with its flex toward the antenna edge; F5/F6
must rotate ILI9488 memory orientation and FT6236 touch coordinates by 180 degrees.
That transform is required target behavior, not an implemented-driver claim.
Stable outer silkscreen identifies the UI and RF/power PCB roles, `R2-EVT1` and
`REV A`; the changing `H1-R2.xx` work marker remains documentation-only.
S3, C5, RF RP and Hub RP each retain USB, RESET/BOOT and internal DBG10.
The Airband filter has a nominal/stress feasibility audit and a 24×11-mm tuning
cell, and port/antenna kit codes are synchronized. The onboard analog-video
receiver, decoder, connector and all firmware contracts are removed: no
post-PCBA active module or owner soldering remains in the product boundary.
The exact 3V3_MAIN cell admits 3.75 A continuous / 4.25 A step across all 12
allowed signal groups; dynamic and enclosure proof remains an H3 gate. Airband
filter H3 uses bounded pre-layout parasitics, H6 repeats routed extraction
before order and H8 selects the VNA-qualified fitted/DNP state. The complete R2
mockup passes its structural audit and was accepted on 2026-08-30. Hardware
`H2-R2.0.1` reviewed the live `FSUSB42MUX/C11355` route and `H2-R2.0.2`
reviewed the exact service-VBUS detector/latch/release implementation. Current
`H2-R2.0.3` reviewed the exact `TCA9803DGKR/C2687966` Pack/Safety
powered-off-Ioff boundary. `H2-R2.1.1` reviewed three native projects, 23 sheets,
six domain owners, 240 exact MPN groups and 1,195 product positions.
`H2-R2.1.2` reviewed exact identities for 234 board groups, six explicit
non-PCBA groups and 1,658 logical contacts. `H2-R2.1.3` materialized 1,185
fitted positions and 4,323 physical pins in the three native KiCad projects.
All 4,319 logical endpoints reconcile into 4,063 connected endpoints, 256
explicit no-connects and 823 canonical nets; all three projects pass KiCad ERC
with zero errors and zero warnings. `H2-R2.1.4` reconciles six domains,
173 controller pins, 52 cross-project nets and 238 cross-sheet nets; the
reviewed `H2-R2.1.5` firmware sync gate is open. H3 now freezes those exact
inputs. Placement/routing has not started,
and R2 byte reproducibility
and order authorization remain open.

### Current phase F2-R2 — detailed position

<!-- current-substep: F2-R2.5 -->

▶️ **`F2-R2.5` — current.** The atomic
[F2-R2.4 qualification](config/f2_r2_build_qualification.json) ran the locked
[shell-free dispatcher](tools/build_f2_r2_targets.py) against all six SDK
projects in debug and release. Its inputs remain the reviewed
[R2 plan](config/f2_r2_target_rebaseline.json),
[matrix](config/f2_r2_build_matrix.json),
[project roots](config/f2_r2_target_projects.json),
[BSP ownership](config/f2_r2_bsp_consumption.json) and
[build policy](config/f2_r2_build_policy.json). All 12 configure/build jobs passed; all 60 named
artifacts and 16 maps exist, and all 16 image-size gates pass without warnings.
The record remains bound to the reviewed matrix and build policy and preserves
the exact S3, C5, dual-RP and Pack/Safety boundaries. No target boot, peripheral,
emulator, development-board or physical run occurred, and byte reproducibility
is not yet proven. F2-R2.5 must now run two clean passes, compare every declared
artifact byte-for-byte and publish the bilingual F2-R2 closure report only if
that comparison passes.
The exact marker and its evidence move together in every commit.

<details>
<summary><strong>Retained R1 F0–F4 evidence — not the current topology</strong></summary>

### Historical R1 phase F4 — position when R2 reopened the architecture

<!-- historical-substep: F4.1.4 -->

**Last R1 marker: `F4.1.4` (cancelled by R2).** The planned direct S3-C5
dev-board gate was not run. Four
locked S3/C5 debug/release builds pass, and exact S3 QEMU executes six
fake-SDIO traffic/fault scenarios in both configurations. Those runs prove
application behavior above the fake boundary, not SDIO signaling, throughput,
timing or C5 USB coexistence. This marker and its evidence move together in
each commit.

- `F2.0` — freeze the target/toolchain matrix.
  - ✅ `F2.0.0` — register the five targets and their flash/RAM/rollback
    contracts.
  - ✅ `F2.0.1` — reviewed exact SDK/toolchain versions, official support,
    lifecycle, license and build-host requirements; see the
    [five-image build environment](docs/toolchains.md).
  - ✅ `F2.0.2` — immutable SDK revisions, 26 verified archive records and the
    hash-locked ESP-IDF Python environment passed review.
  - ✅ `F2.0.3` — one local/CI matrix, shell-free dispatcher, fail-closed
    preflight and 26 named target artifacts passed review.
- `F2.1` — create the shared source/component tree without target pins.
  - ✅ `F2.1.0` — directories, single ownership, target-neutral portable code
    and the empty-until-F2.3 generated-source boundary passed review.
  - ✅ `F2.1.1` — strict C17/C++17, warnings-as-errors for project code,
    debug/release optimization and map-producing link policy passed review.
  - ✅ `F2.1.2` — the integrated environment, source, build-policy, H2-contract
    and 24-scenario host review passed together.
- `F2.2` — create minimal S3, C5, RP, Pack and Safety SDK projects.
  - ✅ `F2.2.0` — the S3 ESP-IDF project, portable component, production
    memory defaults and debug/release inputs passed structural review.
  - ✅ `F2.2.1` — the C5 ESP-IDF project, portable component, production
    memory defaults and debug/release inputs passed structural review.
  - ✅ `F2.2.2` — the exact RP2354B Arm-secure project, 2-MiB custom board,
    partition input and debug/release policy passed structural review.
  - ✅ `F2.2.3` — the exact Pack MSPM0C1106 project, separate boot/application
    images, memory boundaries and debug/release policy passed structural review.
  - ✅ `F2.2.4` — the exact Safety MSPM0C1106 project, separate boot/application
    images, fail-closed entry and debug/release policy passed structural review.
  - ✅ `F2.2.5` — one integrated review passed for five projects, 37 files,
    26 artifacts and 20 debug/release command plans with zero target execution.
- `F2.3` — consume the accepted generated pin/BSP contract.
  - ✅ `F2.3.0` — the immutable H2 source identity, 5 domains, 125 contacts,
    112 nets, 4 transports, 10 groups and proof-field model passed review.
  - ✅ `F2.3.1` — 11 generated C/header files preserve all 125 contacts, pass
    strict C17 syntax checks and reproduce byte-for-byte with a hashed manifest.
  - ✅ `F2.3.2` — every target consumes exactly its domain table and include
    path; no foreign table, copied BSP file or hand-authored pin was found.
  - ✅ `F2.3.3` — sibling H2, deterministic generation, strict C17 tables and
    one-owner consumption passed one integrated review.
- `F2.4` — pass debug/release builds, map files and image-size gates.
  - ✅ `F2.4.0` — locked-toolchain preflight for five targets passed review.
    - ✅ `F2.4.0.1` — exact ESP-IDF `v6.0.2`, Pico SDK/picotool `2.3.0` and TI
      MSPM0 SDK `2.11.00.07` sources and revisions passed review.
    - ✅ `F2.4.0.2` — exact S3/C5 compilers, debuggers, ULP tools, OpenOCD and
      ROM ELFs installed, recognized and passed review.
    - ✅ `F2.4.0.3` — hash-locked Python 3.12 environment and exact CMake/Ninja
      passed review; evidence is in [`config/f2_4_preflight_progress.json`](config/f2_4_preflight_progress.json).
    - ✅ `F2.4.0.4` — hash-verified native Arm GNU `15.2.Rel1` passed review for RP2354B.
    - ✅ `F2.4.0.5` — hash-verified TI Arm Clang `4.0.5.LTS` and SysConfig
      `1.28.0.4712` passed review for Pack/Safety.
    - ✅ `F2.4.0.6` — 30 exact SDK, Git, lock, compiler and input checks plus
      debug/release dispatcher preflight passed; [machine evidence](config/f2_4_preflight_review.json).
  - ✅ `F2.4.1` — S3 debug/release configure, build, ten-artifact presence and
    image-size gates passed; [machine evidence](config/f2_4_s3_build_review.json).
  - ✅ `F2.4.2` — C5 debug/release configure, build, ten-artifact presence and
    image-size gates passed; [machine evidence](config/f2_4_c5_build_review.json).
  - ✅ `F2.4.3` — RP debug/release configure, build, eight-artifact presence and
    image-size gates passed; [machine evidence](config/f2_4_rp_build_review.json).
  - ✅ `F2.4.4` — Pack debug/release configure, build, twelve-artifact presence
    and image-size gates passed; [machine evidence](config/f2_4_pack_build_review.json).
  - ✅ `F2.4.5` — Safety debug/release configure, build, twelve-artifact presence
    and image-size gates passed; [machine evidence](config/f2_4_safety_build_review.json).
  - ✅ `F2.4.6` — all 52 debug/release artifacts, 14 maps and 10 image-size
    gates passed one integrated review; [machine evidence](config/f2_4_build_review.json).
- ✅ `F2.5` — two complete clean passes produced 52/52 byte-identical
  artifacts; 24 distributable images contained no absolute workspace path.
  See the [F2 result report](docs/f2-target-build-system-report.md) and
  [machine evidence](config/f2_5_reproducibility_review.json).
- `F3.0` — freeze the runtime-evidence plan before claiming a boot.
  - ✅ `F3.0.0` — official emulator/simulator support, instruction coverage,
    boot observability and unavoidable dev-board gates
    for all five targets passed review: exact vendor QEMU exists only for S3;
    [machine matrix](config/f3_execution_capability_matrix.json).
  - ✅ `F3.0.1` — exact hash-locked QEMU archives, debug/release recipes, six
    ordered boot markers, a 30-second timeout and fail-closed result contract
    passed review; [machine plan](config/f3_runtime_plan.json).
  - ✅ `F3.0.2` — the five-target evidence matrix and one fail-closed runner
    passed review without executing a target; [machine matrix](config/f3_acceptance_matrix.json).
- ✅ `F3.1` — S3 debug and release images each passed six ordered markers in
  exact Espressif QEMU, including 8-MiB octal-PSRAM initialization and memory
  test; [debug evidence](config/f3_1_s3_debug_runtime_review.json) and
  [release evidence](config/f3_1_s3_release_runtime_review.json).
- ✅ `F3.2` — S3 debug/release each passed nine ordered markers for boot,
  self-test, retained-first-fault and failed-update RAM rollback; 24 portable
  scenarios also passed ASan/UBSan. This does not claim nonvolatile persistence
  or flash rollback; [integrated evidence](config/f3_2_runtime_review.json).
- ✅ `F3.3` — a fresh double clean-build reproduced 52/52 artifacts; ten current
  image/RAM gates and five static rollback topologies fit. S3 debug is 187,040
  bytes with 6,890,848 bytes before its maximum; zero physical rollback
  transitions are claimed. See the
  [boundary evidence](config/f3_3_boundary_review.json).
- ✅ `F3.4` — the [global F3 result](docs/f3-boot-memory-emulation-report.md)
  closes the phase with exact S3 execution, 52 reproducible artifacts and five
  explicit physical target/HIL gates.
- `F4.0` — freeze the transport execution and evidence plan.
  - ✅ `F4.0.0` — [four transports and eight exact SDK endpoint bindings reviewed](config/f4_0_transport_capability_matrix.json); QEMU proves none of their PHYs.
  - ✅ `F4.0.1` — [one fail-closed lifecycle, fixed ownership/queues, credits, duplicates, deadlines, reset and exact ESSL lock reviewed](config/f4_0_1_adapter_contract.json).
  - ✅ `F4.0.2` — [one integrated runner, six evidence classes and 37 scenarios reviewed](config/f4_0_2_acceptance_matrix.json); [baseline snapshot](config/f4_0_2_acceptance_snapshot.json) claims zero transport runs.
- `F4.1` — implement and exercise S3↔C5 SDIO.
  - ✅ `F4.1.0` — [exact offline ESSL 1.1.2 payload and single-owner S3↔C5 source boundary reviewed](config/f4_1_s3_c5_source_boundary.json); [30-file manifest](third_party/esp_serial_slave_link.vendor-lock.json).
  - ✅ `F4.1.1` — [common high-speed core reviewed](config/f4_1_1_high_speed_core_review.json): 19 ASan/UBSan scenarios; cumulative duplicate-safe bulk grants replace the unsafe absolute-credit draft.
  - ✅ `F4.1.2` — [S3 host and C5 SDIO slave endpoints reviewed](config/f4_1_2_s3_c5_endpoint_review.json): generated pins, one-bit 20-MHz SDIO, exact ESSL and two locked debug builds; zero QEMU/PHY claims.
  - ✅ `F4.1.3` — [exact builds and fake-SDIO QEMU reviewed](config/f4_1_3_s3_c5_qemu_review.json): four target builds, two S3 QEMU runs, six scenarios per run and zero PHY claims.
  - ⛔ `F4.1.4` — not run; superseded by the R2 Hub↔C5 4-bit path.
- `F4.2` — implement and exercise S3↔RP SPI+alert.
- `F4.3` — implement and exercise Pack/Safety I²C mailboxes.
- `F4.4` — inject saturation, duplicate, deadline, reset and link-loss faults.
- `F4.5` — reconcile target evidence and publish the global F4 result.

F3 is reviewed at its honest evidence boundary. F4 now turns the accepted
message contracts into real target transports while preserving safety/control
priority under waterfall and bulk traffic. Each substep updates evidence, this
exact marker and both language pages in the same commit.

</details>

The firmware turns Leshy2 radio paths into one field instrument: it renders the
menu and waterfall, controls receive and transmit, records data, manages
expansion and preserves a safe state through faults. This documentation
describes the resulting product and its implementation.

## User capabilities

- Fast navigation through D-pad, `OK`, `BACK`, `OPT`, `F1`, `F2`, encoder,
  touch and `PTT`; one maintained `RUN/KILL` switch controls admission and
  physical fault recovery.
- A continuously scrolling spectrum waterfall and path indicators, updating
  only the changed display regions.
- Receive profiles, scanning, supported-protocol decoding and recording of RF
  events, audio and metadata to microSD.
- Stereo playback and external-microphone capture through a CTIA headset, with
  continuous insertion detection and an internal-microphone option for
  ordinary TRS headphones.
- Full mixed operation of three nRF24 radios: `3R`, `1T2R`, `2T1R` and `3T`
  without software disabling a neighboring receiver.
- 2.4/5-GHz Wi-Fi, BLE, ESP-NOW, IEEE 802.15.4, Sub-GHz, broadcast RX,
  VHF/UHF voice, IR, stock U214 LoRa RX/GNSS and exact evidence-qualified
  `LESHY2-LORA-CAP-01-EU868/US915` RX/TX profiles.
- An optional signed U219 profile: CC1101 is hard RX-only and NFC is limited to
  reader/poller read operations. Its 13.56-MHz field remains disabled until the
  independent `EV_N9` detector passes VNA and HIL qualification.
- Import, export and backup of owner profiles; a locally paired phone may supply
  occasional long-form text.

## Three functional levels

1. **Normal mode** — ordinary receive, diagnostics, maintenance and lawful
   communications.
2. **Laboratory** — passive, defensive and constrained research tools.
3. **Laboratory → Controlled Zone** — potentially dangerous active functions.
   Every entry shows a fresh mandatory banner; each action requires separate
   arming and an authorized target or isolated environment.

Firmware cannot override hardware `FAULT_KILL`, derive permission from detected
transmission or restore old arming after reset, recovery, profile change or a
fault. A latched fault requires a physical `KILL`→`RUN` cycle.

## Six-domain runtime

```mermaid
flowchart TB
  S3["S3 image<br/>application and direct UI/display"]
  HUB["Hub RP2354B image<br/>front fan-out, storage, nRF24 ×3"]
  C5["C5 image<br/>native 2.4/5 GHz, 802.15.4, IR"]
  RP["RF RP2354B image<br/>broadcast/Airband, audio, Sub-GHz, voice, Cap Bus"]
  PACK["pack MSPM0 image<br/>local battery-pack admission"]
  SAFE["safety MSPM0 image<br/>watchdog, thermal zones and TX leases"]
  WDG["TPS3435<br/>independent 1.6 s timeout"]
  S3 <-->|"40-MHz quad-SPI + alert"| HUB
  HUB <-->|"4-bit SDIO · 20-MHz bring-up · 40-MHz target"| C5
  HUB <-->|"20-MHz SPI + alert"| RP
  HUB -->|"bounded commands"| PACK
  PACK -->|"read-only state/fault"| HUB
  HUB -->|"heartbeat + one group lease"| SAFE
  SAFE -->|"read-only fault record"| HUB
  SAFE -->|"deadline service"| WDG
  WDG -->|"hardware FAULT_KILL"| SAFE
```

Hard real-time reactions execute at the physical path owner. Inter-processor
messages are typed and versioned; link loss revokes the lease and moves the
dependent function to a safe state. Display, storage and radio avoid long
cross-subsystem blocking operations.

On a fault, C5, RF RP and Hub RP enter their defined safe/reset states. If the UI thermal zone remains safe, S3
may run only a signed fault viewer showing the cause, measured value and limit,
action taken, event identifier and `KILL`→`RUN` instruction. If the display or
UI zone is unsafe, the screen turns off and the independent amber `FAULT` LED
remains visible.

Long operation uses a qualified USB-PD source; the product makes no battery-
autonomy or uptime-hours promise. `Settings > Safety > Full self-test` offers
24-hour, default 48-hour and explicitly warned startup-only proof intervals.
Only the local physical UI may stage a change, and it takes effect after the
next physical `KILL`→`RUN` proof. The safety controller owns the deadline;
expiry revokes leases and enters the retained fault state. This setting cannot
weaken the watchdog, thermal limits, power-fault response or TX-lease checks.

## Update and owner control

Images are signed, target-bound and installed with rollback. Signatures protect
against package substitution without closing the device: owners can build from
source, use their own keys and recover each controller through an independent
physical interface. Irreversible lockdown is not enabled by default.

## Documentation

- [Firmware roadmap and current position](docs/roadmap.md)
- [R1 build environment retained for requalification](docs/toolchains.md)
- [Firmware architecture and subsystem behavior](docs/architecture.md)
- [Flash, PSRAM and rollback layout](docs/memory.md)
- [Hardware architecture](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/hardware.md)
- [Safety model](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/safety.md)
