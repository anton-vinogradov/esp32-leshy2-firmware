# ARC-0003 — local-controls runtime contract

- Status: **reviewed upstream runtime input; implementation not started**
- Hardware inventory/pin input: [`DEC-0086`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0086-complete-local-controls-and-direct-encoder.md)
- Hardware electrical input: [`DEC-0087`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0087-exact-control-switch-and-protection-endpoint.md)
- Exact hardware topology: [`UI-0002`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/UI-0002-exact-switch-and-control-protection.md)
- Consolidated I4 input: [`IOX-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/IOX-0001-consolidated-i4-electrical-closure.md)

## Stable logical controls

The event API preserves these independent physical identities:

- `DPAD_UP`, `DPAD_DOWN`, `DPAD_LEFT`, `DPAD_RIGHT`, `OK`;
- `BACK`, `OPT`, `F1`, `F2`;
- `ENCODER_CW`, `ENCODER_CCW`, `ENCODER_PUSH`;
- `PTT_PRESS`, `PTT_RELEASE`;
- observed `STOP_LATCHED` and fresh `REARM_EDGE` state transitions.

Touch gestures and paired-phone text are separate sources. They may invoke the
same high-level command only after normal UI policy checks; they never erase a
physical source identity and never synthesize PTT, STOP or RE-ARM.

## 4×3 matrix service

Dedicated TCA9534A at candidate address `0x3F` uses P0…P3 as rows and P4…P6 as
columns; P7 is a protected fixture/growth test pad, not a missing product
control. Exact pull-downs keep every row low during reset, and
firmware holds every row low in idle, so any press pulls one column low and
asserts `INT_N`. Before changing P0…P3 from reset inputs to outputs, firmware
must first write their output latches low; it must not expose the reset-default
high latch as an all-high idle state. Firmware then starts one bounded scan: the selected row stays
low while the other three are driven high, P4…P6 are sampled, and all rows
return low after the fourth row. The coordinate map is:

| Row | Col 0 | Col 1 | Col 2 |
|---|---|---|---|
| 0 | UP | DOWN | LEFT |
| 1 | RIGHT | OK | BACK |
| 2 | OPT | F1 | F2 |
| 3 | ENCODER_PUSH | unused | unused |

Each of the nine ordinary positions is a separate exact `C&K Y78B23214FP`
ultra-low-current switch; F1 and F2 therefore remain independent physical
inputs rather than aliases or touch-only commands. `TPD8E003DQDR` protects
P0…P7 individually, including the reserved position, without changing the
logical coordinate map.

Debounce state is per physical position. Multiple simultaneous positions are
never collapsed into an invented third key. A complete scan and first visible
ordinary response remain within 100 ms under the qualified worst-case system
load. No matrix failure may assert PTT or alter the hardware STOP latch.

## Encoder service

S3 PCNT0 captures GPIO39=A and GPIO47=B independently of I²C. The driver
accepts valid Gray transitions, resolves direction and publishes only a
qualified full-detent event. Counter overflow, invalid transition, excessive
chatter or impossible rate increments diagnostics instead of inventing motion.

PCNT hardware filtering is only the first rejection layer. HIL must prove
fastest intended manual rotation, stationary chatter, EMI, temperature and
simultaneous display dirty-region, microSD and active-signal-group load with no
lost or invented detents.

## Shared interrupt and touch

GPIO37 is a wired-low wake hint, not a unique source identity. On every wake
the service loop reads all enabled sources: main TCA6424, UI TCA9534A, touch
controller, TPS25751 and pack admission. Exact integrated `Sitronix ST77922`
touch is a SYS-I2C target at 7-bit address `0x38`, no faster than 400 kHz. It
repeats status reads until the qualified line
release condition or a bounded fault is reached. A stuck source is named and
isolated by its owning policy where hardware permits; it is not hidden by
polling.

The main `TCA6424ARGJR` responds at exact 7-bit address `0x22`; pack admission
responds at fixed firmware target `0x2A`. Startup verifies the expander
identity/default-input state. A stuck bus receives bounded clock/STOP recovery;
an unrecoverable main expander enters explicit safe/degraded service and asks
the power manager for a full `3V3_MAIN` cycle. Runtime never pretends that the
fixture-only `SLOW_IO_RESET_N` pad is an MCU output.

P22 observes the AON STOP latch as low=RUN/high=latched STOP. P23 observes S3
RF evidence as active low. Separate open-drain domain buffers preserve those
polarities, so no compatibility profile is needed. Both are diagnostics only:
writing an expander register cannot clear STOP, arm TX or replace the physical
evidence path.

The exact assembly contract defines active-low TP_INT. Its 10-kOhm raw pull-up
and fixed non-inverting `SN74LVC1G07DCKR` produce an open-drain contribution;
firmware has no polarity/population profile and never supports the removed
inverting alternative. Startup verifies expected controller readback, address,
idle/asserted levels and reset recovery. A mismatch disables touch with an
explicit fault while physical buttons and STOP remain usable.

## PTT, STOP and RE-ARM

- A separate exact `C&K Y78B23214FP` PTT switch pulls the raw line low. Its
  10-kOhm pull-up, 100-nF filter, `TPD4E05U06DQAR` ESD channel and 1-kOhm
  series resistor terminate directly on RP GPIO21. RP owns both physical
  edges and local debounce/dead-man behavior; scan, I²C, touch and phone input
  are not in this path and cannot synthesize PTT. PTT is effective only in an
  armed foreground voice lease, and a qualified release or loss/fault revokes
  the request locally.
- Exact `Panasonic AEQ10410` COM+NC is the hard-STOP loop. Its 10-kOhm AON
  pull-up and 10-nF filter make press, connector loss or an open wire assert
  STOP. A dedicated `TPD4E05U06DQAR` returns only to safety ground. STOP
  remains asynchronous hardware: firmware neither debounces nor gates its
  assertion and only reconstructs/displays the latched cause after reset.
- A separate recessed `C&K Y78B23214FP` with a 47-kOhm AON pull-up, 100-nF
  filter and the dedicated safety ESD array provides RE-ARM. Releasing STOP
  does nothing. Only a fresh physical RE-ARM edge after safe checks permits a
  new TX-off session; it never restores prior context.

The switch data-sheet bounce limit is an input to the initial driver profile,
not permission to hard-code final debounce timing. HIL must qualify press and
release latency, contact chatter, stuck/open/short lines, ESD, simultaneous
matrix positions and PTT loss while the full system is loaded. Diagnostics
name the raw source and protection/fault path without turning a software event
into a physical control.

This contract is an upstream paper input, not a HAL implementation or a claim
that control/touch/encoder HIL has passed.
