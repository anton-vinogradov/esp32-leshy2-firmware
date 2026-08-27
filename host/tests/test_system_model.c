#include "leshy2/system_model.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static l2_system_model_t running_model(void)
{
    l2_system_model_t model;
    l2_system_model_init(&model, 700, 100);
    l2_safety_set_temperatures(&model.safety, true, 250, 250, 250);
    assert(l2_system_model_set_run(&model, true, 0));
    assert(l2_system_model_heartbeat(&model, 1, 0));
    return model;
}

static void tick_to(l2_system_model_t *model, uint32_t target_ms)
{
    while (model->safety.now_ms < target_ms) {
        uint32_t next = model->safety.now_ms + L2_SAFETY_LOOP_PERIOD_MAX_MS;
        if (next > target_ms) {
            next = target_ms;
        }
        l2_system_model_tick(model, next);
    }
}

static void saturate_low_priority(l2_scheduler_t *scheduler)
{
    for (uint16_t id = 0; id < 32; ++id) {
        assert(l2_scheduler_enqueue(scheduler, L2_PRIORITY_TELEMETRY, id));
    }
    for (uint16_t id = 100; id < 116; ++id) {
        assert(l2_scheduler_enqueue(scheduler, L2_PRIORITY_BULK, id));
    }
    assert(!l2_scheduler_enqueue(scheduler, L2_PRIORITY_BULK, 116));
}

static void test_safety_preempts_saturated_waterfall_and_update(void)
{
    l2_system_model_t model = running_model();
    saturate_low_priority(&model.scheduler);
    assert(model.scheduler.queue[L2_PRIORITY_TELEMETRY].dropped == 16);
    assert(l2_scheduler_enqueue(&model.scheduler, L2_PRIORITY_SAFETY, 15));

    l2_priority_t priority = L2_PRIORITY_COUNT;
    uint16_t message_id = 0;
    assert(l2_scheduler_dequeue(&model.scheduler, &priority, &message_id));
    assert(priority == L2_PRIORITY_SAFETY);
    assert(message_id == 15);

    assert(l2_safety_grant_lease(&model.safety, L2_GROUP_NRF24, 100, 0));
    l2_safety_set_evidence(&model.safety, 0x001c);
    l2_safety_revoke_lease(&model.safety, 5);
    l2_safety_set_evidence(&model.safety, 0);
    tick_to(&model, 25);
    assert(!model.safety.fault_kill_asserted);
}

static void test_foreign_tx_fails_closed_under_saturation(void)
{
    l2_system_model_t model = running_model();
    saturate_low_priority(&model.scheduler);
    assert(l2_safety_grant_lease(&model.safety, L2_GROUP_C5_RF, 100, 0));
    l2_safety_set_evidence(&model.safety, 0x0022);
    tick_to(&model, 10);
    assert(model.safety.first_fault == L2_FAULT_UNEXPECTED_EVIDENCE);
    assert(model.rf_domains_held_in_reset);
    assert(!model.domain_online[L2_UPDATE_C5]);
    assert(!model.domain_online[L2_UPDATE_RF_RP]);
    assert(!model.domain_online[L2_UPDATE_HUB_RP]);
    assert(model.fault_viewer_available);
    assert(strcmp(l2_system_model_fault_text(&model),
                  "Unexpected physical transmission detected") == 0);
}

static void test_s3_loss_latches_fault_and_record_survives_reboot(void)
{
    l2_system_model_t model = running_model();
    l2_system_model_set_domain_online(&model, L2_UPDATE_S3, false);
    tick_to(&model, 205);
    assert(model.safety.first_fault == L2_FAULT_HEARTBEAT_LOST);
    assert(!model.fault_viewer_available);
    assert(strcmp(l2_system_model_fault_text(&model),
                  "Controller heartbeat lost") == 0);

    l2_system_model_set_domain_online(&model, L2_UPDATE_S3, true);
    l2_system_model_tick(&model, 210);
    assert(model.fault_viewer_available);
    assert(strcmp(l2_system_model_fault_text(&model),
                  "Controller heartbeat lost") == 0);
}

static void test_ui_thermal_fault_suppresses_screen(void)
{
    l2_system_model_t model = running_model();
    l2_safety_set_temperatures(&model.safety, true, 250, 250, 705);
    l2_system_model_tick(&model, 5);
    assert(model.safety.first_fault == L2_FAULT_OVER_TEMPERATURE);
    assert(model.retained_fault_valid);
    assert(!model.fault_viewer_available);
}

static void test_controlled_kill_is_not_reported_as_a_fault(void)
{
    l2_system_model_t model = running_model();
    assert(l2_system_model_set_run(&model, false, 5));
    l2_system_model_tick(&model, 10);
    assert(model.rf_domains_held_in_reset);
    assert(!model.retained_fault_valid);
    assert(!model.fault_viewer_available);
}

static void test_dead_safety_controller_releases_external_watchdog(void)
{
    l2_system_model_t model = running_model();
    l2_system_model_set_domain_online(&model, L2_UPDATE_SAFETY, false);
    l2_system_model_tick(&model, 1599);
    assert(!model.external_watchdog_tripped);
    l2_system_model_tick(&model, 1600);
    assert(model.external_watchdog_tripped);
    assert(model.rf_domains_held_in_reset);
}

static void test_six_domain_update_rolls_back_as_one_bundle(void)
{
    l2_system_model_t model;
    l2_system_model_init(&model, 700, 100);
    assert(l2_update_begin(&model.update, true, true, true, true, 0));
    for (int domain = 0; domain < L2_UPDATE_DOMAIN_COUNT; ++domain) {
        assert(l2_update_stage(&model.update, (l2_update_domain_t)domain, 101, true));
    }
    assert(l2_update_verify_bundle(&model.update));
    assert(l2_update_activate(&model.update, L2_UPDATE_PACK, 1));
    assert(l2_update_report_self_test(&model.update, L2_UPDATE_PACK, true));
    assert(l2_update_activate(&model.update, L2_UPDATE_SAFETY, 2));
    assert(l2_update_report_self_test(&model.update, L2_UPDATE_SAFETY, true));
    assert(l2_update_activate(&model.update, L2_UPDATE_C5, 3));
    assert(!l2_update_report_self_test(&model.update, L2_UPDATE_C5, false));
    assert(model.update.phase == L2_UPDATE_ROLLED_BACK);
    for (int domain = 0; domain < L2_UPDATE_DOMAIN_COUNT; ++domain) {
        assert(model.update.active_build[domain] == 100);
    }
}

int main(void)
{
    test_safety_preempts_saturated_waterfall_and_update();
    test_foreign_tx_fails_closed_under_saturation();
    test_s3_loss_latches_fault_and_record_survives_reboot();
    test_ui_thermal_fault_suppresses_screen();
    test_controlled_kill_is_not_reported_as_a_fault();
    test_dead_safety_controller_releases_external_watchdog();
    test_six_domain_update_rolls_back_as_one_bundle();
    puts("host six-domain model: 7 scenarios passed");
    return 0;
}
