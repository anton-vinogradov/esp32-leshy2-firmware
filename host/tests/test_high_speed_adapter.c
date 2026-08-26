#include "leshy2/high_speed_adapter.h"

#include <assert.h>
#include <stdio.h>

static l2_hs_adapter_t ready_adapter(uint32_t peer_boot_id)
{
    l2_hs_adapter_t adapter;
    l2_hs_init(&adapter);
    assert(l2_hs_transition(&adapter, L2_HS_STARTING) == L2_HS_OK);
    assert(l2_hs_transition(&adapter, L2_HS_NEGOTIATING) == L2_HS_OK);
    assert(l2_hs_accept_handshake(
        &adapter, 10, peer_boot_id, true, true, 100
    ) == L2_HS_OK);
    return adapter;
}

static void test_handshake_and_non_ready_side_effect_gate(void)
{
    l2_hs_adapter_t adapter;
    l2_hs_init(&adapter);
    assert(!l2_hs_side_effects_open(&adapter));
    assert(l2_hs_transition(&adapter, L2_HS_STARTING) == L2_HS_OK);
    assert(l2_hs_transition(&adapter, L2_HS_NEGOTIATING) == L2_HS_OK);
    assert(l2_hs_transition(&adapter, L2_HS_READY) == L2_HS_INVALID_STATE);
    assert(l2_hs_accept_handshake(&adapter, 1, 2, true, true, 0) == L2_HS_OK);
    assert(l2_hs_side_effects_open(&adapter));
}

static void test_incompatible_handshake_faults_closed(void)
{
    l2_hs_adapter_t adapter;
    l2_hs_init(&adapter);
    assert(l2_hs_transition(&adapter, L2_HS_STARTING) == L2_HS_OK);
    assert(l2_hs_transition(&adapter, L2_HS_NEGOTIATING) == L2_HS_OK);
    assert(l2_hs_accept_handshake(&adapter, 1, 2, false, true, 0) == L2_HS_FAULT);
    assert(adapter.state == L2_HS_FAULTED);
    assert(!l2_hs_side_effects_open(&adapter));
}

static void test_reset_never_returns_directly_to_ready(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    assert(l2_hs_transition(&adapter, L2_HS_RESETTING) == L2_HS_OK);
    assert(l2_hs_transition(&adapter, L2_HS_READY) == L2_HS_INVALID_STATE);
    assert(l2_hs_transition(&adapter, L2_HS_STARTING) == L2_HS_OK);
}

static void test_tx_ownership_requires_completion(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    uint8_t handle;
    assert(l2_hs_tx_acquire(&adapter, L2_HS_PRIORITY_CONTROL, &handle) == L2_HS_OK);
    assert(l2_hs_tx_enqueue(&adapter, handle, 1, false, 0, 0) == L2_HS_OK);
    assert(l2_hs_tx_complete(&adapter, handle) == L2_HS_OWNERSHIP_ERROR);
    uint8_t selected;
    assert(l2_hs_tx_take_next(&adapter, 0, &selected) == L2_HS_OK);
    assert(selected == handle);
    assert(l2_hs_tx_cancel(&adapter, handle) == L2_HS_OWNERSHIP_ERROR);
    assert(l2_hs_tx_complete(&adapter, handle) == L2_HS_OK);
}

static void test_rx_ownership_requires_validation_dispatch_and_release(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    uint8_t handle;
    assert(l2_hs_rx_phy_begin(&adapter, L2_HS_PRIORITY_CONTROL, &handle) == L2_HS_OK);
    assert(l2_hs_rx_dispatch(&adapter, handle) == L2_HS_OWNERSHIP_ERROR);
    assert(l2_hs_rx_finish_phy(&adapter, handle) == L2_HS_OK);
    assert(l2_hs_rx_release(&adapter, handle) == L2_HS_OWNERSHIP_ERROR);
    assert(l2_hs_rx_dispatch(&adapter, handle) == L2_HS_OK);
    assert(l2_hs_rx_release(&adapter, handle) == L2_HS_OK);
}

static void exhaust_protected_queue(l2_hs_priority_t priority, size_t count)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    uint8_t handle;
    for (size_t index = 0; index < count; ++index) {
        assert(l2_hs_tx_acquire(&adapter, priority, &handle) == L2_HS_OK);
    }
    assert(l2_hs_tx_acquire(&adapter, priority, &handle) == L2_HS_FAULT);
    assert(adapter.state == L2_HS_FAULTED);
    assert(!l2_hs_side_effects_open(&adapter));
}

static void test_safety_queue_exhaustion_faults(void)
{
    exhaust_protected_queue(L2_HS_PRIORITY_SAFETY, 4);
}

