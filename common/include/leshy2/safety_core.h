#ifndef LESHY2_SAFETY_CORE_H
#define LESHY2_SAFETY_CORE_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    L2_GROUP_NONE = 0,
    L2_GROUP_S3_RF = 1,
    L2_GROUP_C5_RF = 2,
    L2_GROUP_NRF24 = 3,
    L2_GROUP_CC1101 = 4,
    L2_GROUP_VOICE = 5,
    L2_GROUP_IR = 6,
    L2_GROUP_LORA_CAP = 7,
    L2_GROUP_M5_UNIT = 8,
    L2_GROUP_BROADCAST_RX = 9,
    L2_GROUP_U219_NFC = 10,
} l2_group_t;

typedef enum {
    L2_FAULT_NONE = 0,
    L2_FAULT_RUN_KILL,
    L2_FAULT_HEARTBEAT_LOST,
    L2_FAULT_LEASE_EXPIRED,
    L2_FAULT_UNEXPECTED_EVIDENCE,
    L2_FAULT_POST_REVOKE_EVIDENCE,
    L2_FAULT_THERMAL_SENSOR,
    L2_FAULT_OVER_TEMPERATURE,
    L2_FAULT_POWER,
    L2_FAULT_SAFETY_LOOP_OVERRUN,
} l2_fault_t;

enum {
    L2_HEARTBEAT_GAP_MAX_MS = 200,
    L2_LEASE_LIFETIME_MAX_MS = 100,
    L2_UNEXPECTED_EVIDENCE_MAX_MS = 10,
    L2_POST_REVOKE_GRACE_MS = 20,
    L2_SAFETY_LOOP_PERIOD_MAX_MS = 5,
    L2_EXTERNAL_WATCHDOG_TIMEOUT_MS = 1600,
};

typedef struct {
    uint32_t now_ms;
    uint32_t last_tick_ms;
    uint32_t last_heartbeat_ms;
    uint32_t last_heartbeat_sequence;
    uint32_t lease_expiry_ms;
    uint32_t evidence_mismatch_since_ms;
    uint32_t evidence_grace_expiry_ms;
    uint32_t last_watchdog_service_ms;
    uint16_t observed_evidence_mask;
    uint16_t allowed_evidence_mask;
    int16_t temperatures_deci_c[3];
    int16_t maximum_temperature_deci_c;
    l2_group_t active_group;
    l2_fault_t first_fault;
    bool run_requested;
    bool fault_kill_asserted;
    bool session_open;
    bool lease_active;
    bool evidence_mismatch_pending;
    bool evidence_grace_active;
    bool temperatures_valid;
    bool power_fault;
} l2_safety_t;

void l2_safety_init(l2_safety_t *state, int16_t maximum_temperature_deci_c);
bool l2_safety_set_run(l2_safety_t *state, bool run, uint32_t now_ms);
bool l2_safety_heartbeat(l2_safety_t *state, uint32_t sequence, uint32_t now_ms);
bool l2_safety_grant_lease(
    l2_safety_t *state,
    l2_group_t group,
    uint32_t lifetime_ms,
    uint32_t now_ms
);
void l2_safety_revoke_lease(l2_safety_t *state, uint32_t now_ms);
void l2_safety_set_evidence(l2_safety_t *state, uint16_t evidence_mask);
void l2_safety_set_temperatures(
    l2_safety_t *state,
    bool valid,
    int16_t power_deci_c,
    int16_t rf_deci_c,
    int16_t ui_deci_c
);
void l2_safety_set_power_fault(l2_safety_t *state, bool active);
void l2_safety_tick(l2_safety_t *state, uint32_t now_ms);
bool l2_safety_watchdog_must_trip(const l2_safety_t *state, uint32_t now_ms);
uint16_t l2_group_evidence_mask(l2_group_t group);
const char *l2_fault_text(l2_fault_t fault);

#endif
