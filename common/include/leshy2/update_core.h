#ifndef LESHY2_UPDATE_CORE_H
#define LESHY2_UPDATE_CORE_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    L2_UPDATE_PACK = 0,
    L2_UPDATE_SAFETY = 1,
    L2_UPDATE_C5 = 2,
    L2_UPDATE_RF_RP = 3,
    L2_UPDATE_HUB_RP = 4,
    L2_UPDATE_S3 = 5,
    L2_UPDATE_DOMAIN_COUNT = 6,
} l2_update_domain_t;

typedef enum {
    L2_UPDATE_IDLE = 0,
    L2_UPDATE_STAGING,
    L2_UPDATE_VERIFIED,
    L2_UPDATE_ACTIVATING,
    L2_UPDATE_COMMITTED,
    L2_UPDATE_ROLLED_BACK,
} l2_update_phase_t;

typedef enum {
    L2_UPDATE_FAULT_NONE = 0,
    L2_UPDATE_FAULT_PRECONDITION,
    L2_UPDATE_FAULT_INCOMPLETE_BUNDLE,
    L2_UPDATE_FAULT_VERIFY,
    L2_UPDATE_FAULT_ACTIVATION_ORDER,
    L2_UPDATE_FAULT_SELF_TEST,
    L2_UPDATE_FAULT_DEADLINE,
} l2_update_fault_t;

enum { L2_UPDATE_GLOBAL_DEADLINE_MS = 16700 };

typedef struct {
    uint32_t active_build[L2_UPDATE_DOMAIN_COUNT];
    uint32_t previous_build[L2_UPDATE_DOMAIN_COUNT];
    uint32_t pending_build[L2_UPDATE_DOMAIN_COUNT];
    bool staged[L2_UPDATE_DOMAIN_COUNT];
    bool verified[L2_UPDATE_DOMAIN_COUNT];
    bool activated[L2_UPDATE_DOMAIN_COUNT];
    bool self_test_passed[L2_UPDATE_DOMAIN_COUNT];
    uint32_t started_ms;
    unsigned next_activation;
    l2_update_phase_t phase;
    l2_update_fault_t first_fault;
} l2_update_t;

void l2_update_init(l2_update_t *state, uint32_t initial_build);
bool l2_update_begin(
    l2_update_t *state,
    bool physical_kill,
    bool tx_evidence_quiet,
    bool stable_power,
    bool protocol_compatible,
    uint32_t now_ms
);
bool l2_update_stage(
    l2_update_t *state,
    l2_update_domain_t domain,
    uint32_t build_id,
    bool readback_matches
);
bool l2_update_verify_bundle(l2_update_t *state);
bool l2_update_activate(l2_update_t *state, l2_update_domain_t domain, uint32_t now_ms);
bool l2_update_report_self_test(l2_update_t *state, l2_update_domain_t domain, bool passed);
bool l2_update_commit(l2_update_t *state, uint32_t now_ms);
void l2_update_check_deadline(l2_update_t *state, uint32_t now_ms);
void l2_update_rollback(l2_update_t *state, l2_update_fault_t fault);
const char *l2_update_fault_text(l2_update_fault_t fault);

#endif
