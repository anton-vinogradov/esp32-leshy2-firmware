#include "leshy2/high_speed_adapter.h"

#include <string.h>

static const uint8_t priority_base[L2_HS_PRIORITY_COUNT] = {0, 4, 12, 20, 24};
static const uint8_t priority_count[L2_HS_PRIORITY_COUNT] = {4, 8, 8, 4, 8};

static bool priority_valid(l2_hs_priority_t priority)
{
    return (unsigned)priority < (unsigned)L2_HS_PRIORITY_COUNT;
}

static bool handle_valid(uint8_t handle)
{
    return handle < L2_HS_BUFFER_COUNT;
}

static bool transition_allowed(l2_hs_state_t source, l2_hs_state_t target)
{
    switch (source) {
    case L2_HS_DOWN:
        return target == L2_HS_STARTING;
    case L2_HS_STARTING:
        return target == L2_HS_NEGOTIATING || target == L2_HS_FAULTED ||
            target == L2_HS_RESETTING || target == L2_HS_DOWN;
    case L2_HS_NEGOTIATING:
        return target == L2_HS_READY || target == L2_HS_FAULTED ||
            target == L2_HS_RESETTING || target == L2_HS_DOWN;
    case L2_HS_READY:
        return target == L2_HS_QUIESCING || target == L2_HS_FAULTED ||
            target == L2_HS_RESETTING;
    case L2_HS_QUIESCING:
        return target == L2_HS_DOWN || target == L2_HS_FAULTED ||
            target == L2_HS_RESETTING;
    case L2_HS_FAULTED:
        return target == L2_HS_RESETTING || target == L2_HS_DOWN;
    case L2_HS_RESETTING:
        return target == L2_HS_STARTING || target == L2_HS_FAULTED ||
            target == L2_HS_DOWN;
    case L2_HS_STATE_COUNT:
        return false;
    }
    return false;
}

static void clear_buffer(l2_hs_buffer_t *buffer)
{
    *buffer = (l2_hs_buffer_t){.owner = L2_HS_BUFFER_FREE};
}

static void clear_session(l2_hs_adapter_t *adapter)
{
    adapter->local_boot_id = 0;
    adapter->peer_boot_id = 0;
    adapter->session_valid = false;
    adapter->last_valid_pong_ms = 0;
    adapter->queue_order = 0;
    adapter->remote_bulk_granted_total = 0;
    adapter->remote_bulk_consumed_total = 0;
    adapter->receive_bulk_granted_total = 0;
    adapter->receive_bulk_consumed_total = 0;
    adapter->highest_message_id = 0;
    adapter->highest_message_id_valid = false;
    memset(adapter->pending, 0, sizeof(adapter->pending));
    memset(adapter->cache, 0, sizeof(adapter->cache));
    for (size_t index = 0; index < L2_HS_BUFFER_COUNT; ++index) {
        clear_buffer(&adapter->tx[index]);
        clear_buffer(&adapter->rx[index]);
    }
}

static bool all_buffers_free(const l2_hs_adapter_t *adapter)
{
    for (size_t index = 0; index < L2_HS_BUFFER_COUNT; ++index) {
        if (adapter->tx[index].owner != L2_HS_BUFFER_FREE ||
            adapter->rx[index].owner != L2_HS_BUFFER_FREE) {
            return false;
        }
    }
    return true;
}

static void enter_fault(l2_hs_adapter_t *adapter)
{
    adapter->state = L2_HS_FAULTED;
    clear_session(adapter);
}

void l2_hs_init(l2_hs_adapter_t *adapter)
{
    *adapter = (l2_hs_adapter_t){.state = L2_HS_DOWN};
}

l2_hs_result_t l2_hs_transition(l2_hs_adapter_t *adapter, l2_hs_state_t next)
{
    if (adapter == NULL || (unsigned)next >= (unsigned)L2_HS_STATE_COUNT) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (next == L2_HS_READY || !transition_allowed(adapter->state, next)) {
        return L2_HS_INVALID_STATE;
    }
    if (adapter->state == L2_HS_QUIESCING && next == L2_HS_DOWN &&
        !all_buffers_free(adapter)) {
        return L2_HS_BUSY;
    }
    adapter->state = next;
    if (next != L2_HS_QUIESCING) {
        clear_session(adapter);
    }
    return L2_HS_OK;
}

