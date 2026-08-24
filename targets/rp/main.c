#include "leshy2/l2ip.h"

#include "pico/stdlib.h"

#include <stdint.h>

static l2ip_replay_guard_t replay_guard;

int main(void)
{
    l2ip_replay_guard_reset(&replay_guard, UINT32_C(0));
    for (;;) {
        tight_loop_contents();
    }
}
