#include "leshy2/l2ip.h"

#include <string.h>

static void put_u16(uint8_t *out, uint16_t value)
{
    out[0] = (uint8_t)value;
    out[1] = (uint8_t)(value >> 8);
}

static void put_u32(uint8_t *out, uint32_t value)
{
    out[0] = (uint8_t)value;
    out[1] = (uint8_t)(value >> 8);
    out[2] = (uint8_t)(value >> 16);
    out[3] = (uint8_t)(value >> 24);
}

static uint16_t get_u16(const uint8_t *in)
{
    return (uint16_t)((uint16_t)in[0] | ((uint16_t)in[1] << 8));
}

static uint32_t get_u32(const uint8_t *in)
{
    return (uint32_t)in[0] |
           ((uint32_t)in[1] << 8) |
           ((uint32_t)in[2] << 16) |
           ((uint32_t)in[3] << 24);
}

uint32_t l2_crc32c(const uint8_t *data, size_t bytes)
{
    uint32_t crc = UINT32_C(0xffffffff);
    for (size_t index = 0; index < bytes; ++index) {
        crc ^= data[index];
        for (unsigned bit = 0; bit < 8; ++bit) {
            const uint32_t mask = (uint32_t)-(int32_t)(crc & 1U);
            crc = (crc >> 1) ^ (UINT32_C(0x82f63b78) & mask);
        }
    }
    return ~crc;
}

bool l2ip_message_has_side_effect(uint16_t message_type)
{
    switch (message_type) {
    case 9:  /* STATE_REQUEST */
    case 11: /* QUIET_REQUEST */
    case 13: /* LEASE_SET */
    case 15: /* LEASE_REVOKE */
    case 17: /* STREAM_OPEN */
    case 20: /* STREAM_CLOSE */
    case 23: /* UPDATE_BEGIN */
    case 25: /* UPDATE_CHUNK */
    case 27: /* UPDATE_VERIFY */
    case 29: /* UPDATE_ACTIVATE_PENDING */
    case 31: /* UPDATE_COMMIT */
    case 32: /* UPDATE_ROLLBACK */
        return true;
    default:
        return false;
    }
}

static bool header_values_valid(const l2ip_header_t *header)
{
    if (header->major != L2IP_MAJOR || header->minor > L2IP_MINOR) {
        return false;
    }
    if ((header->flags & UINT8_C(0xe0)) != 0 || header->message_type > 32) {
        return false;
    }
    if (header->payload_bytes > L2IP_MAX_PAYLOAD_BYTES || header->deadline_ms > 60000) {
        return false;
    }
    if (l2ip_message_has_side_effect(header->message_type) && header->deadline_ms == 0) {
        return false;
    }
    return true;
}

bool l2ip_encode(
    uint8_t output[L2IP_HEADER_BYTES],
    l2ip_header_t *header,
    const uint8_t *payload
)
{
    if (!header_values_valid(header) || (header->payload_bytes != 0 && payload == NULL)) {
        return false;
    }
    memset(output, 0, L2IP_HEADER_BYTES);
    put_u32(output + 0, L2IP_MAGIC);
    output[4] = header->major;
    output[5] = header->minor;
    output[6] = L2IP_HEADER_BYTES;
    output[7] = header->flags;
    put_u16(output + 8, header->message_type);
    output[10] = header->source;
    output[11] = header->target;
    put_u32(output + 12, header->message_id);
    put_u32(output + 16, header->correlation_id);
    put_u16(output + 20, header->payload_bytes);
    put_u16(output + 22, header->deadline_ms);
    header->payload_crc32c = l2_crc32c(payload, header->payload_bytes);
    put_u32(output + 24, header->payload_crc32c);
    header->header_crc32c = l2_crc32c(output, 28);
    put_u32(output + 28, header->header_crc32c);
    return true;
}

l2ip_decode_result_t l2ip_decode(
    l2ip_header_t *header,
    const uint8_t input[L2IP_HEADER_BYTES],
    const uint8_t *payload,
    size_t payload_bytes
)
{
    if (input[6] != L2IP_HEADER_BYTES) {
        return L2IP_DECODE_SIZE;
    }
    if (get_u32(input + 0) != L2IP_MAGIC) {
        return L2IP_DECODE_MAGIC;
    }
    if (input[4] != L2IP_MAJOR || input[5] > L2IP_MINOR) {
        return L2IP_DECODE_VERSION;
    }
    if ((input[7] & UINT8_C(0xe0)) != 0) {
        return L2IP_DECODE_FLAGS;
    }
    if (get_u16(input + 8) > 32) {
        return L2IP_DECODE_MESSAGE;
    }
    if (get_u16(input + 20) > L2IP_MAX_PAYLOAD_BYTES ||
        get_u16(input + 20) != payload_bytes || (payload_bytes != 0 && payload == NULL)) {
        return L2IP_DECODE_SIZE;
    }
    if (get_u16(input + 22) > 60000 ||
        (l2ip_message_has_side_effect(get_u16(input + 8)) && get_u16(input + 22) == 0)) {
        return L2IP_DECODE_DEADLINE;
    }
    if (l2_crc32c(payload, payload_bytes) != get_u32(input + 24)) {
        return L2IP_DECODE_PAYLOAD_CRC;
    }
    if (l2_crc32c(input, 28) != get_u32(input + 28)) {
        return L2IP_DECODE_HEADER_CRC;
    }

    *header = (l2ip_header_t){
        .major = input[4],
        .minor = input[5],
        .flags = input[7],
        .message_type = get_u16(input + 8),
        .source = input[10],
        .target = input[11],
        .message_id = get_u32(input + 12),
        .correlation_id = get_u32(input + 16),
        .payload_bytes = get_u16(input + 20),
        .deadline_ms = get_u16(input + 22),
        .payload_crc32c = get_u32(input + 24),
        .header_crc32c = get_u32(input + 28),
    };
    return L2IP_DECODE_OK;
}

void l2ip_replay_guard_reset(l2ip_replay_guard_t *guard, uint32_t boot_id)
{
    *guard = (l2ip_replay_guard_t){
        .boot_id = boot_id,
        .highest_message_id = 0,
        .initialized = false,
    };
}

l2ip_request_result_t l2ip_replay_guard_accept(
    l2ip_replay_guard_t *guard,
    uint32_t boot_id,
    uint32_t message_id
)
{
    if (boot_id != guard->boot_id) {
        l2ip_replay_guard_reset(guard, boot_id);
    }
    if (!guard->initialized) {
        guard->initialized = true;
        guard->highest_message_id = message_id;
        return L2IP_REQUEST_NEW;
    }
    if (message_id == guard->highest_message_id) {
        return L2IP_REQUEST_DUPLICATE;
    }
    if (message_id < guard->highest_message_id) {
        return L2IP_REQUEST_STALE;
    }
    guard->highest_message_id = message_id;
    return L2IP_REQUEST_NEW;
}