static void test_control_queue_exhaustion_faults(void)
{
    exhaust_protected_queue(L2_HS_PRIORITY_CONTROL, 8);
}

static void test_interactive_queue_backpressures(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    uint8_t handle;
    for (size_t index = 0; index < 8; ++index) {
        assert(l2_hs_tx_acquire(&adapter, L2_HS_PRIORITY_INTERACTIVE, &handle) == L2_HS_OK);
    }
    assert(l2_hs_tx_acquire(&adapter, L2_HS_PRIORITY_INTERACTIVE, &handle) == L2_HS_BUSY);
    assert(adapter.state == L2_HS_READY);
}

static void test_telemetry_overflow_preserves_newest(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    uint8_t handle;
    for (uint32_t message = 1; message <= 5; ++message) {
        assert(l2_hs_tx_acquire(&adapter, L2_HS_PRIORITY_TELEMETRY, &handle) == L2_HS_OK);
        assert(l2_hs_tx_enqueue(&adapter, handle, message, false, 0, 0) == L2_HS_OK);
    }
    assert(adapter.telemetry_dropped == 1);
    assert(l2_hs_tx_take_next(&adapter, 0, &handle) == L2_HS_OK);
    assert(adapter.tx[handle].message_id == 2);
}

static void test_bulk_zero_credit_stalls_without_blocking_control(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    uint8_t bulk;
    uint8_t control;
    assert(l2_hs_tx_acquire(&adapter, L2_HS_PRIORITY_BULK, &bulk) == L2_HS_OK);
    assert(l2_hs_tx_enqueue(&adapter, bulk, 1, false, 0, 0) == L2_HS_NO_CREDIT);
    assert(l2_hs_tx_acquire(&adapter, L2_HS_PRIORITY_CONTROL, &control) == L2_HS_OK);
    assert(l2_hs_tx_enqueue(&adapter, control, 2, false, 0, 0) == L2_HS_OK);
    assert(l2_hs_tx_take_next(&adapter, 0, &control) == L2_HS_OK);
    assert(adapter.tx[control].message_id == 2);
    assert(l2_hs_tx_cancel(&adapter, bulk) == L2_HS_OK);
}

static void test_bulk_credit_returns_only_after_rx_release(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    assert(l2_hs_seed_receive_bulk_credit(&adapter) == L2_HS_OK);
    assert(l2_hs_receive_bulk_credit(&adapter) == 8);
    uint8_t handle;
    assert(l2_hs_rx_phy_begin(&adapter, L2_HS_PRIORITY_BULK, &handle) == L2_HS_OK);
    assert(l2_hs_receive_bulk_credit(&adapter) == 7);
    assert(l2_hs_rx_finish_phy(&adapter, handle) == L2_HS_OK);
    assert(l2_hs_rx_dispatch(&adapter, handle) == L2_HS_OK);
    assert(l2_hs_receive_bulk_credit(&adapter) == 7);
    assert(l2_hs_rx_release(&adapter, handle) == L2_HS_OK);
    assert(l2_hs_receive_bulk_credit(&adapter) == 8);
}

static void test_monotonic_remote_grant_is_duplicate_safe(void)
{
    l2_hs_adapter_t invalid = ready_adapter(2);
    assert(l2_hs_apply_remote_bulk_grant(&invalid, 2, 7) == L2_HS_FAULT);
    assert(invalid.state == L2_HS_FAULTED);

    l2_hs_adapter_t adapter = ready_adapter(2);
    assert(l2_hs_apply_remote_bulk_grant(&adapter, 2, 8) == L2_HS_OK);
    assert(l2_hs_remote_bulk_credit(&adapter) == 8);
    uint8_t handle;
    assert(l2_hs_tx_acquire(&adapter, L2_HS_PRIORITY_BULK, &handle) == L2_HS_OK);
    assert(l2_hs_tx_enqueue(&adapter, handle, 1, false, 0, 0) == L2_HS_OK);
    assert(l2_hs_remote_bulk_credit(&adapter) == 7);
    assert(l2_hs_apply_remote_bulk_grant(&adapter, 2, 8) == L2_HS_OK);
    assert(l2_hs_remote_bulk_credit(&adapter) == 7);
    assert(l2_hs_apply_remote_bulk_grant(&adapter, 2, 7) == L2_HS_STALE);
    assert(l2_hs_apply_remote_bulk_grant(&adapter, 3, 9) == L2_HS_SESSION_MISMATCH);
}

