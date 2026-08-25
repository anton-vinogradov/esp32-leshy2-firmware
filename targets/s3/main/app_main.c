#include "leshy2/system_model.h"
#include "leshy2/hardware/s3_bsp.h"

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wundef"
#include "esp_chip_info.h"
#include "esp_log.h"
#pragma GCC diagnostic pop

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>

static const char *const TAG = "leshy2_s3";
static l2_system_model_t system_model;

static bool all_builds_equal(const l2_update_t *update, uint32_t expected)
{
    for (size_t index = 0; index < L2_UPDATE_DOMAIN_COUNT; ++index) {
        if (update->active_build[index] != expected) {
            return false;
        }
    }
    return true;
}

static bool self_test_pass_path(void)
{
    l2_update_t update;
    l2_update_init(&update, UINT32_C(100));
    if (!l2_update_begin(&update, true, true, true, true, UINT32_C(0))) {
        return false;
    }
    for (size_t index = 0; index < L2_UPDATE_DOMAIN_COUNT; ++index) {
        if (!l2_update_stage(
                &update,
                (l2_update_domain_t)index,
                UINT32_C(101),
                true
            )) {
            return false;
        }
    }
    if (!l2_update_verify_bundle(&update)) {
        return false;
    }
    for (size_t index = 0; index < L2_UPDATE_DOMAIN_COUNT; ++index) {
        const l2_update_domain_t domain = (l2_update_domain_t)index;
        if (!l2_update_activate(&update, domain, UINT32_C(1) + (uint32_t)index) ||
            !l2_update_report_self_test(&update, domain, true)) {
            return false;
        }
    }
    return l2_update_commit(&update, UINT32_C(10)) &&
        update.phase == L2_UPDATE_COMMITTED &&
        all_builds_equal(&update, UINT32_C(101));
}

static bool retained_first_fault_path(void)
{
    l2_system_model_t model;
    l2_system_model_init(&model, INT16_C(700), UINT32_C(100));
    l2_safety_set_temperatures(
        &model.safety,
        true,
        INT16_C(250),
        INT16_C(250),
        INT16_C(250)
    );
    if (!l2_system_model_set_run(&model, true, UINT32_C(0)) ||
        !l2_system_model_heartbeat(&model, UINT32_C(1), UINT32_C(0))) {
        return false;
    }
    l2_safety_set_temperatures(
        &model.safety,
        true,
        INT16_C(250),
        INT16_C(701),
        INT16_C(250)
    );
    l2_system_model_tick(&model, UINT32_C(5));
    return model.safety.first_fault == L2_FAULT_OVER_TEMPERATURE &&
        model.retained_fault_valid &&
        model.retained_fault == L2_FAULT_OVER_TEMPERATURE &&
        model.rf_domains_held_in_reset &&
        model.fault_viewer_available;
}

static bool failed_update_rollback_model_path(void)
{
    l2_update_t update;
    l2_update_init(&update, UINT32_C(200));
    if (!l2_update_begin(&update, true, true, true, true, UINT32_C(0))) {
        return false;
    }
    for (size_t index = 0; index < L2_UPDATE_DOMAIN_COUNT; ++index) {
        if (!l2_update_stage(
                &update,
                (l2_update_domain_t)index,
                UINT32_C(201),
                true
            )) {
            return false;
        }
    }
    if (!l2_update_verify_bundle(&update) ||
        !l2_update_activate(&update, L2_UPDATE_PACK, UINT32_C(1)) ||
        !l2_update_report_self_test(&update, L2_UPDATE_PACK, true) ||
        !l2_update_activate(&update, L2_UPDATE_SAFETY, UINT32_C(2)) ||
        l2_update_report_self_test(&update, L2_UPDATE_SAFETY, false)) {
        return false;
    }
    return update.phase == L2_UPDATE_ROLLED_BACK &&
        update.first_fault == L2_UPDATE_FAULT_SELF_TEST &&
        all_builds_equal(&update, UINT32_C(200));
}

static void run_power_on_software_self_test(void)
{
    if (!self_test_pass_path()) {
        ESP_LOGE(TAG, "F3.2 scenario FAIL: self-test pass path");
        abort();
    }
    ESP_LOGI(TAG, "F3.2 scenario self-test PASS");

    if (!retained_first_fault_path()) {
        ESP_LOGE(TAG, "F3.2 scenario FAIL: retained first-fault path");
        abort();
    }
    ESP_LOGI(TAG, "F3.2 scenario retained-first-fault RAM model PASS");

    if (!failed_update_rollback_model_path()) {
        ESP_LOGE(TAG, "F3.2 scenario FAIL: failed-update rollback model path");
        abort();
    }
    ESP_LOGI(TAG, "F3.2 scenario failed-update RAM rollback model PASS");
}

void app_main(void)
{
    esp_chip_info_t chip = {0};
    esp_chip_info(&chip);
    run_power_on_software_self_test();
    l2_system_model_init(&system_model, INT16_C(700), UINT32_C(0));
    ESP_LOGI(
        TAG,
        "skeleton ready: %u cores, %u reviewed contacts; RF domains remain held",
        (unsigned int)chip.cores,
        (unsigned int)l2_hw_s3_domain.pin_count
    );
}
