#include <ti/devices/msp/msp.h>

int main(void)
{
    __disable_irq();
    for (;;) {
        __WFI();
    }
}
