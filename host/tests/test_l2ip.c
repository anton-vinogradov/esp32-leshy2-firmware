#include "leshy2/l2ip.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void test_crc32c_standard_vector(void)
{
    static const uint8_t input[] = "123456789";
    assert(l2_crc32c(input, 9) == UINT32_C(0xe3069283));
}

static void test_header_round_trip_and_corruption(void)
{
    uint8_t encoded[L2IP_HEADER_BYTES];
    uint8_t payload[] = {0x4c, 0x32, 0x49, 0x50};
    l2ip_header_t source = {
        .major = 1,
        .minor = 0,
        .flags = 1,
        .message_type = 9,
        .source = 1,
        .target = 3,
        .message_id = 0x01020304,
        .correlation_id = 0,
        .payload_bytes = sizeof(payload),
        .deadline_ms = 25,
    };
    assert(l2ip_encode(encoded, &source, payload));
    assert(encoded[0] == 'L' && encoded[1] == 'S' && encoded[2] == 'H' && encoded[3] == '2');

    l2ip_header_t decoded;
    assert(l2ip_decode(&decoded, encoded, payload, sizeof(payload)) == L2IP_DECODE_OK);
    assert(decoded.message_id == source.message_id);
    assert(decoded.payload_crc32c == source.payload_crc32c);
    assert(decoded.header_crc32c == source.header_crc32c);

    payload[0] ^= 1;
    assert(l2ip_decode(&decoded, encoded, payload, sizeof(payload)) == L2IP_DECODE_PAYLOAD_CRC);
    payload[0] ^= 1;
    encoded[12] ^= 1;
    assert(l2ip_decode(&decoded, encoded, payload, sizeof(payload)) == L2IP_DECODE_HEADER_CRC);
}

static void test_reserved_flags_and_deadline_fail_closed(void)
{
    uint8_t encoded[L2IP_HEADER_BYTES];
    l2ip_header_t header = {
        .major = 1, .minor = 0, .flags = 0x20, .message_type = 3,
        .source = 1, .target = 2, .message_id = 1, .payload_bytes = 0,
    };
    assert(!l2ip_encode(encoded, &header, NULL));
    header.flags = 0;
    header.message_type = 13;
    assert(!l2ip_encode(encoded, &header, NULL));
    header.deadline_ms = 1;
    assert(l2ip_encode(encoded, &header, NULL));
}

static void test_duplicate_never_becomes_new_side_effect(void)
{
    l2ip_replay_guard_t guard;
    l2ip_replay_guard_reset(&guard, 10);
    assert(l2ip_replay_guard_accept(&guard, 10, 7) == L2IP_REQUEST_NEW);
    assert(l2ip_replay_guard_accept(&guard, 10, 7) == L2IP_REQUEST_DUPLICATE);
    assert(l2ip_replay_guard_accept(&guard, 10, 6) == L2IP_REQUEST_STALE);
    assert(l2ip_replay_guard_accept(&guard, 10, 8) == L2IP_REQUEST_NEW);
    assert(l2ip_replay_guard_accept(&guard, 11, 1) == L2IP_REQUEST_NEW);
}

int main(void)
{
    test_crc32c_standard_vector();
    test_header_round_trip_and_corruption();
    test_reserved_flags_and_deadline_fail_closed();
    test_duplicate_never_becomes_new_side_effect();
    puts("host L2IP core: 4 scenarios passed");
    return 0;
}
