#include "leshy2/safety_core.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static l2_safety_t running_state(void)
{
    l2_safety_t state;
    l2_safety_init(&state, 700);
    l2_safety_set_temperatures(&state, true, 250, 250, 250);
    assert(l2_safety_set_run(&state, true, 0));
    assert(l2_safety_heartbeat(&state, 1, 0));
    return state;
}

static void tick_to(l2_safety_t *state, uint32_t target_ms)
{
    while (state->now_ms < target_ms) {
        uint32_t next = state->now_ms + L2_SAFETY_LOOP_PERIOD_MAX_MS;
        if (next > target_ms) {
            next = target_ms;
        }
        l2_safety_tick(state, next);
    }
}

static void test_reset_and_physical_rearm(void)
{
    l2_safety_t state;
    l2_safety_init(&state, 700);
    assert(state.fault_kill_asserted);
    assert(state.first_fault == L2_FAULT_RUN_KILL);
    assert(!l2_safety_set_run(&state, true, 0));

    l2_safety_set_temperatures(&state, true, 250, 250, 250);
    assert(l2_safety_set_run(&state, true, 0));
    assert(!state.fault_kill_asserted);
    l2_safety_set_power_fault(&state, true);
    l2_safety_tick(&state, 5);
    assert(state.fault_kill_asserted);
    assert(state.first_fault == L2_FAULT_POWER);
    assert(!l2_safety_set_run(&state, true, 10));

    l2_safety_set_run(&state, false, 15);
    l2_safety_set_power_fault(&state, false);
    assert(l2_safety_set_run(&state, true, 20));
    assert(state.first_fault == L2_FAULT_NONE);
}

static void test_full_nrf_mix_and_u219_field_evidence(void)
{
    l2_safety_t state = running_state();
    assert(l2_safety_grant_lease(&state, L2_GROUP_NRF24, 100, 0));
    assert(state.allowed_evidence_mask == 0x001c);
    l2_safety_set_evidence(&state, 0x001c);
    tick_to(&state, 40);
    assert(!state.fault_kill_asserted);

    assert(l2_safety_heartbeat(&state, 2, 40));
    assert(l2_safety_grant_lease(&state, L2_GROUP_NRF24, 100, 40));
    l2_safety_set_evidence(&state, 0x003c);
    tick_to(&state, 50);
    assert(state.fault_kill_asserted);
    assert(state.first_fault == L2_FAULT_UNEXPECTED_EVIDENCE);
    assert(strcmp(l2_fault_text(state.first_fault),
                  "Unexpected physical transmission detected") == 0);

    state = running_state();
    assert(l2_group_evidence_mask(L2_GROUP_U219_NFC) == 0x1000);
    assert(l2_safety_grant_lease(&state, L2_GROUP_U219_NFC, 100, 0));
    l2_safety_set_evidence(&state, 0x1000);
    tick_to(&state, 40);
    assert(!state.fault_kill_asserted);
    l2_safety_revoke_lease(&state, 40);
    l2_safety_set_evidence(&state, 0);
    tick_to(&state, 60);
    assert(!state.fault_kill_asserted);
}

static void test_duplicate_or_stale_heartbeat_does_not_extend_session(void)
{
    l2_safety_t state = running_state();
    assert(!l2_safety_grant_lease(&state, L2_GROUP_BROADCAST_RX, 100, 0));
    tick_to(&state, 95);
    assert(!l2_safety_heartbeat(&state, 1, 95));
    assert(!l2_safety_heartbeat(&state, 0, 95));
    tick_to(&state, 205);
    assert(state.fault_kill_asserted);
    assert(state.first_fault == L2_FAULT_HEARTBEAT_LOST);
}

static void test_lease_expiry_is_fail_closed(void)
{
    l2_safety_t state = running_state();
    assert(!l2_safety_grant_lease(&state, L2_GROUP_VOICE, 101, 0));
    assert(l2_safety_grant_lease(&state, L2_GROUP_VOICE, 100, 0));
    tick_to(&state, 100);
    assert(state.fault_kill_asserted);
    assert(state.first_fault == L2_FAULT_LEASE_EXPIRED);
    assert(state.active_group == L2_GROUP_NONE);
    assert(!state.lease_active);
}

static void test_revoke_grace_and_stuck_rf(void)
{
    l2_safety_t state = running_state();
    assert(l2_safety_grant_lease(&state, L2_GROUP_C5_RF, 100, 0));
    l2_safety_set_evidence(&state, 0x0002);
    l2_safety_revoke_lease(&state, 5);
    tick_to(&state, 20);
    assert(!state.fault_kill_asserted);
    tick_to(&state, 25);
    assert(state.fault_kill_asserted);
    assert(state.first_fault == L2_FAULT_POST_REVOKE_EVIDENCE);
}

static void test_thermal_fault_is_retained_for_viewer(void)
{
    l2_safety_t state = running_state();
    assert(l2_safety_grant_lease(&state, L2_GROUP_S3_RF, 100, 0));
    l2_safety_set_temperatures(&state, true, 250, 705, 250);
    l2_safety_tick(&state, 5);
    assert(state.fault_kill_asserted);
    assert(state.first_fault == L2_FAULT_OVER_TEMPERATURE);
    assert(strcmp(l2_fault_text(state.first_fault), "Safe temperature exceeded") == 0);
}

static void test_watchdog_stops_after_latched_fault(void)
{
    l2_safety_t state = running_state();
    tick_to(&state, 100);
    l2_safety_set_power_fault(&state, true);
    l2_safety_tick(&state, 105);
    assert(state.last_watchdog_service_ms == 100);
    assert(!l2_safety_watchdog_must_trip(&state, 1699));
    assert(l2_safety_watchdog_must_trip(&state, 1700));
}

static void test_loop_deadline_is_fail_closed(void)
{
    l2_safety_t state = running_state();
    l2_safety_tick(&state, 6);
    assert(state.fault_kill_asserted);
    assert(state.first_fault == L2_FAULT_SAFETY_LOOP_OVERRUN);
}

int main(void)
{
    test_reset_and_physical_rearm();
    test_full_nrf_mix_and_u219_field_evidence();
    test_duplicate_or_stale_heartbeat_does_not_extend_session();
    test_lease_expiry_is_fail_closed();
    test_revoke_grace_and_stuck_rf();
    test_thermal_fault_is_retained_for_viewer();
    test_watchdog_stops_after_latched_fault();
    test_loop_deadline_is_fail_closed();
    puts("host safety core: 8 scenarios passed");
    return 0;
}
