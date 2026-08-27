#ifndef LESHY2_RECEIVER_CORE_H
#define LESHY2_RECEIVER_CORE_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    L2_RECEIVER_MODE_DISABLED = 0,
    L2_RECEIVER_MODE_DIRECT_FM_SW,
    L2_RECEIVER_MODE_AIRBAND,
} l2_receiver_mode_t;

typedef enum {
    L2_RECEIVER_DISABLED = 0,
    L2_RECEIVER_DIRECT_ACTIVE,
    L2_RECEIVER_AIRBAND_SETTLING,
    L2_RECEIVER_AIRBAND_ACTIVE,
    L2_RECEIVER_FAULT,
} l2_receiver_state_t;

typedef enum {
    L2_RECEIVER_FAULT_NONE = 0,
    L2_RECEIVER_FAULT_INVALID_MODE,
    L2_RECEIVER_FAULT_FREQUENCY_RANGE,
    L2_RECEIVER_FAULT_HUB_LINK,
    L2_RECEIVER_FAULT_AIRBAND_EVIDENCE_LOST,
} l2_receiver_fault_t;

enum {
    L2_AIRBAND_LO_KHZ = 112000,
    L2_AIRBAND_MIN_KHZ = 118000,
    L2_AIRBAND_MAX_KHZ = 137000,
    L2_AIRBAND_IF_MIN_KHZ = 6000,
    L2_AIRBAND_IF_MAX_KHZ = 25000,
};

typedef struct {
    l2_receiver_state_t state;
    l2_receiver_mode_t requested_mode;
    l2_receiver_fault_t first_fault;
    uint32_t tuned_frequency_khz;
    uint32_t intermediate_frequency_khz;
    bool receiver_enabled;
    bool air_rx_enable;
    bool air_rx_mode_airband;
    bool lo_locked;
    bool rf_path_settled;
} l2_receiver_t;

void l2_receiver_init(l2_receiver_t *receiver);
bool l2_receiver_request(
    l2_receiver_t *receiver,
    l2_receiver_mode_t mode,
    uint32_t frequency_khz
);
void l2_receiver_observe(
    l2_receiver_t *receiver,
    bool hub_link_online,
    bool lo_locked,
    bool rf_path_settled
);
bool l2_receiver_clear_fault(l2_receiver_t *receiver, bool hub_link_online);
const char *l2_receiver_fault_text(l2_receiver_fault_t fault);

#endif
