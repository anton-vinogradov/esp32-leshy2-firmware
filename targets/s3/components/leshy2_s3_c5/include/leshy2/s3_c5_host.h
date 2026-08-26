#ifndef LESHY2_S3_C5_HOST_H
#define LESHY2_S3_C5_HOST_H

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpedantic"
#pragma GCC diagnostic ignored "-Wundef"
#include "esp_err.h"
#pragma GCC diagnostic pop
#include "leshy2/high_speed_adapter.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

enum {
    L2_S3_C5_SDIO_BUS_WIDTH = 1,
    L2_S3_C5_SDIO_FREQUENCY_KHZ = 20000,
    L2_S3_C5_INTERRUPT_COUNT = 8,
};

esp_err_t l2_s3_c5_host_start(uint32_t wait_ms);
void l2_s3_c5_host_stop(void);
bool l2_s3_c5_host_started(void);
l2_hs_adapter_t *l2_s3_c5_host_core(void);
esp_err_t l2_s3_c5_host_send_cell(
    const uint8_t cell[L2_HS_CELL_BYTES],
    uint32_t wait_ms
);
esp_err_t l2_s3_c5_host_receive_cell(
    uint8_t cell[L2_HS_CELL_BYTES],
    size_t *received_bytes,
    uint32_t wait_ms
);
esp_err_t l2_s3_c5_host_wait_interrupt(uint32_t wait_ms);
esp_err_t l2_s3_c5_host_read_interrupts(
    uint32_t *raw,
    uint32_t *masked,
    uint32_t wait_ms
);
esp_err_t l2_s3_c5_host_clear_interrupts(uint32_t mask, uint32_t wait_ms);
esp_err_t l2_s3_c5_host_send_interrupt(uint8_t interrupt, uint32_t wait_ms);

#endif
