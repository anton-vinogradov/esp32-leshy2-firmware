# SVC-0001 — service and recovery runtime contract

Status: **reviewed firmware input; implementation and physical HIL blocked**.

This document consumes hardware `SVC-0002/DEC-0099`. It defines observable
software and fixture behavior; it does not make firmware part of the physical
BOOT, RESET, SWD or hard-STOP path and does not authorize HAL implementation
before the atomic architecture package.

## Independent paths

| Domain | Normal service data | Keyed DBG10 | Physical controls |
|---|---|---|---|
| S3 | protected product USB Serial/JTAG | UART0 GPIO43/44, EN, GPIO0; passive ID `00` | separate RESET and BOOT |
| C5 | independent data-only USB on GPIO13/14 | UART0 GPIO11/12, CHIP_PU, GPIO28; passive ID `01` | separate RESET and BOOT; GPIO27 remains fixed high/read-only |
| `SC1512-A4` (`RP2354B0A4`) | independent data-only USB on package DP/DM | SWDIO, SWCLK, RUN, USB_BOOT; passive ID `10` | separate RESET and BOOT |

No path needs a healthy peer or application image. C5/RP USB data exists only
while the board powers its fixed HSD1 isolation switch. Their connector VBUS
does not power the product and is not a firmware-controlled source. DBG10 ID
and VTREF are fixture inputs, not MCU GPIO or software identity claims.

## Runtime-observable state

```text
SAFE_TX_OFF -> ATTACH_DIAGNOSTIC -> SERVICE_REQUESTED -> SERVICE_ACTIVE
     ^                |                    |                  |
     +----------------+--------------------+---- VERIFY/RESET-+
                 any invalid/fault event -> SAFE_TX_OFF + FAULT_EVIDENCE
```

- `SAFE_TX_OFF`: default after boot/reset/update/recovery; no prior arm, target,
  power or lease survives.
- `ATTACH_DIAGNOSTIC`: a USB attach or service-channel activity may be logged,
  but cannot itself open a menu, arm TX, select Laboratory mode or authorize an
  update.
- `SERVICE_REQUESTED`: an explicit local-owner action selects one domain and
  one operation. Normal signed update verifies target/profile before transfer.
- `SERVICE_ACTIVE`: affected leases are revoked globally, signal groups quiet,
  power is qualified and only the bounded service channel runs.
- `VERIFY/RESET`: hashes/readback/rollback state are recorded, then the target
  resets into `SAFE_TX_OFF`. A failed or interrupted verification remains
  recoverable and never falls back to an unsigned normal boot.
- `FAULT_EVIDENCE`: unexpected disconnect, invalid target, STOP, brownout,
  watchdog, fixture fault or inconsistent identity closes the session and
  preserves reason/evidence where a running domain remains.

Physical ROM/SWD recovery can proceed when application firmware is absent, so
it cannot depend on this state machine. The same safety result is enforced by
hardware/fixture ordering: no TX permission exists, STOP dominates reset and
the recovered image must begin from a new TX-off session.

## Fixture admission

The external fixture follows this mandatory order:

Passive `ID1:ID0` codes are `00=S3`, `01=C5`, `10=RP`, `11=invalid`.

1. hold RESET, BOOT and debug drivers high-Z;
2. establish ground, then measure VTREF through pin 1;
3. read passive `ID1:ID0`; `11`, unstable or mismatched ID means detach/high-Z;
4. select only the domain-specific voltage/protocol and keep all other headers
   high-Z;
5. assert RESET/BOOT only by pulling low; never drive these pins high;
6. use UART/SWD only inside its configured current/drive limit;
7. release BOOT before RESET for normal restart, stop driving debug and verify
   a fresh TX-off boot;
8. on STOP, brownout, overcurrent, ESD symptom, attach loss or disagreement,
   return every drive high-Z immediately.

For C5 Joint Download Boot 0 the fixture preserves GPIO27 high, pulls GPIO28
low and toggles CHIP_PU before USB/UART. For RP USB BOOT it uses the physical
1-kΩ USB_BOOT path; SWD remains the independent second recovery method.

## Security and openness

Normal field updates remain owner-signed, target-bound, rollback-protected and
sequential. This prevents a corrupt/malicious package from becoming the normal
boot image. It does not close the device: reproducible/offline signing remains
available to the owner, intentional physical recovery can install owner-built
firmware, and irreversible secure-boot/eFuse/OTP lockdown is not the default.

Service attach is not authorization. Laboratory and Controlled-Zone rules,
the per-entry warning, legal/technical manifests and hard STOP remain in force.
No service command can create a lease, bypass antenna/profile checks or revive
a lease that existed before reset.

## Required evidence

- erased, corrupt, wrong-target and interrupted-image recovery on each path;
- invalid/unstable DBG10 ID, no/incorrect VTREF and fixture-overdrive handling;
- held or misordered buttons, simultaneous USB hosts and repeated attach/reset;
- C5/RP board-off D-line leakage and no VBUS power/backfeed;
- STOP/AON loss at every fixture step and verified TX-off first boot;
- event completeness: domain, physical path, reset cause, manifest/hash,
  verifier result, fixture ID, STOP state and final safe-state reason.
