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

static void test_hub_loss_closes_receiver_and_isolates_downstream_domains(void)
{
    l2_system_model_t model = running_model();
    assert(l2_system_model_request_receiver(
        &model, L2_RECEIVER_MODE_AIRBAND, 125000
    ));
    l2_system_model_observe_receiver(&model, true, true);
    assert(model.receiver.state == L2_RECEIVER_AIRBAND_ACTIVE);

    l2_system_model_set_domain_online(&model, L2_UPDATE_HUB_RP, false);
    l2_system_model_tick(&model, 5);
    assert(model.receiver.state == L2_RECEIVER_FAULT);
    assert(model.receiver.first_fault == L2_RECEIVER_FAULT_HUB_LINK);
    assert(!model.domain_online[L2_UPDATE_C5]);
    assert(!model.domain_online[L2_UPDATE_RF_RP]);
    assert(!l2_system_model_heartbeat(&model, 2, 50));
    tick_to(&model, 205);
    assert(model.safety.first_fault == L2_FAULT_HEARTBEAT_LOST);
}

static void test_pack_loss_becomes_local_power_fault(void)
{
    l2_system_model_t model = running_model();
    assert(l2_system_model_request_receiver(
        &model, L2_RECEIVER_MODE_DIRECT_FM_SW, 101700
    ));
    l2_system_model_set_domain_online(&model, L2_UPDATE_PACK, false);
    l2_system_model_tick(&model, 5);
    assert(model.safety.first_fault == L2_FAULT_POWER);
    assert(model.safety.fault_kill_asserted);
    assert(model.receiver.state == L2_RECEIVER_DISABLED);
    assert(!model.fault_viewer_available);
}

static void test_safety_loss_disables_receiver_before_watchdog_trip(void)
{
    l2_system_model_t model = running_model();
    assert(l2_system_model_request_receiver(
        &model, L2_RECEIVER_MODE_DIRECT_FM_SW, 101700
    ));
    l2_system_model_set_domain_online(&model, L2_UPDATE_SAFETY, false);
    l2_system_model_tick(&model, 5);
    assert(model.receiver.state == L2_RECEIVER_DISABLED);
    assert(!model.receiver.receiver_enabled);
    assert(!model.external_watchdog_tripped);
    l2_system_model_tick(&model, 1600);
    assert(model.external_watchdog_tripped);
}