l2_hs_result_t l2_hs_accept_handshake(
    l2_hs_adapter_t *adapter,
    uint32_t local_boot_id,
    uint32_t peer_boot_id,
    bool protocol_major_compatible,
    bool capability_hash_accepted,
    uint64_t now_ms
)
{
    if (adapter == NULL || local_boot_id == 0 || peer_boot_id == 0) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (adapter->state != L2_HS_NEGOTIATING) {
        return L2_HS_INVALID_STATE;
    }
    if (!protocol_major_compatible || !capability_hash_accepted) {
        enter_fault(adapter);
        return L2_HS_FAULT;
    }
    clear_session(adapter);
    adapter->local_boot_id = local_boot_id;
    adapter->peer_boot_id = peer_boot_id;
    adapter->session_valid = true;
    adapter->last_valid_pong_ms = now_ms;
    adapter->state = L2_HS_READY;
    return L2_HS_OK;
}

void l2_hs_transport_fault(l2_hs_adapter_t *adapter)
{
    if (adapter != NULL && adapter->state != L2_HS_DOWN) {
        enter_fault(adapter);
    }
}

l2_hs_result_t l2_hs_observe_peer_boot(
    l2_hs_adapter_t *adapter,
    uint32_t peer_boot_id
)
{
    if (adapter == NULL || peer_boot_id == 0) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (adapter->state != L2_HS_READY || !adapter->session_valid) {
        return L2_HS_INVALID_STATE;
    }
    if (peer_boot_id == adapter->peer_boot_id) {
        return L2_HS_OK;
    }
    adapter->state = L2_HS_RESETTING;
    clear_session(adapter);
    return L2_HS_SESSION_MISMATCH;
}

l2_hs_result_t l2_hs_note_pong(
    l2_hs_adapter_t *adapter,
    uint32_t peer_boot_id,
    uint64_t now_ms
)
{
    if (adapter == NULL) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (adapter->state != L2_HS_READY || !adapter->session_valid) {
        return L2_HS_INVALID_STATE;
    }
    if (peer_boot_id != adapter->peer_boot_id) {
        return l2_hs_observe_peer_boot(adapter, peer_boot_id);
    }
    adapter->last_valid_pong_ms = now_ms;
    return L2_HS_OK;
}

l2_hs_result_t l2_hs_tick(l2_hs_adapter_t *adapter, uint64_t now_ms)
{
    if (adapter == NULL) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (adapter->state != L2_HS_READY || !adapter->session_valid) {
        return L2_HS_OK;
    }
    if (now_ms > adapter->last_valid_pong_ms &&
        now_ms - adapter->last_valid_pong_ms > L2_HS_LIVENESS_GAP_MS) {
        enter_fault(adapter);
        return L2_HS_FAULT;
    }
    return L2_HS_OK;
}

bool l2_hs_side_effects_open(const l2_hs_adapter_t *adapter)
{
    return adapter != NULL && adapter->state == L2_HS_READY &&
        adapter->session_valid;
}

static int find_free_buffer(
    const l2_hs_buffer_t buffers[L2_HS_BUFFER_COUNT],
    l2_hs_priority_t priority
)
{
    const uint8_t end = (uint8_t)(priority_base[priority] + priority_count[priority]);
    for (uint8_t index = priority_base[priority]; index < end; ++index) {
        if (buffers[index].owner == L2_HS_BUFFER_FREE) {
            return index;
        }
    }
    return -1;
}

static int oldest_buffer(
    const l2_hs_buffer_t buffers[L2_HS_BUFFER_COUNT],
    l2_hs_priority_t priority,
    l2_hs_buffer_owner_t owner
)
{
    const uint8_t end = (uint8_t)(priority_base[priority] + priority_count[priority]);
    int selected = -1;
    for (uint8_t index = priority_base[priority]; index < end; ++index) {
        if (buffers[index].owner != owner) {
            continue;
        }
        if (selected < 0 || buffers[index].order < buffers[(size_t)selected].order) {
            selected = index;
        }
    }
    return selected;
}

