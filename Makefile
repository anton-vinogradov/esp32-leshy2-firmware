CC ?= cc
CFLAGS ?= -std=c17 -O2 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?= -Icommon/include
HOST_BUILD := build_host
HOST_SAFETY_TEST := $(HOST_BUILD)/test_safety_core
HOST_L2IP_TEST := $(HOST_BUILD)/test_l2ip
HOST_HS_TEST := $(HOST_BUILD)/test_high_speed_adapter
HOST_UPDATE_TEST := $(HOST_BUILD)/test_update_core
HOST_SYSTEM_TEST := $(HOST_BUILD)/test_system_model
TARGET ?= all
CONFIG ?= debug
TARGET_PYTHON ?= python3.12
LOCKED_PYTHON ?= .toolchains/python/idf6_py3.12_env/bin/python

.PHONY: test f0-r2-review host-test host-sanitize matrix-check source-layout-check build-policy-check f2-1-review f2-2-review f2-3-review f2-4-preflight-review f2-4-build-review f2-5-reproducibility-review f3-0-capability-review f3-0-runtime-plan-review f3-0-acceptance-plan-review f3-1-runtime-review f3-2-runtime-review f3-3-boundary-review f3-4-closure-review f4-0-capability-review f4-0-adapter-review f4-0-acceptance-review f4-1-source-review f4-1-core-review f4-1-endpoint-review f4-1-qemu-review f3-s3-run f3-s3-evidence-check f3-s3-scenario-run f3-s3-scenario-check capture-target-build locked-target-configure locked-target-build locked-target-clean locked-target-verify bsp-input-check bsp-generate bsp-check bsp-target-check target-projects-check targets-list target-preflight target-configure target-build target-verify target-artifacts target-clean clean

test: f2-3-review f2-4-build-review f2-5-reproducibility-review f3-0-capability-review f3-0-runtime-plan-review f3-0-acceptance-plan-review f3-1-runtime-review f3-2-runtime-review f3-3-boundary-review f3-4-closure-review f4-0-capability-review f4-0-adapter-review f4-0-acceptance-review f4-1-source-review f4-1-core-review f4-1-endpoint-review f4-1-qemu-review
	python3 -m unittest discover -s tests

f0-r2-review:
	python3 tools/review_f0_r2.py

matrix-check:
	python3 tools/build_targets.py verify-matrix

source-layout-check:
	python3 tools/check_source_layout.py

build-policy-check:
	python3 tools/check_build_policy.py

f2-1-review:
	python3 tools/review_f2_1.py

f2-2-review:
	python3 tools/review_f2_2.py

f2-3-review:
	python3 tools/review_f2_3.py

f2-4-preflight-review:
	$(LOCKED_PYTHON) tools/review_f2_4_preflight.py --check

f2-4-build-review:
	python3 tools/review_f2_4_builds.py --check

f2-5-reproducibility-review:
	$(LOCKED_PYTHON) tools/review_f2_5_reproducibility.py --check

f3-0-capability-review:
	python3 tools/check_f3_execution_capability.py

f3-0-runtime-plan-review:
	python3 tools/check_f3_runtime_plan.py

f3-0-acceptance-plan-review:
	python3 tools/run_f3_acceptance.py --check-plan

f3-1-runtime-review:
	python3 tools/run_f3_acceptance.py --check-s3-evidence --config debug
	python3 tools/run_f3_acceptance.py --check-s3-evidence --config release

f3-2-runtime-review:
	python3 tools/run_f3_acceptance.py --check-f3-2-review

f3-3-boundary-review:
	python3 tools/review_f3_3_boundaries.py --check

f3-4-closure-review:
	python3 tools/review_f3_4_closure.py --check

f4-0-capability-review:
	python3 tools/check_f4_transport_capability.py

f4-0-adapter-review:
	python3 tools/check_f4_adapter_contract.py

f4-0-acceptance-review:
	python3 tools/run_f4_acceptance.py --check-plan
	python3 tools/run_f4_acceptance.py --check-snapshot

f4-1-source-review:
	python3 tools/check_f4_1_source_boundary.py

f4-1-core-review:
	python3 tools/review_f4_1_core.py --check
	python3 tools/run_f4_acceptance.py --check-evidence

f4-1-endpoint-review:
	python3 tools/review_f4_1_endpoints.py --check

f4-1-qemu-review:
	python3 tools/review_f4_1_qemu.py --check

f3-s3-run:
	$(LOCKED_PYTHON) tools/run_f3_acceptance.py --run-s3 --config $(CONFIG) --write

