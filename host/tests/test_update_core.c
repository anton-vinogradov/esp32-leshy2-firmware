#include "leshy2/update_core.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void stage_complete_bundle(l2_update_t *state, uint32_t build)
{
    for (int domain = 0; domain < L2_UPDATE_DOMAIN_COUNT; ++domain) {
        assert(l2_update_stage(state, (l2_update_domain_t)domain, build, true));
    }
    assert(l2_update_verify_bundle(state));
}

static void test_preconditions_are_fail_closed(void)
{
    l2_update_t state;
    l2_update_init(&state, 10);
    assert(!l2_update_begin(&state, false, true, true, true, 0));
    assert(state.first_fault == L2_UPDATE_FAULT_PRECONDITION);
    assert(!l2_update_begin(&state, true, false, true, true, 0));
}

static void test_s3_is_activated_last_and_commit_succeeds(void)
{
    l2_update_t state;
    l2_update_init(&state, 10);
    assert(l2_update_begin(&state, true, true, true, true, 100));
    stage_complete_bundle(&state, 11);
    for (int domain = 0; domain < L2_UPDATE_DOMAIN_COUNT; ++domain) {
        assert(l2_update_activate(&state, (l2_update_domain_t)domain, 200 + (uint32_t)domain));
        assert(l2_update_report_self_test(&state, (l2_update_domain_t)domain, true));
    }
    assert(l2_update_commit(&state, 300));
    assert(state.phase == L2_UPDATE_COMMITTED);
    for (int domain = 0; domain < L2_UPDATE_DOMAIN_COUNT; ++domain) {
        assert(state.active_build[domain] == 11);
    }
}

static void test_wrong_order_rolls_every_domain_back(void)
{
    l2_update_t state;
    l2_update_init(&state, 20);
    assert(l2_update_begin(&state, true, true, true, true, 0));
    stage_complete_bundle(&state, 21);
    assert(!l2_update_activate(&state, L2_UPDATE_S3, 1));
    assert(state.phase == L2_UPDATE_ROLLED_BACK);
    assert(state.first_fault == L2_UPDATE_FAULT_ACTIVATION_ORDER);
    for (int domain = 0; domain < L2_UPDATE_DOMAIN_COUNT; ++domain) {
        assert(state.active_build[domain] == 20);
    }
}

static void test_mid_bundle_self_test_and_deadline_restore_previous_bundle(void)
{
    l2_update_t state;
    l2_update_init(&state, 30);
    assert(l2_update_begin(&state, true, true, true, true, 0));
    stage_complete_bundle(&state, 31);
    assert(l2_update_activate(&state, L2_UPDATE_PACK, 1));
    assert(l2_update_report_self_test(&state, L2_UPDATE_PACK, true));
    assert(l2_update_activate(&state, L2_UPDATE_SAFETY, 2));
    assert(!l2_update_report_self_test(&state, L2_UPDATE_SAFETY, false));
    assert(strcmp(l2_update_fault_text(state.first_fault),
                  "Target self-test failed; previous bundle restored") == 0);
    assert(state.active_build[L2_UPDATE_PACK] == 30);

    assert(l2_update_begin(&state, true, true, true, true, 100));
    stage_complete_bundle(&state, 32);
    l2_update_check_deadline(&state, 12101);
    assert(state.phase == L2_UPDATE_ROLLED_BACK);
    assert(state.first_fault == L2_UPDATE_FAULT_DEADLINE);
}

int main(void)
{
    test_preconditions_are_fail_closed();
    test_s3_is_activated_last_and_commit_succeeds();
    test_wrong_order_rolls_every_domain_back();
    test_mid_bundle_self_test_and_deadline_restore_previous_bundle();
    puts("host update core: 4 scenarios passed");
    return 0;
}
