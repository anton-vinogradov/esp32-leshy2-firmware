#include "leshy2/evidence_register.h"

uint16_t l2_evidence_decode_tca9535(uint8_t port0, uint8_t port1)
{
    const uint16_t raw = (uint16_t)((uint16_t)port0 | ((uint16_t)port1 << 8));
    const uint16_t asserted = (uint16_t)~raw & L2_EVIDENCE_TCA9535_RAW_MASK;
    /* Physical P17 is raw bit 15; U219 EV9 retains logical ABI bit 12. */
    return (uint16_t)((asserted & UINT16_C(0x01ff)) | ((asserted & UINT16_C(0x8000)) >> 3));
}

bool l2_evidence_tca9535_readback_valid(uint16_t configuration, uint16_t polarity)
{
    return (configuration & L2_EVIDENCE_TCA9535_REQUIRED_INPUT_MASK) ==
               L2_EVIDENCE_TCA9535_REQUIRED_INPUT_MASK &&
           (polarity & L2_EVIDENCE_TCA9535_RAW_MASK) == 0;
}
