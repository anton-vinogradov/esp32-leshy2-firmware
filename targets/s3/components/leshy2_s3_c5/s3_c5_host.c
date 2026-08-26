#include "leshy2/s3_c5_host.h"

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpedantic"
#pragma GCC diagnostic ignored "-Wundef"
#include "driver/sdmmc_host.h"
#include "esp_serial_slave_link/essl.h"
#include "esp_serial_slave_link/essl_sdio.h"
#include "sdmmc_cmd.h"
#pragma GCC diagnostic pop

#include "leshy2/hardware/s3_bsp.h"

#include <stdlib.h>
#include <string.h>

_Static_assert(L2_HW_S3_S3_C5_SDIO_CLK == 10, "generated S3 SDIO CLK changed");
_Static_assert(L2_HW_S3_S3_C5_SDIO_CMD == 11, "generated S3 SDIO CMD changed");
_Static_assert(L2_HW_S3_S3_C5_SDIO_D0 == 12, "generated S3 SDIO D0 changed");
_Static_assert(L2_HW_S3_S3_C5_SDIO_D1_IRQ == 13, "generated S3 SDIO D1 changed");
_Static_assert(L2_S3_C5_SDIO_BUS_WIDTH == 1, "C5 native USB requires 1-bit SDIO");
_Static_assert(L2_HS_CELL_BYTES == 512, "ESSL and L2 high-speed cell size changed");

typedef struct {
    l2_hs_adapter_t core;
    sdmmc_card_t card;
    essl_handle_t link;
    bool host_initialized;
    bool started;
} l2_s3_c5_host_context_t;

static l2_s3_c5_host_context_t host_context;

static void release_host_resources(void)
{
    if (host_context.link != NULL) {
        (void)essl_sdio_deinit_dev(host_context.link);
        host_context.link = NULL;
    }
    if (host_context.card.host.dma_aligned_buffer != NULL) {
        free(host_context.card.host.dma_aligned_buffer);
        host_context.card.host.dma_aligned_buffer = NULL;
    }
    if (host_context.host_initialized) {
        (void)sdmmc_host_deinit();
        host_context.host_initialized = false;
    }
    host_context.started = false;
}

static esp_err_t fail_start(esp_err_t error)
{
    release_host_resources();
    l2_hs_transport_fault(&host_context.core);
    return error;
}

esp_err_t l2_s3_c5_host_start(uint32_t wait_ms)
{
    if (host_context.started) {
        return ESP_ERR_INVALID_STATE;
    }

    memset(&host_context, 0, sizeof(host_context));
    l2_hs_init(&host_context.core);
    if (l2_hs_transition(&host_context.core, L2_HS_STARTING) != L2_HS_OK) {
        return ESP_FAIL;
    }

    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    host.flags = SDMMC_HOST_FLAG_1BIT |
        SDMMC_HOST_FLAG_ALLOC_ALIGNED_BUF |
        SDMMC_HOST_FLAG_DEINIT_ARG;
    host.slot = SDMMC_HOST_SLOT_1;
    host.max_freq_khz = L2_S3_C5_SDIO_FREQUENCY_KHZ;

    sdmmc_slot_config_t slot = SDMMC_SLOT_CONFIG_DEFAULT();
    slot.width = L2_S3_C5_SDIO_BUS_WIDTH;
    slot.flags = 0;
    slot.clk = L2_HW_S3_S3_C5_SDIO_CLK;
    slot.cmd = L2_HW_S3_S3_C5_SDIO_CMD;
    slot.d0 = L2_HW_S3_S3_C5_SDIO_D0;
    slot.d1 = L2_HW_S3_S3_C5_SDIO_D1_IRQ;
    slot.d2 = GPIO_NUM_NC;
    slot.d3 = GPIO_NUM_NC;
    slot.d4 = GPIO_NUM_NC;
    slot.d5 = GPIO_NUM_NC;
    slot.d6 = GPIO_NUM_NC;
    slot.d7 = GPIO_NUM_NC;

    esp_err_t result = sdmmc_host_init();
    if (result != ESP_OK) {
        return fail_start(result);
    }
    host_context.host_initialized = true;

    result = sdmmc_host_init_slot(SDMMC_HOST_SLOT_1, &slot);
    if (result != ESP_OK) {
        return fail_start(result);
    }
    result = sdmmc_card_init(&host, &host_context.card);
    if (result != ESP_OK) {
        return fail_start(result);
    }

    const essl_sdio_config_t link_config = {
        .card = &host_context.card,
        .recv_buffer_size = L2_HS_CELL_BYTES,
    };
    result = essl_sdio_init_dev(&host_context.link, &link_config);
    if (result != ESP_OK) {
        return fail_start(result);
    }
    result = essl_init(host_context.link, wait_ms);
    if (result != ESP_OK) {
        return fail_start(result);
    }
    if (l2_hs_transition(&host_context.core, L2_HS_NEGOTIATING) != L2_HS_OK) {
        return fail_start(ESP_FAIL);
    }
    host_context.started = true;
    return ESP_OK;
}

void l2_s3_c5_host_stop(void)
{
    release_host_resources();
    l2_hs_init(&host_context.core);
}

bool l2_s3_c5_host_started(void)
{
    return host_context.started;
}

l2_hs_adapter_t *l2_s3_c5_host_core(void)
{
    return &host_context.core;
}

esp_err_t l2_s3_c5_host_send_cell(
    const uint8_t cell[L2_HS_CELL_BYTES],
    uint32_t wait_ms
)
{
    if (!host_context.started) {
        return ESP_ERR_INVALID_STATE;
    }
    if (cell == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    return essl_send_packet(host_context.link, cell, L2_HS_CELL_BYTES, wait_ms);
}

esp_err_t l2_s3_c5_host_receive_cell(
    uint8_t cell[L2_HS_CELL_BYTES],
    size_t *received_bytes,
    uint32_t wait_ms
)
{
    if (!host_context.started) {
        return ESP_ERR_INVALID_STATE;
    }
    if (cell == NULL || received_bytes == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    *received_bytes = 0;
    const esp_err_t result = essl_get_packet(
        host_context.link,
        cell,
        L2_HS_CELL_BYTES,
        received_bytes,
        wait_ms
    );
    if (result == ESP_OK && *received_bytes != L2_HS_CELL_BYTES) {
        return ESP_ERR_INVALID_SIZE;
    }
    return result;
}

esp_err_t l2_s3_c5_host_wait_interrupt(uint32_t wait_ms)
{
    if (!host_context.started) {
        return ESP_ERR_INVALID_STATE;
    }
    return essl_wait_int(host_context.link, wait_ms);
}

esp_err_t l2_s3_c5_host_read_interrupts(
    uint32_t *raw,
    uint32_t *masked,
    uint32_t wait_ms
)
{
    if (!host_context.started) {
        return ESP_ERR_INVALID_STATE;
    }
    if (raw == NULL && masked == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    return essl_get_intr(host_context.link, raw, masked, wait_ms);
}

esp_err_t l2_s3_c5_host_clear_interrupts(uint32_t mask, uint32_t wait_ms)
{
    if (!host_context.started) {
        return ESP_ERR_INVALID_STATE;
    }
    return essl_clear_intr(host_context.link, mask, wait_ms);
}

esp_err_t l2_s3_c5_host_send_interrupt(uint8_t interrupt, uint32_t wait_ms)
{
    if (!host_context.started || interrupt >= L2_S3_C5_INTERRUPT_COUNT) {
        return ESP_ERR_INVALID_ARG;
    }
    return essl_send_slave_intr(host_context.link, UINT32_C(1) << interrupt, wait_ms);
}
