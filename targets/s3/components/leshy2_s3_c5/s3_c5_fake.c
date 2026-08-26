#include "leshy2/s3_c5_fake.h"

#include "leshy2/high_speed_adapter.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

enum {
    L2_FAKE_S3_BOOT_ID = 0x53,
    L2_FAKE_C5_BOOT_ID = 0xC5,
};

typedef struct {
    l2_hs_adapter_t s3;
    l2_hs_adapter_t c5;
    uint8_t cell[L2_HS_CELL_BYTES];
    size_t cell_bytes;
} l2_s3_c5_fake_wire_t;

static l2_s3_c5_fake_wire_t fake_wire;

static bool start_pair(void)
{
    l2_hs_init(&fake_wire.s3);
    l2_hs_init(&fake_wire.c5);
    memset(fake_wire.cell, 0, sizeof(fake_wire.cell));
    fake_wire.cell_bytes = 0;
    return
        l2_hs_transition(&fake_wire.s3, L2_HS_STARTING) == L2_HS_OK &&
        l2_hs_transition(&fake_wire.s3, L2_HS_NEGOTIATING) == L2_HS_OK &&
        l2_hs_transition(&fake_wire.c5, L2_HS_STARTING) == L2_HS_OK &&
        l2_hs_transition(&fake_wire.c5, L2_HS_NEGOTIATING) == L2_HS_OK &&
        l2_hs_accept_handshake(
            &fake_wire.s3,
            L2_FAKE_S3_BOOT_ID,
            L2_FAKE_C5_BOOT_ID,
            true,
            true,
            UINT64_C(100)
        ) == L2_HS_OK &&
        l2_hs_accept_handshake(
            &fake_wire.c5,
            L2_FAKE_C5_BOOT_ID,
            L2_FAKE_S3_BOOT_ID,
            true,
            true,
            UINT64_C(100)
        ) == L2_HS_OK;
}

static bool transfer_s3_to_c5(
    l2_hs_priority_t priority,
    uint32_t message_id,
    size_t cell_bytes
)
{
    uint8_t tx_handle = L2_HS_INVALID_HANDLE;
    uint8_t selected = L2_HS_INVALID_HANDLE;
    if (l2_hs_tx_acquire(&fake_wire.s3, priority, &tx_handle) != L2_HS_OK ||
        l2_hs_tx_enqueue(
            &fake_wire.s3,
            tx_handle,
            message_id,
            false,
            UINT64_C(0),
            UINT64_C(100)
        ) != L2_HS_OK ||
        l2_hs_tx_take_next(&fake_wire.s3, UINT64_C(100), &selected) != L2_HS_OK ||
        selected != tx_handle) {
        return false;
    }

    memset(fake_wire.cell, 0, sizeof(fake_wire.cell));
    fake_wire.cell[0] = (uint8_t)priority;
    memcpy(&fake_wire.cell[1], &message_id, sizeof(message_id));
    fake_wire.cell_bytes = cell_bytes;
    if (fake_wire.cell_bytes != L2_HS_CELL_BYTES) {
        l2_hs_transport_fault(&fake_wire.s3);
        l2_hs_transport_fault(&fake_wire.c5);
        return false;
    }

    uint8_t rx_handle = L2_HS_INVALID_HANDLE;
    uint32_t received_message_id = 0;
    memcpy(&received_message_id, &fake_wire.cell[1], sizeof(received_message_id));
    if (fake_wire.cell[0] != (uint8_t)priority ||
        received_message_id != message_id ||
        l2_hs_rx_phy_begin(&fake_wire.c5, priority, &rx_handle) != L2_HS_OK ||
        l2_hs_rx_finish_phy(&fake_wire.c5, rx_handle) != L2_HS_OK ||
        l2_hs_rx_dispatch(&fake_wire.c5, rx_handle) != L2_HS_OK ||
        l2_hs_rx_release(&fake_wire.c5, rx_handle) != L2_HS_OK ||
        l2_hs_tx_complete(&fake_wire.s3, tx_handle) != L2_HS_OK) {
        l2_hs_transport_fault(&fake_wire.s3);
        l2_hs_transport_fault(&fake_wire.c5);
        return false;
    }
    return true;
}

static bool review_handshake_and_full_cell(void)
{
    return start_pair() &&
        l2_hs_side_effects_open(&fake_wire.s3) &&
        l2_hs_side_effects_open(&fake_wire.c5) &&
        transfer_s3_to_c5(L2_HS_PRIORITY_CONTROL, UINT32_C(1), L2_HS_CELL_BYTES) &&
        fake_wire.s3.state == L2_HS_READY &&
        fake_wire.c5.state == L2_HS_READY;
}

