#include "leshy2/system_model.h"

#include "esp_chip_info.h"
#include "esp_log.h"

#include <stdint.h>

static const char *const TAG = "leshy2_s3";
static l2_system_model_t system_model;

void app_main(void)
{
    esp_chip_info_t chip = {0};
    esp_chip_info(&chip);
    l2_system_model_init(&system_model, INT16_C(700), UINT32_C(0));
    ESP_LOGI(
        TAG,
        "skeleton ready: %u cores; RF domains remain held",
        (unsigned int)chip.cores
    );
}
