#include "leshy2/l2ip.h"

#include "esp_chip_info.h"
#include "esp_log.h"

#include <stdint.h>

static const char *const TAG = "leshy2_c5";
static l2ip_replay_guard_t replay_guard;

void app_main(void)
{
    esp_chip_info_t chip = {0};
    esp_chip_info(&chip);
    l2ip_replay_guard_reset(&replay_guard, UINT32_C(0));
    ESP_LOGI(
        TAG,
        "skeleton ready: %u cores; native RF/IR remain unconfigured",
        (unsigned int)chip.cores
    );
}
