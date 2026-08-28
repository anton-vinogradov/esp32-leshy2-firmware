#include "leshy2/safety_core.h"

#include <stddef.h>

static void quiet(l2_safety_t *state)
{
    state->active_group = L2_GROUP_NONE;
    state->allowed_evidence_mask = 0;
    state->lease_active = false;
}

static void latch_fault(l2_safety_t *state, l2_fault_t fault)
{
    if (state->first_fault == L2_FAULT_NONE) {
        state->first_fault = fault;
    }
    state->fault_kill_asserted = true;
    state->session_open = false;
    state->evidence_grace_active = false;
    state->evidence_mismatch_pending = false;
    quiet(state);
}

uint16_t l2_group_evidence_mask(l2_group_t group)
{
    switch (group) {
    case L2_GROUP_S3_RF: return UINT16_C(1) << 0;
    case L2_GROUP_C5_RF: return UINT16_C(1) << 1;
    case L2_GROUP_NRF24: return UINT16_C(7) << 2;
    case L2_GROUP_CC1101: return UINT16_C(1) << 5;
    case L2_GROUP_VOICE: return UINT16_C(1) << 6;
    case L2_GROUP_IR: return UINT16_C(1) << 7;
    case L2_GROUP_LORA_CAP: return UINT16_C(1) << 8;
    case L2_GROUP_U219_NFC: return UINT16_C(1) << 12;
    case L2_GROUP_NONE:
    case L2_GROUP_M5_UNIT:
    case L2_GROUP_BROADCAST_RX:
    default:
        return 0;
    }
}

void l2_safety_init(l2_safety_t *state, int16_t maximum_temperature_deci_c)
{
    *state = (l2_safety_t){0};
    state->fault_kill_asserted = true;
    state->first_fault = L2_FAULT_RUN_KILL;
    state->maximum_temperature_deci_c = maximum_temperature_deci_c;
}

bool l2_safety_set_run(l2_safety_t *state, bool run, uint32_t now_ms)
{
    state->now_ms = now_ms;
    state->last_tick_ms = now_ms;
    state->run_requested = run;
    quiet(state);
    state->session_open = false;
    state->evidence_grace_active = false;
    state->evidence_mismatch_pending = false;

    if (!run) {
        state->fault_kill_asserted = true;
        return true;
    }
    if (!state->temperatures_valid || state->power_fault) {
        state->fault_kill_asserted = true;
        return false;
    }
    for (size_t index = 0; index < 3; ++index) {
        if (state->temperatures_deci_c[index] > state->maximum_temperature_deci_c) {
            state->fault_kill_asserted = true;
            return false;
        }
    }
    state->first_fault = L2_FAULT_NONE;
    state->fault_kill_asserted = false;
    state->last_watchdog_service_ms = now_ms;
    return true;
}

bool l2_safety_heartbeat(l2_safety_t *state, uint32_t sequence, uint32_t now_ms)
{
    if (!state->run_requested || state->fault_kill_asserted) {
        return false;
    }
    if (state->session_open) {
        const uint32_t advance = sequence - state->last_heartbeat_sequence;
        if (advance == 0 || advance >= UINT32_C(0x80000000)) {
            return false;
        }
    }
    state->session_open = true;
    state->last_heartbeat_sequence = sequence;
    state->last_heartbeat_ms = now_ms;
    return true;
}

bool l2_safety_grant_lease(
    l2_safety_t *state,
    l2_group_t group,
    uint32_t lifetime_ms,
    uint32_t now_ms
)
{
    const uint16_t evidence_mask = l2_group_evidence_mask(group);
    if (!state->run_requested || state->fault_kill_asserted || !state->session_open) {
        return false;
    }
    if (group == L2_GROUP_NONE || evidence_mask == 0 || lifetime_ms == 0 ||
        lifetime_ms > L2_LEASE_LIFETIME_MAX_MS) {
        return false;
    }
    state->active_group = group;
    state->allowed_evidence_mask = evidence_mask;
    state->lease_expiry_ms = now_ms + lifetime_ms;
    state->lease_active = true;
    state->evidence_grace_active = false;
    state->evidence_mismatch_pending = false;
    return true;
}

void l2_safety_revoke_lease(l2_safety_t *state, uint32_t now_ms)
{
    const bool evidence_was_live = state->observed_evidence_mask != 0;
    quiet(state);
    state->evidence_mismatch_pending = false;
    state->evidence_grace_active = evidence_was_live;
    state->evidence_grace_expiry_ms = now_ms + L2_POST_REVOKE_GRACE_MS;
}

