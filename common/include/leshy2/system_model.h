#ifndef LESHY2_SYSTEM_MODEL_H
#define LESHY2_SYSTEM_MODEL_H

#include "leshy2/safety_core.h"
#include "leshy2/update_core.h"

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    L2_PRIORITY_SAFETY = 0,
    L2_PRIORITY_CONTROL = 1,
    L2_PRIORITY_INTERACTIVE = 2,
    L2_PRIORITY_TELEMETRY = 3,
    L2_PRIORITY_BULK = 4,
    L2_PRIORITY_COUNT = 5,
} l2_priority_t;

enum { L2_QUEUE_STORAGE = 16 };

typedef struct {
    uint16_t message_ids[L2_QUEUE_STORAGE];
    uint8_t head;
    uint8_t count;
    uint8_t capacity;
    uint32_t dropped;
} l2_queue_t;

typedef struct {
    l2_queue_t queue[L2_PRIORITY_COUNT];
} l2_scheduler_t;

typedef struct {
    l2_safety_t safety;
    l2_update_t update;
    l2_scheduler_t scheduler;
    bool domain_online[L2_UPDATE_DOMAIN_COUNT];
    bool rf_domains_held_in_reset;
    bool external_watchdog_tripped;
    bool fault_viewer_available;
    bool retained_fault_valid;
    l2_fault_t retained_fault;
} l2_system_model_t;

void l2_scheduler_init(l2_scheduler_t *scheduler);
bool l2_scheduler_enqueue(
    l2_scheduler_t *scheduler,
    l2_priority_t priority,
    uint16_t message_id
);
bool l2_scheduler_dequeue(
    l2_scheduler_t *scheduler,
    l2_priority_t *priority,
    uint16_t *message_id
);

void l2_system_model_init(
    l2_system_model_t *model,
    int16_t maximum_temperature_deci_c,
    uint32_t initial_build
);
bool l2_system_model_set_run(l2_system_model_t *model, bool run, uint32_t now_ms);
bool l2_system_model_heartbeat(
    l2_system_model_t *model,
    uint32_t sequence,
    uint32_t now_ms
);
void l2_system_model_set_domain_online(
    l2_system_model_t *model,
    l2_update_domain_t domain,
    bool online
);
void l2_system_model_tick(l2_system_model_t *model, uint32_t now_ms);
const char *l2_system_model_fault_text(const l2_system_model_t *model);

#endif
