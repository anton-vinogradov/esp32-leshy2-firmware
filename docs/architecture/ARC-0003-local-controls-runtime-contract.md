# ARC-0003 — local-controls runtime contract

- Status: **reviewed upstream runtime input; implementation not started**
- Hardware input: [`DEC-0086`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/decisions/DEC-0086-complete-local-controls-and-direct-encoder.md)
- Hardware topology: [`UI-0001`](https://github.com/anton-vinogradov/esp32-leshy2/blob/main/docs/review/architecture/UI-0001-complete-local-control-topology.md)

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
columns; P7 is reserved. Exact pull-downs keep every row low during reset, and
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
controller, TPS25751 and pack admission. It repeats status reads until the qualified line
release condition or a bounded fault is reached. A stuck source is named and
isolated by its owning policy where hardware permits; it is not hidden by
polling.

The populated touch adapter determines whether raw TP_INT is inverted. The
driver profile records that hardware population and validates idle/asserted
levels at startup. A mismatch disables touch with an explicit fault while
physical buttons and STOP remain usable.

## PTT, STOP and RE-ARM

- RP GPIO21 owns physical PTT edges and local debounce/dead-man behavior. PTT
  is effective only in an armed foreground voice lease; matrix/touch/phone
  events cannot synthesize it.
- STOP is asynchronous hardware. Firmware only reconstructs and displays the
  latched cause after reset; no task, queue or I²C transaction precedes it.
- Releasing STOP does nothing. Only a fresh physical RE-ARM edge after safe
  checks permits a new TX-off session; it never restores prior context.

This contract is an upstream paper input, not a HAL implementation or a claim
that switch/touch/encoder HIL has passed.
