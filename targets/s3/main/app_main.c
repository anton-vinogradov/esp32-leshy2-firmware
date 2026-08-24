#include "leshy2/system_model.h"
#include "leshy2/hardware/s3_bsp.h"

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
        "skeleton ready: %u cores, %u reviewed contacts; RF domains remain held",
        (unsigned int)chip.cores,
        (unsigned int)l2_hw_s3_domain.pin_count
    );
}