static void verify_u219_cap_policy_is_fail_closed(void)
{
    l2_cap_state_t cap;
    l2_cap_init(&cap);
    assert(cap.profile == L2_CAP_PROFILE_UNKNOWN);
    assert(cap.phase == L2_CAP_OFF);
    assert(!cap.branch_power_enabled);
    assert(!cap.io_connected);
    assert(!cap.contact8_high);
    assert(!cap.contact10_is_output);
    assert(cap.contact10_high);
    assert(cap.contact14_high);
    assert(!l2_cap_select_profile(&cap, L2_CAP_PROFILE_UNKNOWN, true));
    assert(!l2_cap_select_profile(&cap, L2_CAP_PROFILE_U219, false));

    assert(l2_cap_select_profile(&cap, L2_CAP_PROFILE_U219, true));
    assert(l2_cap_start_power(&cap));
    assert(!l2_cap_observe_power_good(&cap, false));
    assert(cap.phase == L2_CAP_FAULT);
    assert(cap.profile == L2_CAP_PROFILE_UNKNOWN);
    assert(!cap.branch_power_enabled);
    assert(!cap.io_connected);
    assert(!cap.contact8_high);
    l2_cap_shutdown(&cap);

    assert(l2_cap_select_profile(&cap, L2_CAP_PROFILE_U214, true));
    assert(!l2_cap_select_profile(&cap, L2_CAP_PROFILE_U219, true));
    assert(l2_cap_start_power(&cap));
    assert(cap.branch_power_enabled);
    assert(!cap.io_connected);
    assert(!cap.contact8_high);
    assert(!cap.contact10_is_output);
    assert(l2_cap_observe_power_good(&cap, true));
    assert(cap.io_connected);
    assert(!cap.contact8_high);
    assert(l2_cap_release_device(&cap));
    assert(cap.phase == L2_CAP_ACTIVE);
    assert(cap.contact8_high);
    assert(l2_cap_spi_select(&cap, L2_CAP_SPI_U214_SX1262));
    assert(l2_cap_spi_mode(cap.spi_target) == 0);
    assert(!cap.contact14_high);
    assert(cap.contact10_high);
    l2_cap_spi_deselect(&cap);
    l2_cap_shutdown(&cap);

    assert(l2_cap_select_profile(&cap, L2_CAP_PROFILE_U219, true));
    assert(l2_cap_start_power(&cap));
    assert(cap.contact10_is_output);
    assert(cap.contact10_high);
    assert(!cap.io_connected);
    assert(l2_cap_observe_power_good(&cap, true));
    assert(cap.io_connected);
    assert(!cap.contact8_high);
    assert(l2_cap_release_device(&cap));

    assert(l2_cap_spi_select(&cap, L2_CAP_SPI_U219_CC1101));
    assert(l2_cap_spi_mode(cap.spi_target) == 0);
    const uint8_t allowed_strobes[] = {
        0x30, 0x32, 0x33, 0x34, 0x36, 0x39, 0x3a, 0x3d,
    };
    for (unsigned strobe = 0; strobe <= UINT8_MAX; ++strobe) {
        bool expected = false;
        for (unsigned index = 0;
             index < sizeof(allowed_strobes) / sizeof(allowed_strobes[0]);
             ++index) {
            if (strobe == allowed_strobes[index]) {
                expected = true;
            }
        }
        assert(l2_cap_cc1101_access_allowed(
            &cap, L2_CC1101_STROBE, (uint8_t)strobe, 0
        ) == expected);
    }
    assert(l2_cap_cc1101_access_allowed(
        &cap, L2_CC1101_WRITE_REGISTER, 0x17, 0x0c
    ));
    assert(!l2_cap_cc1101_access_allowed(
        &cap, L2_CC1101_WRITE_REGISTER, 0x17, 0x08
    ));
    assert(!l2_cap_cc1101_access_allowed(
        &cap, L2_CC1101_WRITE_REGISTER, 0x18, 0x02
    ));
    assert(!l2_cap_cc1101_access_allowed(
        &cap, L2_CC1101_WRITE_PATABLE, 0x3e, 0
    ));
    assert(!l2_cap_cc1101_access_allowed(
        &cap, L2_CC1101_WRITE_TX_FIFO, 0x3f, 0
    ));
    l2_cap_spi_deselect(&cap);

    assert(l2_cap_spi_select(&cap, L2_CAP_SPI_U219_NFC));
    assert(l2_cap_spi_mode(cap.spi_target) == 1);
    assert(cap.contact10_is_output);
    assert(!cap.contact10_high);
    assert(cap.contact14_high);
    assert(l2_cap_nfc_operation_supported(L2_CAP_NFC_POLL));
    assert(l2_cap_nfc_operation_supported(L2_CAP_NFC_READ));
    assert(!l2_cap_nfc_operation_supported(L2_CAP_NFC_WRITE));
    assert(!l2_cap_nfc_operation_supported(L2_CAP_NFC_CARD_EMULATION));
    assert(!l2_cap_nfc_begin_field(
        &cap, L2_CAP_NFC_READ, true, true
    ));
    assert(!cap.nfc_field_active);
    l2_cap_spi_deselect(&cap);
    cap.nfc_field_active = true;
    assert(!l2_cap_spi_select(&cap, L2_CAP_SPI_U219_CC1101));
    cap.nfc_field_active = false;
    l2_cap_shutdown(&cap);
    assert(cap.profile == L2_CAP_PROFILE_UNKNOWN);
    assert(!cap.branch_power_enabled);
    assert(!cap.io_connected);
    assert(!cap.contact8_high);
    assert(!cap.contact10_is_output);
}

static void test_six_domain_update_and_cap_policy_are_fail_closed(void)
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
    verify_u219_cap_policy_is_fail_closed();
}

int main(void)
{
    test_safety_preempts_saturated_waterfall_and_update();
    test_foreign_tx_fails_closed_under_saturation();
    test_s3_loss_latches_fault_and_record_survives_reboot();
    test_ui_thermal_fault_suppresses_screen();
    test_controlled_kill_is_not_reported_as_a_fault();
    test_dead_safety_controller_releases_external_watchdog();
    test_hub_loss_closes_receiver_and_isolates_downstream_domains();
    test_pack_loss_becomes_local_power_fault();
    test_safety_loss_disables_receiver_before_watchdog_trip();
    test_six_domain_update_and_cap_policy_are_fail_closed();
    puts("host six-domain model: 10 scenarios passed");
    return 0;
}
