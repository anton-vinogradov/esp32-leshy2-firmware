#ifndef LESHY2_S3_C5_FAKE_H
#define LESHY2_S3_C5_FAKE_H

#include <stdbool.h>

typedef struct {
    bool handshake_and_full_cell;
    bool partial_cell_fault;
    bool slave_reset_fault;
    bool interrupt_loss_fault;
    bool priority_under_bulk;
    bool link_loss_side_effect_gate;
} l2_s3_c5_fake_review_t;

bool l2_s3_c5_fake_run_review(l2_s3_c5_fake_review_t *review);

#endif
