#include "pico/stdlib.h"
#include "leshy2/r2/hardware/rf_rp_bsp.h"

#include <stdint.h>

enum {
    L2_RF_RP_IMAGE_IDENTITY = UINT32_C(0x52465250),
};

static volatile uint32_t image_identity = L2_RF_RP_IMAGE_IDENTITY;

int main(void)
{
    for (;;) {
        if (image_identity != L2_RF_RP_IMAGE_IDENTITY ||
            l2_r2_rf_rp_domain.mapping != L2_R2_MAPPING_EXACT_PINS ||
            l2_r2_rf_rp_domain.pin_count != UINT16_C(48)) {
            return 1;
        }
        tight_loop_contents();
    }
}
