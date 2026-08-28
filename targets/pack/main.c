#include "leshy2/safety_core.h"
#include "leshy2/r2/hardware/pack_bsp.h"
#include "ti_msp_dl_config.h"

#include <stdint.h>
#include <ti/devices/msp/msp.h>

static l2_safety_t pack_admission;

int main(void)
{
    SYSCFG_DL_init();
    if (l2_r2_pack_domain.mapping != L2_R2_MAPPING_IDENTITY_ONLY) {
        __disable_irq();
        for (;;) {
            __WFI();
        }
    }
    l2_safety_init(&pack_admission, INT16_C(700));
    for (;;) {
        __WFI();
    }
}
