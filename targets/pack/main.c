#include "leshy2/safety_core.h"
#include "leshy2/hardware/pack_bsp.h"
#include "ti_msp_dl_config.h"

#include <stdint.h>
#include <ti/devices/msp/msp.h>

static l2_safety_t pack_admission;

int main(void)
{
    SYSCFG_DL_init();
    if (l2_hw_pack_domain.pin_count != (uint16_t)L2_HW_PACK_PIN_COUNT) {
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