static bool review_partial_cell_fault(void)
{
    if (!start_pair() ||
        transfer_s3_to_c5(
            L2_HS_PRIORITY_CONTROL,
            UINT32_C(2),
            L2_HS_CELL_BYTES - 1U
        )) {
        return false;
    }
    return fake_wire.s3.state == L2_HS_FAULTED &&
        fake_wire.c5.state == L2_HS_FAULTED &&
        !l2_hs_side_effects_open(&fake_wire.s3) &&
        !l2_hs_side_effects_open(&fake_wire.c5);
}

static bool review_slave_reset_fault(void)
{
    return start_pair() &&
        l2_hs_observe_peer_boot(&fake_wire.s3, L2_FAKE_C5_BOOT_ID + 1U) ==
            L2_HS_SESSION_MISMATCH &&
        fake_wire.s3.state == L2_HS_RESETTING &&
        !l2_hs_side_effects_open(&fake_wire.s3);
}

static bool review_interrupt_loss_fault(void)
{
    return start_pair() &&
        l2_hs_tick(&fake_wire.s3, UINT64_C(300)) == L2_HS_OK &&
        l2_hs_tick(&fake_wire.s3, UINT64_C(301)) == L2_HS_FAULT &&
        fake_wire.s3.state == L2_HS_FAULTED &&
        !l2_hs_side_effects_open(&fake_wire.s3);
}

static bool review_priority_under_bulk(void)
{
    if (!start_pair() ||
        l2_hs_apply_remote_bulk_grant(
            &fake_wire.s3,
            L2_FAKE_C5_BOOT_ID,
            L2_HS_BULK_CREDITS_MAX
        ) != L2_HS_OK) {
        return false;
    }
    for (uint32_t index = 0; index < L2_HS_BULK_CREDITS_MAX; ++index) {
        uint8_t bulk = L2_HS_INVALID_HANDLE;
        if (l2_hs_tx_acquire(&fake_wire.s3, L2_HS_PRIORITY_BULK, &bulk) != L2_HS_OK ||
            l2_hs_tx_enqueue(
                &fake_wire.s3,
                bulk,
                UINT32_C(100) + index,
                false,
                UINT64_C(0),
                UINT64_C(100)
            ) != L2_HS_OK) {
            return false;
        }
    }
    uint8_t control = L2_HS_INVALID_HANDLE;
    uint8_t selected = L2_HS_INVALID_HANDLE;
    return
        l2_hs_tx_acquire(&fake_wire.s3, L2_HS_PRIORITY_CONTROL, &control) == L2_HS_OK &&
        l2_hs_tx_enqueue(
            &fake_wire.s3,
            control,
            UINT32_C(3),
            false,
            UINT64_C(0),
            UINT64_C(100)
        ) == L2_HS_OK &&
        l2_hs_tx_take_next(&fake_wire.s3, UINT64_C(100), &selected) == L2_HS_OK &&
        selected == control &&
        fake_wire.s3.tx[selected].priority == L2_HS_PRIORITY_CONTROL &&
        l2_hs_tx_complete(&fake_wire.s3, selected) == L2_HS_OK;
}

static bool review_link_loss_side_effect_gate(void)
{
    if (!start_pair() || !l2_hs_side_effects_open(&fake_wire.s3)) {
        return false;
    }
    l2_hs_transport_fault(&fake_wire.s3);
    return fake_wire.s3.state == L2_HS_FAULTED &&
        !l2_hs_side_effects_open(&fake_wire.s3);
}

bool l2_s3_c5_fake_run_review(l2_s3_c5_fake_review_t *review)
{
    if (review == NULL) {
        return false;
    }
    *review = (l2_s3_c5_fake_review_t){
        .handshake_and_full_cell = review_handshake_and_full_cell(),
        .partial_cell_fault = review_partial_cell_fault(),
        .slave_reset_fault = review_slave_reset_fault(),
        .interrupt_loss_fault = review_interrupt_loss_fault(),
        .priority_under_bulk = review_priority_under_bulk(),
        .link_loss_side_effect_gate = review_link_loss_side_effect_gate(),
    };
    return review->handshake_and_full_cell &&
        review->partial_cell_fault &&
        review->slave_reset_fault &&
        review->interrupt_loss_fault &&
        review->priority_under_bulk &&
        review->link_loss_side_effect_gate;
}