f3-s3-evidence-check:
	python3 tools/run_f3_acceptance.py --check-s3-evidence --config $(CONFIG)

f3-s3-scenario-run:
	$(LOCKED_PYTHON) tools/run_f3_acceptance.py --run-s3-f3-2 --config $(CONFIG) --write

f3-s3-scenario-check:
	python3 tools/run_f3_acceptance.py --check-f3-2-evidence --config $(CONFIG)

capture-target-build:
	$(LOCKED_PYTHON) tools/capture_target_build_review.py --target $(TARGET) --write

locked-target-configure:
	$(LOCKED_PYTHON) tools/run_locked_target.py configure --target $(TARGET) --config $(CONFIG)

locked-target-build:
	$(LOCKED_PYTHON) tools/run_locked_target.py build --target $(TARGET) --config $(CONFIG)

locked-target-clean:
	$(LOCKED_PYTHON) tools/run_locked_target.py clean --target $(TARGET) --config $(CONFIG)

locked-target-verify:
	$(LOCKED_PYTHON) tools/run_locked_target.py verify --target $(TARGET) --config $(CONFIG)

bsp-input-check:
	python3 tools/validate_bsp_generation_input.py

bsp-generate:
	python3 tools/generate_hardware_bsp.py --write

bsp-check:
	python3 tools/generate_hardware_bsp.py --check

bsp-target-check:
	python3 tools/check_bsp_target_consumption.py

target-projects-check:
	python3 tools/check_target_projects.py

targets-list:
	python3 tools/build_targets.py list

target-preflight:
	$(TARGET_PYTHON) tools/build_targets.py preflight --target $(TARGET) --config $(CONFIG)

target-configure:
	$(TARGET_PYTHON) tools/build_targets.py configure --target $(TARGET) --config $(CONFIG)

target-build:
	$(TARGET_PYTHON) tools/build_targets.py build --target $(TARGET) --config $(CONFIG)

target-verify:
	$(TARGET_PYTHON) tools/build_targets.py verify --target $(TARGET) --config $(CONFIG)

target-artifacts:
	$(TARGET_PYTHON) tools/build_targets.py artifacts --target $(TARGET) --config $(CONFIG)

target-clean:
	$(TARGET_PYTHON) tools/build_targets.py clean --target $(TARGET) --config $(CONFIG)

host-test: $(HOST_SAFETY_TEST) $(HOST_L2IP_TEST) $(HOST_HS_TEST) $(HOST_UPDATE_TEST) $(HOST_SYSTEM_TEST)
	./$(HOST_SAFETY_TEST)
	./$(HOST_L2IP_TEST)
	./$(HOST_HS_TEST)
	./$(HOST_UPDATE_TEST)
	./$(HOST_SYSTEM_TEST)

host-sanitize:
	$(MAKE) HOST_BUILD=build_host_sanitized CFLAGS="-std=c17 -O1 -g -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -fno-omit-frame-pointer" host-test

$(HOST_SAFETY_TEST): common/src/safety_core.c host/tests/test_safety_core.c common/include/leshy2/safety_core.h
	mkdir -p $(HOST_BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) common/src/safety_core.c host/tests/test_safety_core.c -o $@

$(HOST_L2IP_TEST): common/src/l2ip.c host/tests/test_l2ip.c common/include/leshy2/l2ip.h
	mkdir -p $(HOST_BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) common/src/l2ip.c host/tests/test_l2ip.c -o $@

$(HOST_HS_TEST): common/src/high_speed_adapter.c host/tests/test_high_speed_adapter.c common/include/leshy2/high_speed_adapter.h
	mkdir -p $(HOST_BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) common/src/high_speed_adapter.c host/tests/test_high_speed_adapter.c -o $@

$(HOST_UPDATE_TEST): common/src/update_core.c host/tests/test_update_core.c common/include/leshy2/update_core.h
	mkdir -p $(HOST_BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) common/src/update_core.c host/tests/test_update_core.c -o $@

$(HOST_SYSTEM_TEST): common/src/system_model.c common/src/safety_core.c common/src/update_core.c host/tests/test_system_model.c common/include/leshy2/system_model.h common/include/leshy2/safety_core.h common/include/leshy2/update_core.h
	mkdir -p $(HOST_BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) common/src/system_model.c common/src/safety_core.c common/src/update_core.c host/tests/test_system_model.c -o $@

clean:
	rm -f $(HOST_SAFETY_TEST) $(HOST_L2IP_TEST) $(HOST_UPDATE_TEST) $(HOST_SYSTEM_TEST)
