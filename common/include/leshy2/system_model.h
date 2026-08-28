#ifndef LESHY2_SYSTEM_MODEL_H
#define LESHY2_SYSTEM_MODEL_H

#include "leshy2/safety_core.h"
#include "leshy2/receiver_core.h"
#include "leshy2/update_core.h"

#include <stdbool.h>
#include <stdint.h>

#ifndef L2_U219_NFC_FIELD_HIL_CLOSED
#define L2_U219_NFC_FIELD_HIL_CLOSED 0
#endif

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

typedef enum {
    L2_CAP_PROFILE_UNKNOWN = 0,
    L2_CAP_PROFILE_U214,
    L2_CAP_PROFILE_U219,
} l2_cap_profile_t;

typedef enum {
    L2_CAP_OFF = 0,
    L2_CAP_PROFILE_SELECTED,
    L2_CAP_POWERING,
    L2_CAP_IO_READY,
    L2_CAP_ACTIVE,
    L2_CAP_FAULT,
} l2_cap_phase_t;

typedef enum {
    L2_CAP_SPI_NONE = 0,
    L2_CAP_SPI_U214_SX1262,
    L2_CAP_SPI_U219_CC1101,
    L2_CAP_SPI_U219_NFC,
} l2_cap_spi_target_t;

typedef enum {
    L2_CAP_NFC_POLL = 0,
    L2_CAP_NFC_READ,
    L2_CAP_NFC_WRITE,
    L2_CAP_NFC_CARD_EMULATION,
} l2_cap_nfc_operation_t;

typedef enum {
    L2_CC1101_READ = 0,
    L2_CC1101_STROBE,
    L2_CC1101_WRITE_REGISTER,
    L2_CC1101_WRITE_PATABLE,
    L2_CC1101_WRITE_TX_FIFO,
} l2_cc1101_access_t;

typedef struct {
    l2_cap_profile_t profile;
    l2_cap_phase_t phase;
    l2_cap_spi_target_t spi_target;
    bool signed_profile_verified;
    bool branch_power_enabled;
    bool io_connected;
    bool contact8_high;
    bool contact10_is_output;
    bool contact10_high;
    bool contact14_high;
    bool nfc_field_active;
} l2_cap_state_t;

typedef struct {
    l2_safety_t safety;
    l2_receiver_t receiver;
    l2_update_t update;
    l2_scheduler_t scheduler;
    bool domain_online[L2_UPDATE_DOMAIN_COUNT];
    bool rf_domains_held_in_reset;
    bool external_watchdog_tripped;
    bool fault_viewer_available;
    bool retained_fault_valid;
    l2_fault_t retained_fault;
    l2_cap_state_t cap;
} l2_system_model_t;

void l2_cap_init(l2_cap_state_t *state);
bool l2_cap_select_profile(
    l2_cap_state_t *state,
    l2_cap_profile_t profile,
    bool signed_profile_verified
);
bool l2_cap_start_power(l2_cap_state_t *state);
bool l2_cap_observe_power_good(l2_cap_state_t *state, bool power_good);
bool l2_cap_release_device(l2_cap_state_t *state);
void l2_cap_shutdown(l2_cap_state_t *state);
bool l2_cap_spi_select(l2_cap_state_t *state, l2_cap_spi_target_t target);
void l2_cap_spi_deselect(l2_cap_state_t *state);
uint8_t l2_cap_spi_mode(l2_cap_spi_target_t target);
bool l2_cap_nfc_operation_supported(l2_cap_nfc_operation_t operation);
bool l2_cap_nfc_begin_field(
    l2_cap_state_t *state,
    l2_cap_nfc_operation_t operation,
    bool runtime_hil_gate_closed,
    bool physical_evidence_lease_active
);
void l2_cap_nfc_end_field(l2_cap_state_t *state);
bool l2_cap_cc1101_access_allowed(
    const l2_cap_state_t *state,
    l2_cc1101_access_t access,
    uint8_t address,
    uint8_t value
);

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
bool l2_system_model_request_receiver(
    l2_system_model_t *model,
    l2_receiver_mode_t mode,
    uint32_t frequency_khz
);
void l2_system_model_observe_receiver(
    l2_system_model_t *model,
    bool lo_locked,
    bool rf_path_settled
);
void l2_system_model_set_domain_online(
    l2_system_model_t *model,
    l2_update_domain_t domain,
    bool online
);
void l2_system_model_tick(l2_system_model_t *model, uint32_t now_ms);
const char *l2_system_model_fault_text(const l2_system_model_t *model);

#endif
