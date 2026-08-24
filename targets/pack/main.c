#include "leshy2/safety_core.h"
#include "ti_msp_dl_config.h"

#include <stdint.h>
#include <ti/devices/msp/msp.h>

static l2_safety_t pack_admission;

int main(void)
{
    SYSCFG_DL_init();
    l2_safety_init(&pack_admission, INT16_C(700));
    for (;;) {
        __WFI();
    }
}