l2_hs_result_t l2_hs_tx_acquire(
    l2_hs_adapter_t *adapter,
    l2_hs_priority_t priority,
    uint8_t *handle
)
{
    if (adapter == NULL || handle == NULL || !priority_valid(priority)) {
        return L2_HS_INVALID_ARGUMENT;
    }
    *handle = L2_HS_INVALID_HANDLE;
    if (adapter->state != L2_HS_READY || !adapter->session_valid) {
        return L2_HS_INVALID_STATE;
    }
    int selected = find_free_buffer(adapter->tx, priority);
    if (selected < 0 && priority == L2_HS_PRIORITY_TELEMETRY) {
        selected = oldest_buffer(adapter->tx, priority, L2_HS_BUFFER_QUEUED);
        if (selected >= 0) {
            clear_buffer(&adapter->tx[(size_t)selected]);
            adapter->telemetry_dropped += 1U;
        }
    }
    if (selected < 0) {
        if (priority == L2_HS_PRIORITY_SAFETY || priority == L2_HS_PRIORITY_CONTROL) {
            enter_fault(adapter);
            return L2_HS_FAULT;
        }
        return L2_HS_BUSY;
    }
    l2_hs_buffer_t *buffer = &adapter->tx[(size_t)selected];
    clear_buffer(buffer);
    buffer->owner = L2_HS_BUFFER_APP_OWNED;
    buffer->priority = priority;
    *handle = (uint8_t)selected;
    return L2_HS_OK;
}

l2_hs_result_t l2_hs_tx_enqueue(
    l2_hs_adapter_t *adapter,
    uint8_t handle,
    uint32_t message_id,
    bool side_effect,
    uint64_t deadline_at_ms,
    uint64_t now_ms
)
{
    if (adapter == NULL || !handle_valid(handle)) {
        return L2_HS_INVALID_ARGUMENT;
    }
    l2_hs_buffer_t *buffer = &adapter->tx[handle];
    if (buffer->owner != L2_HS_BUFFER_APP_OWNED) {
        return L2_HS_OWNERSHIP_ERROR;
    }
    if (adapter->state != L2_HS_READY || !adapter->session_valid) {
        return L2_HS_INVALID_STATE;
    }
    if (side_effect && (deadline_at_ms == 0 || deadline_at_ms <= now_ms)) {
        return L2_HS_DEADLINE_EXPIRED;
    }
    if (buffer->priority == L2_HS_PRIORITY_BULK) {
        if (l2_hs_remote_bulk_credit(adapter) == 0) {
            return L2_HS_NO_CREDIT;
        }
        adapter->remote_bulk_consumed_total += 1U;
        buffer->bulk_credit_reserved = true;
    }
    adapter->queue_order += 1U;
    buffer->message_id = message_id;
    buffer->side_effect = side_effect;
    buffer->deadline_at_ms = deadline_at_ms;
    buffer->order = adapter->queue_order;
    buffer->owner = L2_HS_BUFFER_QUEUED;
    return L2_HS_OK;
}

l2_hs_result_t l2_hs_tx_take_next(
    l2_hs_adapter_t *adapter,
    uint64_t now_ms,
    uint8_t *handle
)
{
    if (adapter == NULL || handle == NULL) {
        return L2_HS_INVALID_ARGUMENT;
    }
    *handle = L2_HS_INVALID_HANDLE;
    if (adapter->state != L2_HS_READY && adapter->state != L2_HS_QUIESCING) {
        return L2_HS_INVALID_STATE;
    }
    for (size_t priority = 0; priority < L2_HS_PRIORITY_COUNT; ++priority) {
        const l2_hs_priority_t typed = (l2_hs_priority_t)priority;
        int selected = oldest_buffer(adapter->tx, typed, L2_HS_BUFFER_QUEUED);
        while (selected >= 0) {
            l2_hs_buffer_t *buffer = &adapter->tx[(size_t)selected];
            if (buffer->side_effect && buffer->deadline_at_ms <= now_ms) {
                if (buffer->bulk_credit_reserved &&
                    adapter->remote_bulk_consumed_total > 0) {
                    adapter->remote_bulk_consumed_total -= 1U;
                }
                clear_buffer(buffer);
                return L2_HS_DEADLINE_EXPIRED;
            }
            buffer->owner = L2_HS_BUFFER_PHY_OWNED;
            *handle = (uint8_t)selected;
            return L2_HS_OK;
        }
    }
    return L2_HS_BUSY;
}

l2_hs_result_t l2_hs_tx_complete(l2_hs_adapter_t *adapter, uint8_t handle)
{
    if (adapter == NULL || !handle_valid(handle)) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (adapter->tx[handle].owner != L2_HS_BUFFER_PHY_OWNED) {
        return L2_HS_OWNERSHIP_ERROR;
    }
    clear_buffer(&adapter->tx[handle]);
    return L2_HS_OK;
}

