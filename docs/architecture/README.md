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
the ordered ESP32-DIV `L0` pre-HIL observer from target Leshy2 `T1`, with
measurements still pending.

After hardware `FLOW-0001/G7`, this repository will derive and review a new
runtime/HAL/toolchain contract from the selected complete architecture. No
implementation may silently make that decision first.
