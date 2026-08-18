# EXT-0001 — M5 expansion runtime state machine

Status: **reviewed firmware input; implementation and physical HIL blocked**.

This document consumes hardware `DEC-0098/EXP-0001`. It does not authorize a
HAL implementation before the atomic architecture package.

## Independent branch state

The U214 and native-Unit branches each own this state machine:

```text
OFF -> REQUESTED -> POWER_PENDING -> READY -> IDENTIFY -> ACTIVE
 ^                                                    |
 +--------- QUIETING <--------------------------------+
                         any powered state -> FAULT_LATCHED
```

- `OFF`: request low, eFuse disabled/discharged, isolation disabled, no poll.
- `REQUESTED`: an exact signed accessory/profile manifest and explicit session
  exist; changing either aborts to OFF.
- `POWER_PENDING`: common buck and only the selected eFuse are requested;
  converter PG and branch READY have bounded deadlines.
- `READY`: protected 5 V and host 3.3 V are valid; signal isolation may be
  enabled in safe parked state.
- `IDENTIFY`: profile-specific identity/readback, pull/timing and current/fault
  evidence are checked. There is no generic presence bit.
- `ACTIVE`: only manifest-declared protocols and signal-group members run.
- `QUIETING`: stop work, park controllers/pins, disable isolation, remove the
  branch request, wait measured discharge/no-back-power, then OFF.
- `FAULT_LATCHED`: disable signals and request, revoke relevant leases, preserve
  evidence and require a fresh explicit session. No automatic power retry.

## U214-specific gates

`U214_READY` qualifies nine SPI/UART/control directions. TCA4307 `READY` is a
second fact for I²C segment connection/recovery, not a substitute for protected
power readiness. RP must keep PIO1, UART1 and I²C0 stopped before both relevant
gates are valid. U214 downstream Port A load and identity are part of the same
manifest/current envelope.

## Native-Unit-specific gates

`UNIT_READY` is read on slow P26 and permits TXS0102 OE. A profile explicitly
selects I²C, UART, push-pull/open-drain GPIO or qualified 1-Wire behavior. The
two-wire port cannot auto-detect protocol safely. 1-Wire remains disabled until
an exact Unit/cable profile passes electrical and timing HIL.

## Required event evidence

Every transition records branch, manifest hash, reason, request generation,
converter PG, branch READY, eFuse fault, identity result, timeout and discharge
result. Reverse-source/external-power evidence is a fault even when the remote
device otherwise responds correctly.

## Concurrency

U214 and native Unit may be powered together only when one exact combined
manifest passed total buck/eFuse/thermal and no-stall HIL. This does not relax
the one-top-level-signal-group rule: protocol support/power presence is not
permission for cross-group RF activity.

