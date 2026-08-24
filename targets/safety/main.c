#include "leshy2/safety_core.h"
#include "ti_msp_dl_config.h"

#include <stdint.h>
#include <ti/devices/msp/msp.h>

/* F2.3 replaces this fail-closed placeholder with the generated H2 limit. */
enum {
    L2_UNCONFIGURED_TEMPERATURE_LIMIT_DECI_C = 0,
};

static l2_safety_t safety_supervisor;

int main(void)
{
    SYSCFG_DL_init();
    l2_safety_init(
        &safety_supervisor,
        INT16_C(L2_UNCONFIGURED_TEMPERATURE_LIMIT_DECI_C)
    );
    for (;;) {
        __WFI();
    }
}
