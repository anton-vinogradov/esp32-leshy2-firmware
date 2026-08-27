#include "leshy2/receiver_core.h"

static void safe_outputs(l2_receiver_t *receiver)
{
    receiver->receiver_enabled = false;
    receiver->air_rx_enable = false;
    receiver->air_rx_mode_airband = false;
    receiver->lo_locked = false;
    receiver->rf_path_settled = false;
}

static void latch_fault(l2_receiver_t *receiver, l2_receiver_fault_t fault)
{
    if (receiver->first_fault == L2_RECEIVER_FAULT_NONE) {
        receiver->first_fault = fault;
    }
    receiver->state = L2_RECEIVER_FAULT;
    safe_outputs(receiver);
}

void l2_receiver_init(l2_receiver_t *receiver)
{
    *receiver = (l2_receiver_t){0};
    receiver->state = L2_RECEIVER_DISABLED;
    receiver->requested_mode = L2_RECEIVER_MODE_DISABLED;
}

bool l2_receiver_request(
    l2_receiver_t *receiver,
    l2_receiver_mode_t mode,
    uint32_t frequency_khz
)
{
    if (receiver->state == L2_RECEIVER_FAULT) {
        return false;
    }
    if ((unsigned)mode > (unsigned)L2_RECEIVER_MODE_AIRBAND) {
        latch_fault(receiver, L2_RECEIVER_FAULT_INVALID_MODE);
        return false;
    }

    safe_outputs(receiver);
    receiver->requested_mode = mode;
    receiver->tuned_frequency_khz = frequency_khz;
    receiver->intermediate_frequency_khz = 0;
    if (mode == L2_RECEIVER_MODE_DISABLED) {
        receiver->state = L2_RECEIVER_DISABLED;
        receiver->tuned_frequency_khz = 0;
        return true;
    }
    if (mode == L2_RECEIVER_MODE_DIRECT_FM_SW) {
        receiver->state = L2_RECEIVER_DIRECT_ACTIVE;
        receiver->receiver_enabled = true;
        return true;
    }
    if (frequency_khz < L2_AIRBAND_MIN_KHZ || frequency_khz > L2_AIRBAND_MAX_KHZ) {
        latch_fault(receiver, L2_RECEIVER_FAULT_FREQUENCY_RANGE);
        return false;
    }
    receiver->intermediate_frequency_khz = frequency_khz - L2_AIRBAND_LO_KHZ;
    if (receiver->intermediate_frequency_khz < L2_AIRBAND_IF_MIN_KHZ ||
        receiver->intermediate_frequency_khz > L2_AIRBAND_IF_MAX_KHZ) {
        latch_fault(receiver, L2_RECEIVER_FAULT_FREQUENCY_RANGE);
        return false;
    }
    receiver->state = L2_RECEIVER_AIRBAND_SETTLING;
    receiver->receiver_enabled = true;
    receiver->air_rx_enable = true;
    receiver->air_rx_mode_airband = true;
    return true;
}

void l2_receiver_observe(
    l2_receiver_t *receiver,
    bool hub_link_online,
    bool lo_locked,
    bool rf_path_settled
)
{
    if (receiver->state == L2_RECEIVER_FAULT) {
        return;
    }
    if (!hub_link_online) {
        latch_fault(receiver, L2_RECEIVER_FAULT_HUB_LINK);
        return;
    }
    if (receiver->state == L2_RECEIVER_AIRBAND_SETTLING) {
        receiver->lo_locked = lo_locked;
        receiver->rf_path_settled = rf_path_settled;
        if (lo_locked && rf_path_settled) {
            receiver->state = L2_RECEIVER_AIRBAND_ACTIVE;
        }
        return;
    }
    if (receiver->state == L2_RECEIVER_AIRBAND_ACTIVE &&
        (!lo_locked || !rf_path_settled)) {
        latch_fault(receiver, L2_RECEIVER_FAULT_AIRBAND_EVIDENCE_LOST);
    }
}

bool l2_receiver_clear_fault(l2_receiver_t *receiver, bool hub_link_online)
{
    if (receiver->state != L2_RECEIVER_FAULT || !hub_link_online) {
        return false;
    }
    l2_receiver_init(receiver);
    return true;
}

const char *l2_receiver_fault_text(l2_receiver_fault_t fault)
{
    switch (fault) {
    case L2_RECEIVER_FAULT_NONE: return "No receiver fault";
    case L2_RECEIVER_FAULT_INVALID_MODE: return "Invalid receiver mode";
    case L2_RECEIVER_FAULT_FREQUENCY_RANGE: return "Airband frequency is outside 118-137 MHz";
    case L2_RECEIVER_FAULT_HUB_LINK: return "Hub receiver control link lost";
    case L2_RECEIVER_FAULT_AIRBAND_EVIDENCE_LOST: return "Airband LO or RF path evidence lost";
    default: return "Unknown receiver fault";
    }
}
