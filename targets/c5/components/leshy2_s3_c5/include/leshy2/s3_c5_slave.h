#ifndef LESHY2_S3_C5_SLAVE_H
#define LESHY2_S3_C5_SLAVE_H

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
    L2_S3_C5_SLAVE_DMA_BUFFERS = 8,
    L2_S3_C5_INTERRUPT_COUNT = 8,
};

esp_err_t l2_s3_c5_slave_start(void);
void l2_s3_c5_slave_stop(void);
bool l2_s3_c5_slave_started(void);
l2_hs_adapter_t *l2_s3_c5_slave_core(void);
esp_err_t l2_s3_c5_slave_send_cell(
    const uint8_t cell[L2_HS_CELL_BYTES],
    uint32_t wait_ticks
);
esp_err_t l2_s3_c5_slave_receive_cell(
    uint8_t cell[L2_HS_CELL_BYTES],
    size_t *received_bytes,
    uint32_t wait_ticks
);
esp_err_t l2_s3_c5_slave_reclaim_sent(uint32_t wait_ticks);
esp_err_t l2_s3_c5_slave_send_interrupt(uint8_t interrupt);
esp_err_t l2_s3_c5_slave_wait_interrupt(uint8_t interrupt, uint32_t wait_ticks);

#endif
