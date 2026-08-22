#ifndef LESHY2_L2IP_H
#define LESHY2_L2IP_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

enum {
    L2IP_HEADER_BYTES = 32,
    L2IP_MAX_PAYLOAD_BYTES = 480,
    L2IP_MAGIC = 0x3248534c,
    L2IP_MAJOR = 1,
    L2IP_MINOR = 0,
};

typedef struct {
    uint8_t major;
    uint8_t minor;
    uint8_t flags;
    uint16_t message_type;
    uint8_t source;
    uint8_t target;
    uint32_t message_id;
    uint32_t correlation_id;
    uint16_t payload_bytes;
    uint16_t deadline_ms;
    uint32_t payload_crc32c;
    uint32_t header_crc32c;
} l2ip_header_t;

typedef enum {
    L2IP_DECODE_OK = 0,
    L2IP_DECODE_SIZE,
    L2IP_DECODE_MAGIC,
    L2IP_DECODE_VERSION,
    L2IP_DECODE_FLAGS,
    L2IP_DECODE_MESSAGE,
    L2IP_DECODE_DEADLINE,
    L2IP_DECODE_PAYLOAD_CRC,
    L2IP_DECODE_HEADER_CRC,
} l2ip_decode_result_t;

typedef enum {
    L2IP_REQUEST_NEW = 0,
    L2IP_REQUEST_DUPLICATE,
    L2IP_REQUEST_STALE,
} l2ip_request_result_t;

typedef struct {
    uint32_t boot_id;
    uint32_t highest_message_id;
    bool initialized;
} l2ip_replay_guard_t;

uint32_t l2_crc32c(const uint8_t *data, size_t bytes);
bool l2ip_message_has_side_effect(uint16_t message_type);
bool l2ip_encode(
    uint8_t output[L2IP_HEADER_BYTES],
    l2ip_header_t *header,
    const uint8_t *payload
);
l2ip_decode_result_t l2ip_decode(
    l2ip_header_t *header,
    const uint8_t input[L2IP_HEADER_BYTES],
    const uint8_t *payload,
    size_t payload_bytes
);
void l2ip_replay_guard_reset(l2ip_replay_guard_t *guard, uint32_t boot_id);
l2ip_request_result_t l2ip_replay_guard_accept(
    l2ip_replay_guard_t *guard,
    uint32_t boot_id,
    uint32_t message_id
);

#endif
