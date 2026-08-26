#ifndef LESHY2_HIGH_SPEED_ADAPTER_H
#define LESHY2_HIGH_SPEED_ADAPTER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

enum {
    L2_HS_BUFFER_COUNT = 32,
    L2_HS_CELL_BYTES = 512,
    L2_HS_BULK_CREDITS_MAX = 8,
    L2_HS_PENDING_MAX = 8,
    L2_HS_RESULT_CACHE_MAX = 8,
    L2_HS_LIVENESS_GAP_MS = 200,
    L2_HS_INVALID_HANDLE = 255,
};

typedef enum {
    L2_HS_DOWN = 0,
    L2_HS_STARTING,
    L2_HS_NEGOTIATING,
    L2_HS_READY,
    L2_HS_QUIESCING,
    L2_HS_FAULTED,
    L2_HS_RESETTING,
    L2_HS_STATE_COUNT,
} l2_hs_state_t;

typedef enum {
    L2_HS_PRIORITY_SAFETY = 0,
    L2_HS_PRIORITY_CONTROL,
    L2_HS_PRIORITY_INTERACTIVE,
    L2_HS_PRIORITY_TELEMETRY,
    L2_HS_PRIORITY_BULK,
    L2_HS_PRIORITY_COUNT,
} l2_hs_priority_t;

typedef enum {
    L2_HS_BUFFER_FREE = 0,
    L2_HS_BUFFER_APP_OWNED,
    L2_HS_BUFFER_QUEUED,
    L2_HS_BUFFER_PHY_OWNED,
    L2_HS_BUFFER_VALIDATING,
    L2_HS_BUFFER_DISPATCHED,
} l2_hs_buffer_owner_t;

typedef enum {
    L2_HS_OK = 0,
    L2_HS_NEW,
    L2_HS_DUPLICATE_PENDING,
    L2_HS_DUPLICATE_CACHED,
    L2_HS_STALE,
    L2_HS_BUSY,
    L2_HS_NO_CREDIT,
    L2_HS_DEADLINE_EXPIRED,
    L2_HS_INVALID_STATE,
    L2_HS_INVALID_ARGUMENT,
    L2_HS_SESSION_MISMATCH,
    L2_HS_OWNERSHIP_ERROR,
    L2_HS_FAULT,
} l2_hs_result_t;

typedef struct {
    l2_hs_buffer_owner_t owner;
    l2_hs_priority_t priority;
    uint32_t message_id;
    uint64_t deadline_at_ms;
    uint64_t order;
    bool side_effect;
    bool bulk_credit_reserved;
} l2_hs_buffer_t;

typedef struct {
    bool used;
    uint32_t message_id;
    uint64_t deadline_at_ms;
} l2_hs_pending_t;

typedef struct {
    bool used;
    uint32_t message_id;
    int32_t result_code;
    uint32_t owner_state;
    uint64_t order;
} l2_hs_cached_result_t;

typedef struct {
    l2_hs_state_t state;
    uint32_t local_boot_id;
    uint32_t peer_boot_id;
    bool session_valid;
    uint64_t last_valid_pong_ms;
    l2_hs_buffer_t tx[L2_HS_BUFFER_COUNT];
    l2_hs_buffer_t rx[L2_HS_BUFFER_COUNT];
    uint64_t queue_order;
    uint32_t telemetry_dropped;
    uint32_t remote_bulk_granted_total;
    uint32_t remote_bulk_consumed_total;
    uint32_t receive_bulk_granted_total;
    uint32_t receive_bulk_consumed_total;
    uint32_t highest_message_id;
    bool highest_message_id_valid;
    l2_hs_pending_t pending[L2_HS_PENDING_MAX];
    l2_hs_cached_result_t cache[L2_HS_RESULT_CACHE_MAX];
    uint64_t result_order;
} l2_hs_adapter_t;

void l2_hs_init(l2_hs_adapter_t *adapter);
l2_hs_result_t l2_hs_transition(l2_hs_adapter_t *adapter, l2_hs_state_t next);
l2_hs_result_t l2_hs_accept_handshake(
    l2_hs_adapter_t *adapter,
    uint32_t local_boot_id,
    uint32_t peer_boot_id,
    bool protocol_major_compatible,
    bool capability_hash_accepted,
    uint64_t now_ms
);
void l2_hs_transport_fault(l2_hs_adapter_t *adapter);
l2_hs_result_t l2_hs_observe_peer_boot(
    l2_hs_adapter_t *adapter,
    uint32_t peer_boot_id
);
l2_hs_result_t l2_hs_note_pong(
    l2_hs_adapter_t *adapter,
    uint32_t peer_boot_id,
    uint64_t now_ms
);
l2_hs_result_t l2_hs_tick(l2_hs_adapter_t *adapter, uint64_t now_ms);
bool l2_hs_side_effects_open(const l2_hs_adapter_t *adapter);

l2_hs_result_t l2_hs_tx_acquire(
    l2_hs_adapter_t *adapter,
    l2_hs_priority_t priority,
    uint8_t *handle
);
l2_hs_result_t l2_hs_tx_enqueue(
    l2_hs_adapter_t *adapter,
    uint8_t handle,
    uint32_t message_id,
    bool side_effect,
    uint64_t deadline_at_ms,
    uint64_t now_ms
);
l2_hs_result_t l2_hs_tx_take_next(
    l2_hs_adapter_t *adapter,
    uint64_t now_ms,
    uint8_t *handle
);
l2_hs_result_t l2_hs_tx_complete(l2_hs_adapter_t *adapter, uint8_t handle);
l2_hs_result_t l2_hs_tx_cancel(l2_hs_adapter_t *adapter, uint8_t handle);

l2_hs_result_t l2_hs_rx_phy_begin(
    l2_hs_adapter_t *adapter,
    l2_hs_priority_t priority,
    uint8_t *handle
);
l2_hs_result_t l2_hs_rx_finish_phy(l2_hs_adapter_t *adapter, uint8_t handle);
l2_hs_result_t l2_hs_rx_dispatch(l2_hs_adapter_t *adapter, uint8_t handle);
l2_hs_result_t l2_hs_rx_reject(l2_hs_adapter_t *adapter, uint8_t handle);
l2_hs_result_t l2_hs_rx_release(l2_hs_adapter_t *adapter, uint8_t handle);

l2_hs_result_t l2_hs_seed_receive_bulk_credit(l2_hs_adapter_t *adapter);
uint8_t l2_hs_receive_bulk_credit(const l2_hs_adapter_t *adapter);
l2_hs_result_t l2_hs_apply_remote_bulk_grant(
    l2_hs_adapter_t *adapter,
    uint32_t peer_boot_id,
    uint32_t granted_total
);
uint8_t l2_hs_remote_bulk_credit(const l2_hs_adapter_t *adapter);

l2_hs_result_t l2_hs_receive_request(
    l2_hs_adapter_t *adapter,
    uint32_t peer_boot_id,
    uint32_t message_id,
    bool side_effect,
    uint16_t deadline_ms,
    uint64_t now_ms
);
l2_hs_result_t l2_hs_request_can_commit(
    const l2_hs_adapter_t *adapter,
    uint32_t message_id,
    uint64_t now_ms
);
l2_hs_result_t l2_hs_finish_request(
    l2_hs_adapter_t *adapter,
    uint32_t message_id,
    int32_t result_code,
    uint32_t owner_state
);
bool l2_hs_cached_result(
    const l2_hs_adapter_t *adapter,
    uint32_t message_id,
    int32_t *result_code,
    uint32_t *owner_state
);
size_t l2_hs_pending_count(const l2_hs_adapter_t *adapter);

#endif
