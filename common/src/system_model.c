#include "leshy2/system_model.h"

#include <stddef.h>

static const uint8_t queue_capacities[L2_PRIORITY_COUNT] = {4, 8, 8, 16, 16};

enum {
    L2_CC1101_STROBE_RESET = 0x30,
    L2_CC1101_STROBE_XOFF = 0x32,
    L2_CC1101_STROBE_CALIBRATE = 0x33,
    L2_CC1101_STROBE_RX = 0x34,
    L2_CC1101_STROBE_IDLE = 0x36,
    L2_CC1101_STROBE_POWER_DOWN = 0x39,
    L2_CC1101_STROBE_FLUSH_RX = 0x3a,
    L2_CC1101_STROBE_NOP = 0x3d,
    L2_CC1101_REGISTER_MCSM1 = 0x17,
    L2_CC1101_REGISTER_MCSM0 = 0x18,
    L2_CC1101_REGISTER_LAST_CONFIGURATION = 0x2e,
    L2_CC1101_MCSM1_RXOFF_MASK = 0x0c,
    L2_CC1101_MCSM1_RXOFF_IDLE = 0x00,
    L2_CC1101_MCSM1_RXOFF_RX = 0x0c,
    L2_CC1101_MCSM0_PIN_CTRL_EN = 0x02,
};

void l2_cap_init(l2_cap_state_t *state)
{
    *state = (l2_cap_state_t){0};
    state->profile = L2_CAP_PROFILE_UNKNOWN;
    state->phase = L2_CAP_OFF;
    state->spi_target = L2_CAP_SPI_NONE;
    state->contact10_high = true;
    state->contact14_high = true;
}

bool l2_cap_select_profile(
    l2_cap_state_t *state,
    l2_cap_profile_t profile,
    bool signed_profile_verified
)
{
    if (state->phase != L2_CAP_OFF || !signed_profile_verified ||
        (profile != L2_CAP_PROFILE_U214 && profile != L2_CAP_PROFILE_U219)) {
        return false;
    }
    state->profile = profile;
    state->signed_profile_verified = true;
    state->phase = L2_CAP_PROFILE_SELECTED;
    return true;
}

bool l2_cap_start_power(l2_cap_state_t *state)
{
    if (state->phase != L2_CAP_PROFILE_SELECTED ||
        !state->signed_profile_verified) {
        return false;
    }
    state->branch_power_enabled = true;
    state->io_connected = false;
    state->contact8_high = false;
    state->contact10_is_output = state->profile == L2_CAP_PROFILE_U219;
    state->contact10_high = true;
    state->contact14_high = true;
    state->phase = L2_CAP_POWERING;
    return true;
}

bool l2_cap_observe_power_good(l2_cap_state_t *state, bool power_good)
{
    if (state->phase != L2_CAP_POWERING) {
        return false;
    }
    if (!power_good) {
        l2_cap_init(state);
        state->phase = L2_CAP_FAULT;
        return false;
    }
    state->io_connected = true;
    state->phase = L2_CAP_IO_READY;
    return true;
}

bool l2_cap_release_device(l2_cap_state_t *state)
{
    if (state->phase != L2_CAP_IO_READY || !state->io_connected ||
        !state->branch_power_enabled) {
        return false;
    }
    state->contact8_high = true;
    state->phase = L2_CAP_ACTIVE;
    return true;
}

void l2_cap_shutdown(l2_cap_state_t *state)
{
    l2_cap_init(state);
}

bool l2_cap_spi_select(l2_cap_state_t *state, l2_cap_spi_target_t target)
{
    if (state->phase != L2_CAP_ACTIVE || state->spi_target != L2_CAP_SPI_NONE ||
        !state->io_connected || !state->contact8_high || state->nfc_field_active) {
        return false;
    }
    const bool u214_target = state->profile == L2_CAP_PROFILE_U214 &&
        target == L2_CAP_SPI_U214_SX1262;
    const bool u219_target = state->profile == L2_CAP_PROFILE_U219 &&
        (target == L2_CAP_SPI_U219_CC1101 || target == L2_CAP_SPI_U219_NFC);
    if (!u214_target && !u219_target) {
        return false;
    }
    state->spi_target = target;
    if (target == L2_CAP_SPI_U219_NFC) {
        state->contact10_high = false;
    } else {
        state->contact14_high = false;
    }
    return true;
}

void l2_cap_spi_deselect(l2_cap_state_t *state)
{
    state->spi_target = L2_CAP_SPI_NONE;
    state->contact10_high = true;
    state->contact14_high = true;
}

uint8_t l2_cap_spi_mode(l2_cap_spi_target_t target)
{
    if (target == L2_CAP_SPI_U219_NFC) {
        return 1;
    }
    return 0;
}

bool l2_cap_nfc_operation_supported(l2_cap_nfc_operation_t operation)
{
    return operation == L2_CAP_NFC_POLL || operation == L2_CAP_NFC_READ;
}