l2_hs_result_t l2_hs_tx_cancel(l2_hs_adapter_t *adapter, uint8_t handle)
{
    if (adapter == NULL || !handle_valid(handle)) {
        return L2_HS_INVALID_ARGUMENT;
    }
    l2_hs_buffer_t *buffer = &adapter->tx[handle];
    if (buffer->owner != L2_HS_BUFFER_APP_OWNED &&
        buffer->owner != L2_HS_BUFFER_QUEUED) {
        return L2_HS_OWNERSHIP_ERROR;
    }
    if (buffer->bulk_credit_reserved &&
        adapter->remote_bulk_consumed_total > 0) {
        adapter->remote_bulk_consumed_total -= 1U;
    }
    clear_buffer(buffer);
    return L2_HS_OK;
}

l2_hs_result_t l2_hs_rx_phy_begin(
    l2_hs_adapter_t *adapter,
    l2_hs_priority_t priority,
    uint8_t *handle
)
{
    if (adapter == NULL || handle == NULL || !priority_valid(priority)) {
        return L2_HS_INVALID_ARGUMENT;
    }
    *handle = L2_HS_INVALID_HANDLE;
    if (adapter->state != L2_HS_READY || !adapter->session_valid) {
        return L2_HS_INVALID_STATE;
    }
    if (priority == L2_HS_PRIORITY_BULK && l2_hs_receive_bulk_credit(adapter) == 0) {
        enter_fault(adapter);
        return L2_HS_FAULT;
    }
    const int selected = find_free_buffer(adapter->rx, priority);
    if (selected < 0) {
        if (priority == L2_HS_PRIORITY_SAFETY || priority == L2_HS_PRIORITY_CONTROL) {
            enter_fault(adapter);
            return L2_HS_FAULT;
        }
        return L2_HS_BUSY;
    }
    l2_hs_buffer_t *buffer = &adapter->rx[(size_t)selected];
    clear_buffer(buffer);
    buffer->owner = L2_HS_BUFFER_PHY_OWNED;
    buffer->priority = priority;
    if (priority == L2_HS_PRIORITY_BULK) {
        adapter->receive_bulk_consumed_total += 1U;
    }
    *handle = (uint8_t)selected;
    return L2_HS_OK;
}

l2_hs_result_t l2_hs_rx_finish_phy(l2_hs_adapter_t *adapter, uint8_t handle)
{
    if (adapter == NULL || !handle_valid(handle)) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (adapter->rx[handle].owner != L2_HS_BUFFER_PHY_OWNED) {
        return L2_HS_OWNERSHIP_ERROR;
    }
    adapter->rx[handle].owner = L2_HS_BUFFER_VALIDATING;
    return L2_HS_OK;
}

l2_hs_result_t l2_hs_rx_dispatch(l2_hs_adapter_t *adapter, uint8_t handle)
{
    if (adapter == NULL || !handle_valid(handle)) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (adapter->rx[handle].owner != L2_HS_BUFFER_VALIDATING) {
        return L2_HS_OWNERSHIP_ERROR;
    }
    adapter->rx[handle].owner = L2_HS_BUFFER_DISPATCHED;
    return L2_HS_OK;
}

static void release_rx_buffer(l2_hs_adapter_t *adapter, uint8_t handle)
{
    if (adapter->rx[handle].priority == L2_HS_PRIORITY_BULK) {
        adapter->receive_bulk_granted_total += 1U;
    }
    clear_buffer(&adapter->rx[handle]);
}

l2_hs_result_t l2_hs_rx_reject(l2_hs_adapter_t *adapter, uint8_t handle)
{
    if (adapter == NULL || !handle_valid(handle)) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (adapter->rx[handle].owner != L2_HS_BUFFER_VALIDATING) {
        return L2_HS_OWNERSHIP_ERROR;
    }
    if (adapter->rx[handle].priority == L2_HS_PRIORITY_BULK &&
        adapter->receive_bulk_granted_total == UINT32_MAX) {
        enter_fault(adapter);
        return L2_HS_FAULT;
    }
    release_rx_buffer(adapter, handle);
    return L2_HS_OK;
}

