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
MPN. Open `IMP-0043` would require explicit profiled-kit identity, disarm on
profile changes and TX denial for unknown/mismatch. Exact two-source hardware
and measurements remain pending under `FND-0058`.

Hardware `PIN-0003/REV-0004V` now review the machine-generated principled
owner/net/pad atlas. Current direct budgets are S3 `32/3/1`, C5 `14/6/1`, RP
`48/0/0` and slow I/O `24/0/0`; exact SA518 service and Si4732 control/antenna
contacts are represented. This is a reviewed paper input, not final electrical
closure: hardware `FND-0060` keeps the remaining exact peripheral, safety,
power, isolation and service endpoints open.
Hardware `DEC-0051` publishes the same projection in its target README as the
visible G3 working design; firmware still treats it as reopenable upstream
input until atomic architecture.
Hardware `DEC-0052/REV-0004X` additionally make direct QSPI on S3 GPIO41/42
and `<=1 ms` display occupancy reviewed runtime inputs. Hardware
`DEC-0053/REV-0004Z` accept the 3.5-inch portrait `320×480` IPS QSPI+touch
class and two HIL controller profiles. Hardware `DSP-0005/REV-0005A` now
instantiate exact current assembly candidate `HMX035CTFT-001`; GPIO39 is touch
IRQ and slow P06/P07 terminate display/touch reset; later audio `DEC-0054`
uses GPIO6 and changes the total S3 budget to `32/3/1`. ARC-0002 still freezes
only the scheduler/pin/resource contract: production ordering/drawing/
connector and vendor init table remain open.
Hardware `AUDIO-0001/REV-0005B` additionally instantiate exact `ES8311`
QFN-20 digital contacts: address `0x19`, no separate MCLK GPIO and external
P10 `CODEC_PWR_EN` instead of the former fictional codec reset/enable.
`FND-0065/0066` show why PAM8302A can take differential audio while the ES8311
ADC is documented as microphone-oriented rather than a recommended line input. Hardware
`AUDIO-0002/REV-0005C/FND-0067` add the missing P27 RX-source control and
compare the complete high-Z capture, differential playback, attenuated TX and
reset-default paths. `DEC-0054/REV-0005D` accept option A and machine-allocate
direct GPIO6 as `AUDIO_ARM`, changing S3 to `32/3/1`. Firmware may now freeze
safe control sequencing, but not unmeasured gain/mute/passive values.

After hardware `FLOW-0001/G7`, this repository will derive and review a new
runtime/HAL/toolchain contract from the selected complete architecture. No
implementation may silently make that decision first.
