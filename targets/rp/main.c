#include "leshy2/l2ip.h"
#include "leshy2/hardware/rp_bsp.h"

#include "pico/stdlib.h"

#include <stdint.h>

static l2ip_replay_guard_t replay_guard;

int main(void)
{
    if (l2_hw_rp_domain.pin_count != (uint16_t)L2_HW_RP_PIN_COUNT) {
        return 1;
    }
    l2ip_replay_guard_reset(&replay_guard, UINT32_C(0));
    for (;;) {
        tight_loop_contents();
    }
}
