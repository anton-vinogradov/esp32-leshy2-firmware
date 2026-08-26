#include "leshy2/s3_c5_slave.h"

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpedantic"
#pragma GCC diagnostic ignored "-Wundef"
#include "driver/sdio_slave.h"
#include "esp_attr.h"
#include "soc/sdio_slave_pins.h"
#pragma GCC diagnostic pop

#include "leshy2/hardware/c5_bsp.h"

#include <string.h>

_Static_assert(SDIO_SLAVE_SLOT0_IOMUX_PIN_NUM_D1 == L2_HW_C5_S3_C5_SDIO_D1_IRQ,
    "generated C5 SDIO D1 does not match the locked SDK");
_Static_assert(SDIO_SLAVE_SLOT0_IOMUX_PIN_NUM_D0 == L2_HW_C5_S3_C5_SDIO_D0,
    "generated C5 SDIO D0 does not match the locked SDK");
_Static_assert(SDIO_SLAVE_SLOT0_IOMUX_PIN_NUM_CLK == L2_HW_C5_S3_C5_SDIO_CLK,
    "generated C5 SDIO CLK does not match the locked SDK");
_Static_assert(SDIO_SLAVE_SLOT0_IOMUX_PIN_NUM_CMD == L2_HW_C5_S3_C5_SDIO_CMD,
    "generated C5 SDIO CMD does not match the locked SDK");
_Static_assert(SDIO_SLAVE_SLOT0_IOMUX_PIN_NUM_D3 == 13,
    "C5 single-line SDIO/USB mux contract changed");
_Static_assert(SDIO_SLAVE_SLOT0_IOMUX_PIN_NUM_D2 == 14,
    "C5 single-line SDIO/USB mux contract changed");
_Static_assert(
    (unsigned)L2_S3_C5_SLAVE_DMA_BUFFERS == (unsigned)L2_HS_BULK_CREDITS_MAX,
    "physical receive ring must cover every initial bulk credit");
_Static_assert(L2_HS_CELL_BYTES == 512, "SDIO and L2 high-speed cell size changed");

typedef struct {
    bool busy;
} l2_s3_c5_send_slot_t;

typedef struct {
    l2_hs_adapter_t core;
    sdio_slave_buf_handle_t receive_handles[L2_S3_C5_SLAVE_DMA_BUFFERS];
    l2_s3_c5_send_slot_t send_slots[L2_S3_C5_SLAVE_DMA_BUFFERS];
    bool driver_initialized;
    bool started;
} l2_s3_c5_slave_context_t;

static l2_s3_c5_slave_context_t slave_context;
static DMA_ATTR uint8_t receive_cells[L2_S3_C5_SLAVE_DMA_BUFFERS][L2_HS_CELL_BYTES];
static DMA_ATTR uint8_t send_cells[L2_S3_C5_SLAVE_DMA_BUFFERS][L2_HS_CELL_BYTES];

static bool send_slot_pointer_valid(const void *pointer)
{
    for (size_t index = 0; index < L2_S3_C5_SLAVE_DMA_BUFFERS; ++index) {
        if (pointer == &slave_context.send_slots[index]) {
            return true;
        }
    }
    return false;
}

static void release_slave_resources(void)
{
    if (slave_context.started) {
        sdio_slave_stop();
        slave_context.started = false;
    }
    if (slave_context.driver_initialized) {
        sdio_slave_deinit();
        slave_context.driver_initialized = false;
    }
    memset(slave_context.receive_handles, 0, sizeof(slave_context.receive_handles));
    memset(slave_context.send_slots, 0, sizeof(slave_context.send_slots));
}

static esp_err_t fail_start(esp_err_t error)
{
    release_slave_resources();
    l2_hs_transport_fault(&slave_context.core);
    return error;
}

esp_err_t l2_s3_c5_slave_start(void)
{
    if (slave_context.started) {
        return ESP_ERR_INVALID_STATE;
    }

    memset(&slave_context, 0, sizeof(slave_context));
    l2_hs_init(&slave_context.core);
    if (l2_hs_transition(&slave_context.core, L2_HS_STARTING) != L2_HS_OK) {
        return ESP_FAIL;
    }

    sdio_slave_config_t config = {
        .timing = SDIO_SLAVE_TIMING_PSEND_NSAMPLE,
        .sending_mode = SDIO_SLAVE_SEND_PACKET,
        .send_queue_size = L2_S3_C5_SLAVE_DMA_BUFFERS,
        .recv_buffer_size = L2_HS_CELL_BYTES,
        .event_cb = NULL,
        .flags = SDIO_SLAVE_FLAG_DAT2_DISABLED | SDIO_SLAVE_FLAG_HIGH_SPEED,
    };
    esp_err_t result = sdio_slave_initialize(&config);
    if (result != ESP_OK) {
        return fail_start(result);
    }
    slave_context.driver_initialized = true;

    for (size_t index = 0; index < L2_S3_C5_SLAVE_DMA_BUFFERS; ++index) {
        const sdio_slave_buf_handle_t handle =
            sdio_slave_recv_register_buf(receive_cells[index]);
        if (handle == NULL) {
            return fail_start(ESP_ERR_NO_MEM);
        }
        slave_context.receive_handles[index] = handle;
        result = sdio_slave_recv_load_buf(handle);
        if (result != ESP_OK) {
            return fail_start(result);
        }
    }

    sdio_slave_set_host_intena(
        SDIO_SLAVE_HOSTINT_SEND_NEW_PACKET |
        SDIO_SLAVE_HOSTINT_BIT0 |
        SDIO_SLAVE_HOSTINT_BIT1 |
        SDIO_SLAVE_HOSTINT_BIT2 |
        SDIO_SLAVE_HOSTINT_BIT3 |
        SDIO_SLAVE_HOSTINT_BIT4 |
        SDIO_SLAVE_HOSTINT_BIT5 |
        SDIO_SLAVE_HOSTINT_BIT6 |
        SDIO_SLAVE_HOSTINT_BIT7
    );
    result = sdio_slave_start();
    if (result != ESP_OK) {
        return fail_start(result);
    }
    slave_context.started = true;
    if (l2_hs_transition(&slave_context.core, L2_HS_NEGOTIATING) != L2_HS_OK) {
        return fail_start(ESP_FAIL);
    }
    return ESP_OK;
}

