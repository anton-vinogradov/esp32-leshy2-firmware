#include "leshy2/receiver_core.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void test_reset_is_disabled_with_direct_path_selected(void)
{
    l2_receiver_t receiver;
    l2_receiver_init(&receiver);
    assert(receiver.state == L2_RECEIVER_DISABLED);
    assert(!receiver.receiver_enabled);
    assert(!receiver.air_rx_enable);
    assert(!receiver.air_rx_mode_airband);
}

static void test_direct_mode_never_enables_airband_chain(void)
{
    l2_receiver_t receiver;
    l2_receiver_init(&receiver);
    assert(l2_receiver_request(&receiver, L2_RECEIVER_MODE_DIRECT_FM_SW, 101700));
    assert(receiver.state == L2_RECEIVER_DIRECT_ACTIVE);
    assert(receiver.receiver_enabled);
    assert(!receiver.air_rx_enable);
    assert(!receiver.air_rx_mode_airband);
}

static void test_airband_endpoints_map_to_if_and_require_both_proofs(void)
{
    l2_receiver_t receiver;
    l2_receiver_init(&receiver);
    assert(l2_receiver_request(&receiver, L2_RECEIVER_MODE_AIRBAND, 118000));
    assert(receiver.intermediate_frequency_khz == 6000);
    l2_receiver_observe(&receiver, true, true, false);
    assert(receiver.state == L2_RECEIVER_AIRBAND_SETTLING);
    l2_receiver_observe(&receiver, true, true, true);
    assert(receiver.state == L2_RECEIVER_AIRBAND_ACTIVE);

    assert(l2_receiver_request(&receiver, L2_RECEIVER_MODE_AIRBAND, 137000));
    assert(receiver.intermediate_frequency_khz == 25000);
}

static void test_out_of_range_airband_fails_safe(void)
{
    l2_receiver_t receiver;
    l2_receiver_init(&receiver);
    assert(!l2_receiver_request(&receiver, L2_RECEIVER_MODE_AIRBAND, 117999));
    assert(receiver.state == L2_RECEIVER_FAULT);
    assert(!receiver.receiver_enabled);
    assert(!receiver.air_rx_enable);
    assert(strcmp(l2_receiver_fault_text(receiver.first_fault),
                  "Airband frequency is outside 118-137 MHz") == 0);
}

static void test_evidence_loss_latches_fault_and_needs_explicit_clear(void)
{
    l2_receiver_t receiver;
    l2_receiver_init(&receiver);
    assert(l2_receiver_request(&receiver, L2_RECEIVER_MODE_AIRBAND, 125000));
    l2_receiver_observe(&receiver, true, true, true);
    l2_receiver_observe(&receiver, true, false, true);
    assert(receiver.state == L2_RECEIVER_FAULT);
    assert(!receiver.receiver_enabled);
    assert(!l2_receiver_request(&receiver, L2_RECEIVER_MODE_DIRECT_FM_SW, 100000));
    assert(l2_receiver_clear_fault(&receiver, true));
    assert(receiver.state == L2_RECEIVER_DISABLED);
}

static void test_hub_loss_is_fail_closed_in_every_active_mode(void)
{
    l2_receiver_t receiver;
    l2_receiver_init(&receiver);
    assert(l2_receiver_request(&receiver, L2_RECEIVER_MODE_DIRECT_FM_SW, 7000));
    l2_receiver_observe(&receiver, false, false, false);
    assert(receiver.state == L2_RECEIVER_FAULT);
    assert(receiver.first_fault == L2_RECEIVER_FAULT_HUB_LINK);
    assert(!l2_receiver_clear_fault(&receiver, false));
}

int main(void)
{
    test_reset_is_disabled_with_direct_path_selected();
    test_direct_mode_never_enables_airband_chain();
    test_airband_endpoints_map_to_if_and_require_both_proofs();
    test_out_of_range_airband_fails_safe();
    test_evidence_loss_latches_fault_and_needs_explicit_clear();
    test_hub_loss_is_fail_closed_in_every_active_mode();
    puts("host receiver core: 6 scenarios passed");
    return 0;
}
