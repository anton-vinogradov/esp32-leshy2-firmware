#include "leshy2/update_core.h"

#include <stddef.h>

static const l2_update_domain_t activation_order[L2_UPDATE_DOMAIN_COUNT] = {
    L2_UPDATE_PACK,
    L2_UPDATE_SAFETY,
    L2_UPDATE_C5,
    L2_UPDATE_RP,
    L2_UPDATE_S3,
};

void l2_update_init(l2_update_t *state, uint32_t initial_build)
{
    *state = (l2_update_t){0};
    for (size_t index = 0; index < L2_UPDATE_DOMAIN_COUNT; ++index) {
        state->active_build[index] = initial_build;
        state->previous_build[index] = initial_build;
    }
}

bool l2_update_begin(
    l2_update_t *state,
    bool physical_kill,
    bool tx_evidence_quiet,
    bool stable_power,
    bool protocol_compatible,
    uint32_t now_ms
)
{
    if (!physical_kill || !tx_evidence_quiet || !stable_power || !protocol_compatible) {
        state->first_fault = L2_UPDATE_FAULT_PRECONDITION;
        return false;
    }
    for (size_t index = 0; index < L2_UPDATE_DOMAIN_COUNT; ++index) {
        state->previous_build[index] = state->active_build[index];
        state->pending_build[index] = 0;
        state->staged[index] = false;
        state->verified[index] = false;
        state->activated[index] = false;
        state->self_test_passed[index] = false;
    }
    state->started_ms = now_ms;
    state->next_activation = 0;
    state->phase = L2_UPDATE_STAGING;
    state->first_fault = L2_UPDATE_FAULT_NONE;
    return true;
}

bool l2_update_stage(
    l2_update_t *state,
    l2_update_domain_t domain,
    uint32_t build_id,
    bool readback_matches
)
{
    if (state->phase != L2_UPDATE_STAGING || domain >= L2_UPDATE_DOMAIN_COUNT ||
        build_id == 0 || !readback_matches) {
        if (!readback_matches) {
            l2_update_rollback(state, L2_UPDATE_FAULT_VERIFY);
        }
        return false;
    }
    state->pending_build[domain] = build_id;
    state->staged[domain] = true;
    state->verified[domain] = true;
    return true;
}

bool l2_update_verify_bundle(l2_update_t *state)
{
    if (state->phase != L2_UPDATE_STAGING) {
        return false;
    }
    for (size_t index = 0; index < L2_UPDATE_DOMAIN_COUNT; ++index) {
        if (!state->staged[index] || !state->verified[index]) {
            state->first_fault = L2_UPDATE_FAULT_INCOMPLETE_BUNDLE;
            return false;
        }
    }
    state->phase = L2_UPDATE_VERIFIED;
    return true;
}

bool l2_update_activate(l2_update_t *state, l2_update_domain_t domain, uint32_t now_ms)
{
    l2_update_check_deadline(state, now_ms);
    if ((state->phase != L2_UPDATE_VERIFIED && state->phase != L2_UPDATE_ACTIVATING) ||
        state->next_activation >= L2_UPDATE_DOMAIN_COUNT ||
        activation_order[state->next_activation] != domain) {
        if (state->phase != L2_UPDATE_ROLLED_BACK) {
            l2_update_rollback(state, L2_UPDATE_FAULT_ACTIVATION_ORDER);
        }
        return false;
    }
    state->active_build[domain] = state->pending_build[domain];
    state->activated[domain] = true;
    state->next_activation += 1;
    state->phase = L2_UPDATE_ACTIVATING;
    return true;
}

bool l2_update_report_self_test(l2_update_t *state, l2_update_domain_t domain, bool passed)
{
    if (state->phase != L2_UPDATE_ACTIVATING || domain >= L2_UPDATE_DOMAIN_COUNT ||
        !state->activated[domain]) {
        return false;
    }
    if (!passed) {
        l2_update_rollback(state, L2_UPDATE_FAULT_SELF_TEST);
        return false;
    }
    state->self_test_passed[domain] = true;
    return true;
}

bool l2_update_commit(l2_update_t *state, uint32_t now_ms)
{
    l2_update_check_deadline(state, now_ms);
    if (state->phase != L2_UPDATE_ACTIVATING ||
        state->next_activation != L2_UPDATE_DOMAIN_COUNT) {
        return false;
    }
    for (size_t index = 0; index < L2_UPDATE_DOMAIN_COUNT; ++index) {
        if (!state->activated[index] || !state->self_test_passed[index]) {
            return false;
        }
    }
    state->phase = L2_UPDATE_COMMITTED;
    return true;
}

void l2_update_check_deadline(l2_update_t *state, uint32_t now_ms)
{
    if (state->phase != L2_UPDATE_IDLE && state->phase != L2_UPDATE_COMMITTED &&
        state->phase != L2_UPDATE_ROLLED_BACK &&
        now_ms - state->started_ms > L2_UPDATE_GLOBAL_DEADLINE_MS) {
        l2_update_rollback(state, L2_UPDATE_FAULT_DEADLINE);
    }
}

void l2_update_rollback(l2_update_t *state, l2_update_fault_t fault)
{
    if (state->first_fault == L2_UPDATE_FAULT_NONE) {
        state->first_fault = fault;
    }
    for (size_t index = 0; index < L2_UPDATE_DOMAIN_COUNT; ++index) {
        state->active_build[index] = state->previous_build[index];
        state->activated[index] = false;
        state->self_test_passed[index] = false;
    }
    state->phase = L2_UPDATE_ROLLED_BACK;
}

const char *l2_update_fault_text(l2_update_fault_t fault)
{
    switch (fault) {
    case L2_UPDATE_FAULT_NONE: return "No update fault";
    case L2_UPDATE_FAULT_PRECONDITION: return "Update precondition failed";
    case L2_UPDATE_FAULT_INCOMPLETE_BUNDLE: return "Update bundle incomplete";
    case L2_UPDATE_FAULT_VERIFY: return "Image read-back or signature verification failed";
    case L2_UPDATE_FAULT_ACTIVATION_ORDER: return "Unsafe update activation order";
    case L2_UPDATE_FAULT_SELF_TEST: return "Target self-test failed; previous bundle restored";
    case L2_UPDATE_FAULT_DEADLINE: return "Global update activation deadline exceeded";
    default: return "Unknown update fault";
    }
}