l2_hs_result_t l2_hs_rx_release(l2_hs_adapter_t *adapter, uint8_t handle)
{
    if (adapter == NULL || !handle_valid(handle)) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (adapter->rx[handle].owner != L2_HS_BUFFER_DISPATCHED) {
        return L2_HS_OWNERSHIP_ERROR;
    }
    if (adapter->rx[handle].priority == L2_HS_PRIORITY_BULK &&
        adapter->receive_bulk_granted_total == UINT32_MAX) {
        enter_fault(adapter);
        return L2_HS_FAULT;
    }
    release_rx_buffer(adapter, handle);
    return L2_HS_OK;
}

l2_hs_result_t l2_hs_seed_receive_bulk_credit(l2_hs_adapter_t *adapter)
{
    if (adapter == NULL) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (adapter->state != L2_HS_READY || !adapter->session_valid) {
        return L2_HS_INVALID_STATE;
    }
    if (adapter->receive_bulk_granted_total != 0 ||
        adapter->receive_bulk_consumed_total != 0) {
        return L2_HS_INVALID_STATE;
    }
    uint8_t free_count = 0;
    const uint8_t end = (uint8_t)(priority_base[L2_HS_PRIORITY_BULK] +
        priority_count[L2_HS_PRIORITY_BULK]);
    for (uint8_t index = priority_base[L2_HS_PRIORITY_BULK]; index < end; ++index) {
        if (adapter->rx[index].owner == L2_HS_BUFFER_FREE) {
            free_count = (uint8_t)(free_count + 1U);
        }
    }
    if (free_count != L2_HS_BULK_CREDITS_MAX) {
        enter_fault(adapter);
        return L2_HS_FAULT;
    }
    adapter->receive_bulk_granted_total = free_count;
    adapter->receive_bulk_consumed_total = 0;
    return L2_HS_OK;
}

uint8_t l2_hs_receive_bulk_credit(const l2_hs_adapter_t *adapter)
{
    if (adapter == NULL ||
        adapter->receive_bulk_consumed_total > adapter->receive_bulk_granted_total) {
        return 0;
    }
    const uint32_t available = adapter->receive_bulk_granted_total -
        adapter->receive_bulk_consumed_total;
    return available > L2_HS_BULK_CREDITS_MAX ? 0 : (uint8_t)available;
}

l2_hs_result_t l2_hs_apply_remote_bulk_grant(
    l2_hs_adapter_t *adapter,
    uint32_t peer_boot_id,
    uint32_t granted_total
)
{
    if (adapter == NULL) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (adapter->state != L2_HS_READY || !adapter->session_valid) {
        return L2_HS_INVALID_STATE;
    }
    if (peer_boot_id != adapter->peer_boot_id) {
        return L2_HS_SESSION_MISMATCH;
    }
    if (adapter->remote_bulk_granted_total == 0 &&
        adapter->remote_bulk_consumed_total == 0 &&
        granted_total != L2_HS_BULK_CREDITS_MAX) {
        enter_fault(adapter);
        return L2_HS_FAULT;
    }
    if (granted_total < adapter->remote_bulk_granted_total ||
        granted_total < adapter->remote_bulk_consumed_total) {
        return L2_HS_STALE;
    }
    const uint32_t available = granted_total - adapter->remote_bulk_consumed_total;
    if (available > L2_HS_BULK_CREDITS_MAX) {
        enter_fault(adapter);
        return L2_HS_FAULT;
    }
    adapter->remote_bulk_granted_total = granted_total;
    return L2_HS_OK;
}

uint8_t l2_hs_remote_bulk_credit(const l2_hs_adapter_t *adapter)
{
    if (adapter == NULL ||
        adapter->remote_bulk_consumed_total > adapter->remote_bulk_granted_total) {
        return 0;
    }
    const uint32_t available = adapter->remote_bulk_granted_total -
        adapter->remote_bulk_consumed_total;
    return available > L2_HS_BULK_CREDITS_MAX ? 0 : (uint8_t)available;
}

static int find_pending(const l2_hs_adapter_t *adapter, uint32_t message_id)
{
    for (size_t index = 0; index < L2_HS_PENDING_MAX; ++index) {
        if (adapter->pending[index].used &&
            adapter->pending[index].message_id == message_id) {
            return (int)index;
        }
    }
    return -1;
}

static int find_cached(const l2_hs_adapter_t *adapter, uint32_t message_id)
{
    for (size_t index = 0; index < L2_HS_RESULT_CACHE_MAX; ++index) {
        if (adapter->cache[index].used &&
            adapter->cache[index].message_id == message_id) {
            return (int)index;
        }
    }
    return -1;
}

