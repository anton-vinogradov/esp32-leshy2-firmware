#include "pico/stdlib.h"

#include <stdint.h>

enum {
    L2_RF_RP_IMAGE_IDENTITY = UINT32_C(0x52465250),
};

static volatile uint32_t image_identity = L2_RF_RP_IMAGE_IDENTITY;

int main(void)
{
    for (;;) {
        if (image_identity != L2_RF_RP_IMAGE_IDENTITY) {
            return 1;
        }
        tight_loop_contents();
    }
}