static void test_pending_duplicate_coalesces(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    assert(l2_hs_receive_request(&adapter, 2, 7, true, 20, 100) == L2_HS_NEW);
    assert(l2_hs_receive_request(&adapter, 2, 7, true, 20, 101) == L2_HS_DUPLICATE_PENDING);
    assert(l2_hs_pending_count(&adapter) == 1);
}

static void test_cached_duplicate_returns_same_result(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    assert(l2_hs_receive_request(&adapter, 2, 7, true, 20, 100) == L2_HS_NEW);
    assert(l2_hs_finish_request(&adapter, 7, -3, 42) == L2_HS_OK);
    assert(l2_hs_receive_request(&adapter, 2, 7, true, 20, 101) == L2_HS_DUPLICATE_CACHED);
    int32_t result;
    uint32_t owner_state;
    assert(l2_hs_cached_result(&adapter, 7, &result, &owner_state));
    assert(result == -3 && owner_state == 42);
}

static void test_evicted_duplicate_is_stale_and_never_new(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    for (uint32_t message = 1; message <= 9; ++message) {
        assert(l2_hs_receive_request(&adapter, 2, message, true, 20, 100) == L2_HS_NEW);
        assert(l2_hs_finish_request(&adapter, message, 0, message) == L2_HS_OK);
    }
    assert(l2_hs_receive_request(&adapter, 2, 1, true, 20, 101) == L2_HS_STALE);
}

static void test_deadline_expiry_prevents_commit(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    assert(l2_hs_receive_request(&adapter, 2, 7, true, 20, 100) == L2_HS_NEW);
    assert(l2_hs_request_can_commit(&adapter, 7, 119) == L2_HS_OK);
    assert(l2_hs_request_can_commit(&adapter, 7, 120) == L2_HS_DEADLINE_EXPIRED);
}

static void test_post_commit_result_survives_deadline(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    assert(l2_hs_receive_request(&adapter, 2, 7, true, 20, 100) == L2_HS_NEW);
    assert(l2_hs_request_can_commit(&adapter, 7, 119) == L2_HS_OK);
    assert(l2_hs_finish_request(&adapter, 7, 0, 99) == L2_HS_OK);
    int32_t result;
    uint32_t owner_state;
    assert(l2_hs_cached_result(&adapter, 7, &result, &owner_state));
    assert(result == 0 && owner_state == 99);
}

static void test_peer_boot_change_clears_session_credit_and_results(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    assert(l2_hs_apply_remote_bulk_grant(&adapter, 2, 8) == L2_HS_OK);
    assert(l2_hs_receive_request(&adapter, 2, 7, true, 20, 100) == L2_HS_NEW);
    assert(l2_hs_finish_request(&adapter, 7, 0, 1) == L2_HS_OK);
    assert(l2_hs_observe_peer_boot(&adapter, 3) == L2_HS_SESSION_MISMATCH);
    assert(adapter.state == L2_HS_RESETTING);
    assert(l2_hs_remote_bulk_credit(&adapter) == 0);
    assert(!l2_hs_side_effects_open(&adapter));
    int32_t result;
    uint32_t owner_state;
    assert(!l2_hs_cached_result(&adapter, 7, &result, &owner_state));
}

static void test_liveness_gap_faults_closed(void)
{
    l2_hs_adapter_t adapter = ready_adapter(2);
    assert(l2_hs_tick(&adapter, 300) == L2_HS_OK);
    assert(l2_hs_tick(&adapter, 301) == L2_HS_FAULT);
    assert(adapter.state == L2_HS_FAULTED);
    assert(!l2_hs_side_effects_open(&adapter));
}

int main(void)
{
    test_handshake_and_non_ready_side_effect_gate();
    test_incompatible_handshake_faults_closed();
    test_reset_never_returns_directly_to_ready();
    test_tx_ownership_requires_completion();
    test_rx_ownership_requires_validation_dispatch_and_release();
    test_safety_queue_exhaustion_faults();
    test_control_queue_exhaustion_faults();
    test_interactive_queue_backpressures();
    test_telemetry_overflow_preserves_newest();
    test_bulk_zero_credit_stalls_without_blocking_control();
    test_bulk_credit_returns_only_after_rx_release();
    test_monotonic_remote_grant_is_duplicate_safe();
    test_pending_duplicate_coalesces();
    test_cached_duplicate_returns_same_result();
    test_evicted_duplicate_is_stale_and_never_new();
    test_deadline_expiry_prevents_commit();
    test_post_commit_result_survives_deadline();
    test_peer_boot_change_clears_session_credit_and_results();
    test_liveness_gap_faults_closed();
    puts("host high-speed adapter: 19 scenarios passed");
    return 0;
}