bool l2_cap_nfc_begin_field(
    l2_cap_state_t *state,
    l2_cap_nfc_operation_t operation,
    bool runtime_hil_gate_closed,
    bool physical_evidence_lease_active
)
{
    if (L2_U219_NFC_FIELD_HIL_CLOSED == 0 || !runtime_hil_gate_closed ||
        !physical_evidence_lease_active || !l2_cap_nfc_operation_supported(operation) ||
        state->profile != L2_CAP_PROFILE_U219 || state->phase != L2_CAP_ACTIVE ||
        state->spi_target != L2_CAP_SPI_U219_NFC) {
        return false;
    }
    state->nfc_field_active = true;
    return true;
}

void l2_cap_nfc_end_field(l2_cap_state_t *state)
{
    state->nfc_field_active = false;
}

bool l2_cap_cc1101_access_allowed(
    const l2_cap_state_t *state,
    l2_cc1101_access_t access,
    uint8_t address,
    uint8_t value
)
{
    if (state->profile != L2_CAP_PROFILE_U219 || state->phase != L2_CAP_ACTIVE ||
        state->spi_target != L2_CAP_SPI_U219_CC1101) {
        return false;
    }
    if (access == L2_CC1101_READ) {
        return true;
    }
    if (access == L2_CC1101_STROBE) {
        switch (address) {
        case L2_CC1101_STROBE_RESET:
        case L2_CC1101_STROBE_XOFF:
        case L2_CC1101_STROBE_CALIBRATE:
        case L2_CC1101_STROBE_RX:
        case L2_CC1101_STROBE_IDLE:
        case L2_CC1101_STROBE_POWER_DOWN:
        case L2_CC1101_STROBE_FLUSH_RX:
        case L2_CC1101_STROBE_NOP:
            return true;
        default:
            return false;
        }
    }
    if (access != L2_CC1101_WRITE_REGISTER ||
        address > L2_CC1101_REGISTER_LAST_CONFIGURATION) {
        return false;
    }
    if (address == L2_CC1101_REGISTER_MCSM0 &&
        (value & L2_CC1101_MCSM0_PIN_CTRL_EN) != 0) {
        return false;
    }
    if (address == L2_CC1101_REGISTER_MCSM1) {
        const uint8_t rxoff = value & L2_CC1101_MCSM1_RXOFF_MASK;
        if (rxoff != L2_CC1101_MCSM1_RXOFF_IDLE &&
            rxoff != L2_CC1101_MCSM1_RXOFF_RX) {
            return false;
        }
    }
    return true;
}

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
    if ((unsigned)priority >= (unsigned)L2_PRIORITY_COUNT) {
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
    l2_receiver_init(&model->receiver);
    l2_update_init(&model->update, initial_build);
    l2_scheduler_init(&model->scheduler);
    l2_cap_init(&model->cap);
    for (size_t index = 0; index < L2_UPDATE_DOMAIN_COUNT; ++index) {
        model->domain_online[index] = true;
    }
    model->rf_domains_held_in_reset = true;
}

bool l2_system_model_set_run(l2_system_model_t *model, bool run, uint32_t now_ms)
{
    if (run && (!model->domain_online[L2_UPDATE_S3] ||
                !model->domain_online[L2_UPDATE_HUB_RP] ||
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
        !model->domain_online[L2_UPDATE_HUB_RP] ||
        !model->domain_online[L2_UPDATE_SAFETY]) {
        return false;
    }
    return l2_safety_heartbeat(&model->safety, sequence, now_ms);
}

bool l2_system_model_request_receiver(
    l2_system_model_t *model,
    l2_receiver_mode_t mode,
    uint32_t frequency_khz
)
{
    if (!model->domain_online[L2_UPDATE_HUB_RP] ||
        !model->domain_online[L2_UPDATE_PACK] ||
        !model->domain_online[L2_UPDATE_SAFETY] ||
        model->safety.fault_kill_asserted) {
        return false;
    }
    return l2_receiver_request(&model->receiver, mode, frequency_khz);
}

void l2_system_model_observe_receiver(
    l2_system_model_t *model,
    bool lo_locked,
    bool rf_path_settled
)
{
    l2_receiver_observe(
        &model->receiver,
        model->domain_online[L2_UPDATE_HUB_RP],
        lo_locked,
        rf_path_settled
    );
}

void l2_system_model_set_domain_online(
    l2_system_model_t *model,
    l2_update_domain_t domain,
    bool online
)
{
    if ((unsigned)domain < (unsigned)L2_UPDATE_DOMAIN_COUNT) {
        model->domain_online[domain] = online;
    }
}

void l2_system_model_tick(l2_system_model_t *model, uint32_t now_ms)
{
    if (!model->domain_online[L2_UPDATE_HUB_RP]) {
        model->domain_online[L2_UPDATE_C5] = false;
        model->domain_online[L2_UPDATE_RF_RP] = false;
        l2_receiver_observe(&model->receiver, false, false, false);
    }
    if (!model->domain_online[L2_UPDATE_PACK]) {
        l2_safety_set_power_fault(&model->safety, true);
    }
    if (!model->domain_online[L2_UPDATE_SAFETY]) {
        (void)l2_receiver_request(
            &model->receiver, L2_RECEIVER_MODE_DISABLED, 0
        );
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
    model->domain_online[L2_UPDATE_RF_RP] = false;
    model->domain_online[L2_UPDATE_HUB_RP] = false;
    (void)l2_receiver_request(
        &model->receiver, L2_RECEIVER_MODE_DISABLED, 0
    );
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
