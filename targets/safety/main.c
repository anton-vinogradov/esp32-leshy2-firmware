#include "leshy2/safety_core.h"
#include "leshy2/r2/hardware/safety_bsp.h"
#include "ti_msp_dl_config.h"

#include <stdint.h>
#include <ti/devices/msp/msp.h>

/* Keep the target fail-closed until a reviewed target safety limit is published. */
enum {
    L2_UNCONFIGURED_TEMPERATURE_LIMIT_DECI_C = 0,
};

static l2_safety_t safety_supervisor;

int main(void)
{
    SYSCFG_DL_init();
    if (l2_r2_safety_domain.mapping != L2_R2_MAPPING_EXACT_PINS ||
        l2_r2_safety_domain.pin_count != UINT16_C(17)) {
        __disable_irq();
        for (;;) {
            __WFI();
        }
    }
    l2_safety_init(
        &safety_supervisor,
        INT16_C(L2_UNCONFIGURED_TEMPERATURE_LIMIT_DECI_C)
    );
    for (;;) {
        __WFI();
    }
}