void l2_safety_set_evidence(l2_safety_t *state, uint16_t evidence_mask)
{
    state->observed_evidence_mask = evidence_mask & UINT16_C(0x11ff);
    if (!state->evidence_grace_active &&
        (state->observed_evidence_mask & (uint16_t)~state->allowed_evidence_mask) != 0) {
        state->evidence_mismatch_pending = true;
        state->evidence_mismatch_since_ms = state->now_ms;
    } else {
        state->evidence_mismatch_pending = false;
    }
}

void l2_safety_set_temperatures(
    l2_safety_t *state,
    bool valid,
    int16_t power_deci_c,
    int16_t rf_deci_c,
    int16_t ui_deci_c
)
{
    state->temperatures_valid = valid;
    state->temperatures_deci_c[0] = power_deci_c;
    state->temperatures_deci_c[1] = rf_deci_c;
    state->temperatures_deci_c[2] = ui_deci_c;
}

void l2_safety_set_power_fault(l2_safety_t *state, bool active)
{
    state->power_fault = active;
}

void l2_safety_tick(l2_safety_t *state, uint32_t now_ms)
{
    if (now_ms < state->now_ms) {
        latch_fault(state, L2_FAULT_SAFETY_LOOP_OVERRUN);
        return;
    }
    if (now_ms - state->last_tick_ms > L2_SAFETY_LOOP_PERIOD_MAX_MS) {
        latch_fault(state, L2_FAULT_SAFETY_LOOP_OVERRUN);
    }
    state->now_ms = now_ms;
    state->last_tick_ms = now_ms;

    if (!state->run_requested) {
        state->fault_kill_asserted = true;
        quiet(state);
        return;
    }
    if (state->fault_kill_asserted) {
        return;
    }
    if (!state->temperatures_valid) {
        latch_fault(state, L2_FAULT_THERMAL_SENSOR);
        return;
    }
    for (size_t index = 0; index < 3; ++index) {
        if (state->temperatures_deci_c[index] > state->maximum_temperature_deci_c) {
            latch_fault(state, L2_FAULT_OVER_TEMPERATURE);
            return;
        }
    }
    if (state->power_fault) {
        latch_fault(state, L2_FAULT_POWER);
        return;
    }
    if (state->session_open && now_ms - state->last_heartbeat_ms > L2_HEARTBEAT_GAP_MAX_MS) {
        latch_fault(state, L2_FAULT_HEARTBEAT_LOST);
        return;
    }
    if (state->lease_active && now_ms >= state->lease_expiry_ms) {
        latch_fault(state, L2_FAULT_LEASE_EXPIRED);
        return;
    }

    if (state->evidence_grace_active) {
        if (state->observed_evidence_mask == 0) {
            state->evidence_grace_active = false;
        } else if (now_ms >= state->evidence_grace_expiry_ms) {
            latch_fault(state, L2_FAULT_POST_REVOKE_EVIDENCE);
            return;
        }
    } else {
        const uint16_t unexpected =
            state->observed_evidence_mask & (uint16_t)~state->allowed_evidence_mask;
        if (unexpected != 0) {
            if (!state->evidence_mismatch_pending) {
                state->evidence_mismatch_pending = true;
                state->evidence_mismatch_since_ms = now_ms;
            }
            if (now_ms - state->evidence_mismatch_since_ms >=
                L2_UNEXPECTED_EVIDENCE_MAX_MS) {
                latch_fault(state, L2_FAULT_UNEXPECTED_EVIDENCE);
                return;
            }
        } else {
            state->evidence_mismatch_pending = false;
        }
    }

    state->last_watchdog_service_ms = now_ms;
}

bool l2_safety_watchdog_must_trip(const l2_safety_t *state, uint32_t now_ms)
{
    return now_ms - state->last_watchdog_service_ms >= L2_EXTERNAL_WATCHDOG_TIMEOUT_MS;
}

const char *l2_fault_text(l2_fault_t fault)
{
    switch (fault) {
    case L2_FAULT_NONE: return "No fault";
    case L2_FAULT_RUN_KILL: return "RUN/KILL is in KILL";
    case L2_FAULT_HEARTBEAT_LOST: return "Controller heartbeat lost";
    case L2_FAULT_LEASE_EXPIRED: return "Transmit lease expired";
    case L2_FAULT_UNEXPECTED_EVIDENCE: return "Unexpected physical transmission detected";
    case L2_FAULT_POST_REVOKE_EVIDENCE: return "Transmission continued after revoke";
    case L2_FAULT_THERMAL_SENSOR: return "Thermal sensor invalid";
    case L2_FAULT_OVER_TEMPERATURE: return "Safe temperature exceeded";
    case L2_FAULT_POWER: return "Power-path fault";
    case L2_FAULT_SAFETY_LOOP_OVERRUN: return "Safety loop missed its deadline";
    default: return "Unknown safety fault";
    }
}
