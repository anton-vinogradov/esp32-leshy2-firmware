#include "leshy2/l2ip.h"
#include "leshy2/r2/hardware/c5_bsp.h"

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wundef"
#include "esp_chip_info.h"
#include "esp_log.h"
#pragma GCC diagnostic pop

#include <stdint.h>
#include <stdlib.h>

static const char *const TAG = "leshy2_c5";
static l2ip_replay_guard_t replay_guard;

void app_main(void)
{
    esp_chip_info_t chip = {0};
    esp_chip_info(&chip);
    if (l2_r2_c5_domain.mapping != L2_R2_MAPPING_EXACT_PINS ||
        l2_r2_c5_domain.pin_count != UINT16_C(14)) {
        ESP_LOGE(TAG, "reviewed H2 C5 BSP boundary is incomplete");
        abort();
    }
    l2ip_replay_guard_reset(&replay_guard, UINT32_C(0));
    ESP_LOGI(
        TAG,
        "skeleton ready: %u cores, R2 mapping kind %u; native RF/IR remain unconfigured",
        (unsigned int)chip.cores,
        (unsigned int)l2_r2_c5_domain.mapping
    );
}