void l2_s3_c5_slave_stop(void)
{
    release_slave_resources();
    l2_hs_init(&slave_context.core);
}

bool l2_s3_c5_slave_started(void)
{
    return slave_context.started;
}

l2_hs_adapter_t *l2_s3_c5_slave_core(void)
{
    return &slave_context.core;
}

esp_err_t l2_s3_c5_slave_reclaim_sent(uint32_t wait_ticks)
{
    if (!slave_context.started) {
        return ESP_ERR_INVALID_STATE;
    }
    void *completed = NULL;
    const esp_err_t result = sdio_slave_send_get_finished(&completed, wait_ticks);
    if (result != ESP_OK) {
        return result;
    }
    if (!send_slot_pointer_valid(completed)) {
        l2_hs_transport_fault(&slave_context.core);
        return ESP_FAIL;
    }
    ((l2_s3_c5_send_slot_t *)completed)->busy = false;
    return ESP_OK;
}

esp_err_t l2_s3_c5_slave_send_cell(
    const uint8_t cell[L2_HS_CELL_BYTES],
    uint32_t wait_ticks
)
{
    if (!slave_context.started) {
        return ESP_ERR_INVALID_STATE;
    }
    if (cell == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    while (l2_s3_c5_slave_reclaim_sent(0) == ESP_OK) {
    }
    for (size_t index = 0; index < L2_S3_C5_SLAVE_DMA_BUFFERS; ++index) {
        l2_s3_c5_send_slot_t *slot = &slave_context.send_slots[index];
        if (slot->busy) {
            continue;
        }
        memcpy(send_cells[index], cell, L2_HS_CELL_BYTES);
        const esp_err_t result = sdio_slave_send_queue(
            send_cells[index],
            L2_HS_CELL_BYTES,
            slot,
            wait_ticks
        );
        if (result == ESP_OK) {
            slot->busy = true;
        }
        return result;
    }
    return ESP_ERR_TIMEOUT;
}

esp_err_t l2_s3_c5_slave_receive_cell(
    uint8_t cell[L2_HS_CELL_BYTES],
    size_t *received_bytes,
    uint32_t wait_ticks
)
{
    if (!slave_context.started) {
        return ESP_ERR_INVALID_STATE;
    }
    if (cell == NULL || received_bytes == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    *received_bytes = 0;
    sdio_slave_buf_handle_t handle = NULL;
    esp_err_t result = sdio_slave_recv_packet(&handle, wait_ticks);
    if (result != ESP_OK) {
        if (result == ESP_ERR_NOT_FINISHED) {
            if (handle != NULL) {
                (void)sdio_slave_recv_load_buf(handle);
            }
            l2_hs_transport_fault(&slave_context.core);
        }
        return result;
    }

    size_t bytes = 0;
    uint8_t *source = sdio_slave_recv_get_buf(handle, &bytes);
    if (source == NULL || bytes != L2_HS_CELL_BYTES) {
        (void)sdio_slave_recv_load_buf(handle);
        l2_hs_transport_fault(&slave_context.core);
        return ESP_ERR_INVALID_SIZE;
    }
    memcpy(cell, source, bytes);
    *received_bytes = bytes;
    result = sdio_slave_recv_load_buf(handle);
    if (result != ESP_OK) {
        l2_hs_transport_fault(&slave_context.core);
    }
    return result;
}

esp_err_t l2_s3_c5_slave_send_interrupt(uint8_t interrupt)
{
    if (!slave_context.started || interrupt >= L2_S3_C5_INTERRUPT_COUNT) {
        return ESP_ERR_INVALID_ARG;
    }
    return sdio_slave_send_host_int(interrupt);
}

esp_err_t l2_s3_c5_slave_wait_interrupt(uint8_t interrupt, uint32_t wait_ticks)
{
    if (!slave_context.started || interrupt >= L2_S3_C5_INTERRUPT_COUNT) {
        return ESP_ERR_INVALID_ARG;
    }
    return sdio_slave_wait_int(interrupt, wait_ticks);
}
