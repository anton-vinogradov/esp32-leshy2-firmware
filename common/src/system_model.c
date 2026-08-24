#include "leshy2/system_model.h"

#include <stddef.h>

static const uint8_t queue_capacities[L2_PRIORITY_COUNT] = {4, 8, 8, 16, 16};

void l2_scheduler_init(l2_scheduler_t *scheduler)
{
    *scheduler = (l2_scheduler_t){0};
    for (size_t index = 0; index < L2_PRIORITY_COUNT; ++index) {
        scheduler->queue[index].capacity = queue_capacities[index];
    }
}

bool l2_scheduler_enqueue(
    l2_scheduler_t *scheduler,
    l2_priority_t priority,
    uint16_t message_id
)
{
    if (priority < L2_PRIORITY_SAFETY || priority >= L2_PRIORITY_COUNT) {
        return false;
    }
    l2_queue_t *queue = &scheduler->queue[priority];
    if (queue->count == queue->capacity) {
        if (priority != L2_PRIORITY_TELEMETRY) {
            return false;
        }
        queue->head = (uint8_t)((queue->head + 1U) % queue->capacity);
        queue->count = (uint8_t)(queue->count - 1U);
        queue->dropped += 1U;
    }
    const uint8_t tail = (uint8_t)((queue->head + queue->count) % queue->capacity);
    queue->message_ids[tail] = message_id;
    queue->count = (uint8_t)(queue->count + 1U);
    return true;
}

bool l2_scheduler_dequeue(
    l2_scheduler_t *scheduler,
    l2_priority_t *priority,
    uint16_t *message_id
)
{
    for (size_t index = 0; index < L2_PRIORITY_COUNT; ++index) {
        l2_queue_t *queue = &scheduler->queue[index];
        if (queue->count == 0) {
            continue;
        }
        *priority = (l2_priority_t)index;
        *message_id = queue->message_ids[queue->head];
        queue->head = (uint8_t)((queue->head + 1U) % queue->capacity);
        queue->count = (uint8_t)(queue->count - 1U);
        return true;
    }
    return false;
}

void l2_system_model_init(
    l2_system_model_t *model,
    int16_t maximum_temperature_deci_c,
    uint32_t initial_build
)
{
    *model = (l2_system_model_t){0};
    l2_safety_init(&model->safety, maximum_temperature_deci_c);
    l2_update_init(&model->update, initial_build);
    l2_scheduler_init(&model->scheduler);
    for (size_t index = 0; index < L2_UPDATE_DOMAIN_COUNT; ++index) {
        model->domain_online[index] = true;
    }
    model->rf_domains_held_in_reset = true;
}

bool l2_system_model_set_run(l2_system_model_t *model, bool run, uint32_t now_ms)
{
    if (run && (!model->domain_online[L2_UPDATE_S3] ||
                !model->domain_online[L2_UPDATE_PACK] ||
                !model->domain_online[L2_UPDATE_SAFETY])) {
        return false;
    }
    const bool accepted = l2_safety_set_run(&model->safety, run, now_ms);
    model->rf_domains_held_in_reset = !accepted;
    if (accepted) {
        model->fault_viewer_available = false;
    }
    return accepted;
}

bool l2_system_model_heartbeat(
    l2_system_model_t *model,
    uint32_t sequence,
    uint32_t now_ms
)
{
    if (!model->domain_online[L2_UPDATE_S3] ||
        !model->domain_online[L2_UPDATE_SAFETY]) {
        return false;
    }
    return l2_safety_heartbeat(&model->safety, sequence, now_ms);
}

void l2_system_model_set_domain_online(
    l2_system_model_t *model,
    l2_update_domain_t domain,
    bool online
)
{
    if (domain >= L2_UPDATE_PACK && domain < L2_UPDATE_DOMAIN_COUNT) {
        model->domain_online[domain] = online;
    }
}

void l2_system_model_tick(l2_system_model_t *model, uint32_t now_ms)
{
    if (!model->domain_online[L2_UPDATE_SAFETY]) {
        model->rf_domains_held_in_reset = true;
        model->fault_viewer_available = false;
        if (l2_safety_watchdog_must_trip(&model->safety, now_ms)) {
            model->external_watchdog_tripped = true;
        }
        return;
    }
    l2_safety_tick(&model->safety, now_ms);
    if (!model->safety.fault_kill_asserted) {
        return;
    }

    model->rf_domains_held_in_reset = true;
    model->domain_online[L2_UPDATE_C5] = false;
    model->domain_online[L2_UPDATE_RP] = false;
    if (!model->safety.run_requested || model->safety.first_fault == L2_FAULT_NONE) {
        model->fault_viewer_available = false;
        return;
    }
    if (!model->retained_fault_valid || model->retained_fault == L2_FAULT_RUN_KILL) {
        model->retained_fault = model->safety.first_fault;
        model->retained_fault_valid = true;
    }

    const bool ui_temperature_safe = model->safety.temperatures_valid &&
        model->safety.temperatures_deci_c[2] <= model->safety.maximum_temperature_deci_c;
    model->fault_viewer_available = model->domain_online[L2_UPDATE_S3] &&
        ui_temperature_safe && !model->safety.power_fault;
}

const char *l2_system_model_fault_text(const l2_system_model_t *model)
{
    if (!model->retained_fault_valid) {
        return "No retained fault";
    }
    return l2_fault_text(model->retained_fault);
}