l2_hs_result_t l2_hs_receive_request(
    l2_hs_adapter_t *adapter,
    uint32_t peer_boot_id,
    uint32_t message_id,
    bool side_effect,
    uint16_t deadline_ms,
    uint64_t now_ms
)
{
    if (adapter == NULL) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (adapter->state != L2_HS_READY || !adapter->session_valid) {
        return L2_HS_INVALID_STATE;
    }
    if (peer_boot_id != adapter->peer_boot_id) {
        return L2_HS_SESSION_MISMATCH;
    }
    if (find_pending(adapter, message_id) >= 0) {
        return L2_HS_DUPLICATE_PENDING;
    }
    if (find_cached(adapter, message_id) >= 0) {
        return L2_HS_DUPLICATE_CACHED;
    }
    if (adapter->highest_message_id_valid &&
        message_id <= adapter->highest_message_id) {
        return L2_HS_STALE;
    }
    if (side_effect && deadline_ms == 0) {
        return L2_HS_INVALID_ARGUMENT;
    }
    if (side_effect) {
        size_t slot = L2_HS_PENDING_MAX;
        for (size_t index = 0; index < L2_HS_PENDING_MAX; ++index) {
            if (!adapter->pending[index].used) {
                slot = index;
                break;
            }
        }
        if (slot == L2_HS_PENDING_MAX) {
            return L2_HS_BUSY;
        }
        adapter->pending[slot] = (l2_hs_pending_t){
            .used = true,
            .message_id = message_id,
            .deadline_at_ms = now_ms + deadline_ms,
        };
    }
    adapter->highest_message_id = message_id;
    adapter->highest_message_id_valid = true;
    return L2_HS_NEW;
}

l2_hs_result_t l2_hs_request_can_commit(
    const l2_hs_adapter_t *adapter,
    uint32_t message_id,
    uint64_t now_ms
)
{
    if (adapter == NULL) {
        return L2_HS_INVALID_ARGUMENT;
    }
    const int index = find_pending(adapter, message_id);
    if (index < 0) {
        return L2_HS_STALE;
    }
    if (now_ms >= adapter->pending[(size_t)index].deadline_at_ms) {
        return L2_HS_DEADLINE_EXPIRED;
    }
    return L2_HS_OK;
}

l2_hs_result_t l2_hs_finish_request(
    l2_hs_adapter_t *adapter,
    uint32_t message_id,
    int32_t result_code,
    uint32_t owner_state
)
{
    if (adapter == NULL) {
        return L2_HS_INVALID_ARGUMENT;
    }
    const int pending_index = find_pending(adapter, message_id);
    if (pending_index < 0) {
        return L2_HS_STALE;
    }
    size_t cache_index = L2_HS_RESULT_CACHE_MAX;
    uint64_t oldest_order = UINT64_MAX;
    for (size_t index = 0; index < L2_HS_RESULT_CACHE_MAX; ++index) {
        if (!adapter->cache[index].used) {
            cache_index = index;
            break;
        }
        if (adapter->cache[index].order < oldest_order) {
            oldest_order = adapter->cache[index].order;
            cache_index = index;
        }
    }
    adapter->result_order += 1U;
    adapter->cache[cache_index] = (l2_hs_cached_result_t){
        .used = true,
        .message_id = message_id,
        .result_code = result_code,
        .owner_state = owner_state,
        .order = adapter->result_order,
    };
    adapter->pending[(size_t)pending_index] = (l2_hs_pending_t){0};
    return L2_HS_OK;
}

bool l2_hs_cached_result(
    const l2_hs_adapter_t *adapter,
    uint32_t message_id,
    int32_t *result_code,
    uint32_t *owner_state
)
{
    if (adapter == NULL || result_code == NULL || owner_state == NULL) {
        return false;
    }
    const int index = find_cached(adapter, message_id);
    if (index < 0) {
        return false;
    }
    *result_code = adapter->cache[(size_t)index].result_code;
    *owner_state = adapter->cache[(size_t)index].owner_state;
    return true;
}

size_t l2_hs_pending_count(const l2_hs_adapter_t *adapter)
{
    if (adapter == NULL) {
        return 0;
    }
    size_t count = 0;
    for (size_t index = 0; index < L2_HS_PENDING_MAX; ++index) {
        if (adapter->pending[index].used) {
            count += 1U;
        }
    }
    return count;
}
