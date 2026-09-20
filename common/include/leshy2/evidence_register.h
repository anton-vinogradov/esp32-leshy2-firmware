#ifndef LESHY2_EVIDENCE_REGISTER_H
#define LESHY2_EVIDENCE_REGISTER_H

#include <stdbool.h>
#include <stdint.h>

#define L2_EVIDENCE_TCA9535_RAW_MASK UINT16_C(0x81ff)
#define L2_EVIDENCE_LOGICAL_MASK UINT16_C(0x11ff)
#define L2_EVIDENCE_TCA9535_REQUIRED_INPUT_MASK UINT16_C(0xe3ff)

/* Pure host-tested adapter, not compiled into current SDK targets or connected
 * to a target driver. Port 0 is the low byte. Readback must be fresh and
 * successful; a true result proves only these supplied bit patterns.
 * Evidence inversion bits must be zero before decoding active-low input bytes.
 * Only service P12/P13/P14 may be outputs; this does not authorize their state.
 * Decoded output uses the asserted-high logical ABI of l2_safety_set_evidence.
 * No helper proves physical GPIO/pull modes, bus integrity or electrical safety.
 */
uint16_t l2_evidence_decode_tca9535(uint8_t port0, uint8_t port1);
bool l2_evidence_tca9535_readback_valid(uint16_t configuration, uint16_t polarity);

#endif
