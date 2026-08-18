# Firmware architecture workspace

- Status: **target-specific architecture blocked; G2F-3I paper runtime input reviewed**
- Superseding hardware decision: [`DEC-0032`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0032-reopen-product-design-before-cad.md)
- Corrected method: [`FLOW-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/FLOW-0001-product-to-cad-gates.md)

Firmware currently consumes only the already reviewed capability, safety,
update, failure and evidence subset. Hardware `FND-0040/AUD-0004` is resolving
the missing current-competitor delta; pending candidates are not silently added
or rejected here. Firmware must not select compute ownership, image count,
IPC, pins or HAL before the hardware whole-device architecture is accepted.

[`ARC-0001`](ARC-0001-three-domain-runtime-contract.md) preserves the former
`SYN-3A` three-domain runtime study. Its typed-channel, local-deadline, lease,
compatibility, update and failure ideas may be reused, but its S3/C5/RP owners,
1-bit SDIO, SPI+alert, exact budgets and three-image lifecycle are not normative.

[`ARC-0002`](ARC-0002-g2f-3i-runtime-input.md) records the leading `G2F-3I`
paper map after hardware `DEC-0044/NIF-0001/REV-0004L`: independent radio
buses, dedicated RP/C5 IPC, bounded display+SD scheduling and complete
recovery inputs. It also records hardware `DEC-0045/0046`: one active
top-level group, `SG-N24` as three concurrently full-function PTX/PRX radios,
and verified quiet states for every unused interface. It is a reviewed upstream
input, not a target/HAL/toolchain freeze; exact nRF mixed-RF measurements,
physical RF, exact parts/power and HIL remain open. Hardware `DEC-0047` closes
the policy choice with a qualified internal envelope; `N24H-0001` separates
the ordered ESP32-DIV `L0` pre-HIL observer from target Leshy2 `T1`.
`DEC-0048` adds external-SMA port/antenna identity to the runtime manifest;
`DEC-0050` adds assembly polarity metadata without changing logical paths;
hardware `ANT-0002/REV-0004U` adds a reviewed sourcing shortlist but no target
MPN. `DEC-0055/REV-0005E` accept explicit profiled-kit identity, disarm on
profile changes and TX denial for unknown/mismatch; availability is checked at
exact-MPN selection. Exact two-source hardware and measurements remain pending
under `FND-0058`.

[`ARC-0003`](ARC-0003-local-controls-runtime-contract.md) consumes hardware
`DEC-0086/UI-0001`: dedicated TCA9534A P0…P6 gives the complete
D-pad/OK/BACK/OPT/F1/F2 set and encoder push an interrupt-driven bounded 4×3
scan while P7 remains reserved; encoder A/B use direct S3 PCNT0 on GPIO39/GPIO47,
physical PTT stays direct RP GPIO21 and STOP/RE-ARM remain asynchronous AON
controls. Touch IRQ joins shared GPIO37 through a specimen-selected polarity
adapter and never falls back to polling-only operation.

Hardware `PIN-0003/REV-0004V` now review the machine-generated principled
owner/net/pad atlas. Current direct budgets are S3 `33/3/0`, C5 `14/6/1`, RP
`48/0/0` and slow I/O `24/0/0`; exact SA518 service and Si4732 control/antenna
contacts are represented. This is a reviewed paper input, not final electrical
closure: hardware `FND-0060` keeps the remaining exact peripheral, safety,
power, isolation and service endpoints open.
Hardware `DEC-0051` publishes the same projection in its target README as the
visible G3 working design; firmware still treats it as reopenable upstream
input until atomic architecture.
Hardware `DEC-0059/REV-0005L` amend the same input to dedicated 1-bit
S3↔C5 SDIO, restoring C5 native USB and S3 default UART0 while retaining both
UART service paths. M5 Unit UART moves to UART1 on unchanged GPIO7/8. The link
still requires ≥1.5 MB/s framed HIL; 4-bit is fallback evidence, not a parallel
runtime profile.
Hardware `DEC-0062/REV-0005Q` retain two individually replaceable 18650 slots
behind fail-closed admission. `DEC-0064/PWR-0006/REV-0005S` later reopened the
electrical alternatives; `DEC-0065/REV-0005T` select supervised 2S for the
base product, with both cells required.
Hardware `DEC-0077/PWR-0016/REV-0005AH` additionally freeze exact polarized
`Keystone 1048P`, protected-button-top compatibility and three distinct NTC
roles. Firmware treats cell identity as a qualified profile and every missing
or inconsistent thermal/contact channel as fail-closed; it does not infer an
arbitrary cell's authenticity from two terminals.
Hardware `DEC-0079/PWR-0018/REV-0005AJ` now selects two exact
`XTAR 18650 4000mAh` protected button-top instances as the first qualification
target: `28.8 Wh` nominal per pair, 10-A discharge class and 2-A standard/
product charge ceiling. Firmware blocks charge outside the initial `0…45 °C`
window and treats missing assembly certification/lot identity as an upstream
kit fault, not as something electrical measurements can authenticate.
`DEC-0063/PWR-0004/REV-0005R` accept
the exact sink-only 30-W TPS25751DREFR/BQ25798RQMR frontend with mandatory
CAT24C512WI-GT3 boot image and TVS2200DRVR. ARC-0002 consumes the fixed 5/9/15-V
contracts, direct S3 USB2, shared I2C/IRQ status, charge-disable defaults and
signed dual-region PD-image recovery. Hardware `DEC-0068/PWR-0008/REV-0005Y`
now add four separate fixed rails: autonomous low-IQ `AON_SAFE_3V3`,
`3V3_MAIN`, independent `VVOICE_4V` and reverse-blocked/protected 5-V accessory
power. Exact TPS22919 branches gate nRF, CC1101, microSD, ES8311 and Si4732;
the runtime contract consumes reset-off defaults, PG/fault sequencing and
measured-discharge gates without inventing programmable rail voltages.
Hardware `PWR-0011/DEC-0072/REV-0005AC` now also fixes the 24 converter
energy/configuration/feedback parts. Firmware gains no voltage-setting API:
the nominal 3.318/4.000/5.000-V outputs and their qualification evidence are
read-only hardware facts. Hardware `PWR-0012/DEC-0073/REV-0005AD` first fixes
the direct AON EN strap and nine converter EN/PG/qualifier/fault resistors.
`FND-0084/PWR-0019/DEC-0080/REV-0005AK` then amend that profile to ten
positions and replace the hidden sequencer placeholder with direct
SYS-to-AON, AON-PG/MR, 3.07-V SENSE/CT/POR and main-EN wiring. Firmware cannot
bypass the delayed hardware POR. The source budget reserves the larger of
declared or measured-plus-margin system load from 85% of negotiated input
power and sets charge to zero on missing/DPM/thermal/fault evidence. Complete
transition/rail/thermal/fault HIL remains upstream I3 work.
`FND-0085/PWR-0020/DEC-0081/REV-0005AL` then split AON, main and voice raw
converter outputs from their loads with independent exact cutoffs. Firmware
uses protected-side PG only, revokes leases on a latch fault, offers no eFuse
bypass/reset API and requires a fresh validated power session; persistent
main faults need complete source removal, while AON hardware owns bounded
auto-retry and cannot release compute before stable PG/SENSE/CT. Hardware
`FND-0086/PWR-0021/DEC-0082/REV-0005AM` then review the consolidated I3
source/heat/fault ledger and activate I4 paper work. Firmware may consume those
exact contracts, but cell/holder procurement and received-lot, transition,
rail, destructive-fault and thermal HIL remain upstream evidence; no measured
threshold or production qualification is inferred.
`FND-0087/USB-0001/DEC-0083/REV-0005AN` now close the first I4 endpoint with
exact four-line product-port protection. ARC-0002 consumes automatic
disconnect, sink-only/no-Alt-Mode behavior and protected native S3 USB2 while
keeping direct `FLT` fixture-only and USB Full-Speed RC/SI, ESD/short HIL
upstream.
`FND-0088/DSP-0006/DEC-0084/REV-0005AO` then close the display paper
electrical endpoint. ARC-0002 consumes reset-low defaults, 120-ms display and
100-ms touch post-release waits, backlight-last startup and no automatic retry
after a latch fault. The first ZIF candidate remains a physical-HIL input and
the fixture-only backlight fault point is not exposed as a firmware sensor.
`FND-0089/STO-0001/DEC-0085/REV-0005AP` then close the isolated microSD paper
endpoint. ARC-0002 consumes always-readable detect, fail-low switched power,
SPI-mode-first admission, card-CS-gated DAT0/MISO, clean drain/unmount and
explicit unexpected-removal recovery. Media/endurance, final timing/RC,
throughput/contention and fault/corruption HIL remain upstream evidence.
Hardware
`PWR-0013/FND-0078/DEC-0074/REV-0005AE` then
fixes the 10-Ohm pre-admission load, independent non-retriggerable timer and
exact PA25/PA26 divider/filter frontends. Its C0G timing network has a
28.7-40.7-ms paper window and production accepts only measured 25-50-ms
pulses. Firmware emits one PA22 edge, samples against the internal 1.4-V
reference only after `>=10 ms` settling and cannot extend the pulse;
production thresholds remain exact-cell HIL inputs. Hardware
`PWR-0017/FND-0082/DEC-0078/REV-0005AI` corrects the TPUL WQFN pin map,
cascades channel 2 into a measured 350-860-ms hardware refractory interval
and splits the 10-Ohm load across two 20-Ohm/2-W branches. Firmware waits
`>=1 ms` after stable admission VDD and `>=10 s` between normal attempts; it
cannot shorten the hardware bound or infer a missing load branch. Hardware
`PWR-0014/DEC-0075/REV-0005AF` then fixes the BQ25798 2S/750-kHz strap,
2.2-uH/7-A inductor, complete physical capacitor banks, BATP/TS/ILIM, local
pulls, reset-high open-drain CE and Rev-C special-pin terminations. Runtime
therefore starts from 1-A reset charge, writes contract-derived IINDPM before
CE, never exceeds 2-A charge and never ignores the independent BQ TS sensor.
`FND-0079` returns product USB-C/USB2 protection to dependent hardware I4;
hardware `FND-0080/PWR-0015/DEC-0076/REV-0005AG` then fixes separate raw
VBUS/VBUS_IN startup, hardware SafeMode, 17 exact TPS/EEPROM support parts,
open-drain WP and both complete I2C pull networks. Firmware consumes that
ordering without claiming TPS performs a fresh owner-signature check. Hardware
`DEC-0069/REV-0005Z` additionally correct the external eFuse to exact
latch-off `TPS259470LRPWR`: firmware may not restore it in a retry loop after
`FLT`, and a new user action follows physical fault removal. Hardware
`PWR-0009/DEC-0070/REV-0005AA` also qualifies optional voice/accessory PG with
the matching safe EN. Runtime therefore treats `EN=0, PG=0` as normal off and
`EN=1, PG=0` as bounded startup pending followed by a latched timeout, instead
of interpreting every disabled optional rail as a fault. Hardware
`PWR-0010/DEC-0071/REV-0005AB` then correct the eFuse transient model and close
its eight exact passives: current limit is active immediately at startup,
`dVdt` controls the ramp, and 2 A is only a bounded post-start excursion.
Runtime also treats OVLO recovery as a new admission because it bypasses the
normal ramp. Hardware
`PWR-0005/FND-0075` prove that gauge and
pre-closure loose-cell admission are separate jobs; `PWR-0006/FND-0076` retain
the controlled-1S cross-charge, rail/current and SOC consequences as future
variant evidence. Hardware `DEC-0066/REV-0005V` accept exact
MAX17320G20+T plus MSPM0C1104SDGS20R: the MSP owns local admission and becomes
a fourth independently recoverable image domain; S3 sees only bounded
read-only state/fault and cannot override refusal.
Hardware `DEC-0067/REV-0005X` additionally disable in-product zero-volt and
linear-prequalification recovery, accept the exact fully-switching pack path
and originally propose PA24/PA25 as midpoint/full-stack evidence. Hardware
`FND-0078/DEC-0074` correct the live map to PA25/PA26 because PA24 permits no
injection current. Firmware refuses a
deep cell and exposes no recovery command; any recovery research is a separate
isolated Controlled-Zone fixture operation.
Hardware `DEC-0052/REV-0004X` additionally make direct QSPI on S3 GPIO41/42
and `<=1 ms` display occupancy reviewed runtime inputs. Hardware
`DEC-0053/REV-0004Z` accept the 3.5-inch portrait `320×480` IPS QSPI+touch
class and two HIL controller profiles. Hardware `DSP-0005/REV-0005A` now
instantiate exact current assembly candidate `HMX035CTFT-001`; slow P06/P07
terminate display/touch reset. `DEC-0086` later moves touch IRQ to shared
GPIO37 and uses GPIO39/GPIO47 for encoder PCNT0; audio `DEC-0054` retains
GPIO6. ARC-0002 still freezes
the scheduler/pin/resource and `DEC-0084` reset/backlight-fault contract:
production ordering/drawing, final connector, specimen electrical HIL and
vendor init table remain open.
Hardware `STO-0001/DEC-0085/REV-0005AP` also close the paper storage endpoint
without a GPIO change. ARC-0002 freezes card-power/session sequencing and
clean-versus-unexpected-removal semantics, while socket access, media set,
throughput, hot-removal and corruption evidence remain open.
Hardware `AUDIO-0001/REV-0005B` additionally instantiate exact `ES8311`
QFN-20 digital contacts: address `0x19`, no separate MCLK GPIO and external
P10 `CODEC_PWR_EN` instead of the former fictional codec reset/enable.
`FND-0065/0066` show why PAM8302A can take differential audio while the ES8311
ADC is documented as microphone-oriented rather than a recommended line input. Hardware
`AUDIO-0002/REV-0005C/FND-0067` add the missing P27 RX-source control and
compare the complete high-Z capture, differential playback, attenuated TX and
reset-default paths. `DEC-0054/REV-0005D` accept option A and machine-allocate
direct GPIO6 as `AUDIO_ARM`, changing S3 to the then-current `32/3/1`;
`DEC-0086` later closes it to `33/3/0` for encoder capture. Firmware may now freeze
safe control sequencing, but not unmeasured gain/mute/passive values.

After hardware `FLOW-0001/G7`, this repository will derive and review a new
runtime/HAL/toolchain contract from the selected complete architecture. No
implementation may silently make that decision first.
