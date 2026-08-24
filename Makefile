CC ?= cc
CFLAGS ?= -std=c17 -O2 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?= -Icommon/include
HOST_BUILD := build_host
HOST_SAFETY_TEST := $(HOST_BUILD)/test_safety_core
HOST_L2IP_TEST := $(HOST_BUILD)/test_l2ip
HOST_UPDATE_TEST := $(HOST_BUILD)/test_update_core
HOST_SYSTEM_TEST := $(HOST_BUILD)/test_system_model
TARGET ?= all
CONFIG ?= debug
TARGET_PYTHON ?= python3.12
LOCKED_PYTHON ?= .toolchains/python/idf6_py3.12_env/bin/python

.PHONY: test host-test host-sanitize matrix-check source-layout-check build-policy-check f2-1-review f2-2-review f2-3-review f2-4-preflight-review f2-4-build-review capture-target-build locked-target-configure locked-target-build locked-target-verify bsp-input-check bsp-generate bsp-check bsp-target-check target-projects-check targets-list target-preflight target-configure target-build target-verify target-artifacts target-clean clean

test: f2-3-review f2-4-build-review
	python3 -m unittest discover -s tests

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

capture-target-build:
	$(LOCKED_PYTHON) tools/capture_target_build_review.py --target $(TARGET) --write

locked-target-configure:
	$(LOCKED_PYTHON) tools/run_locked_target.py configure --target $(TARGET) --config $(CONFIG)

locked-target-build:
	$(LOCKED_PYTHON) tools/run_locked_target.py build --target $(TARGET) --config $(CONFIG)

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

host-test: $(HOST_SAFETY_TEST) $(HOST_L2IP_TEST) $(HOST_UPDATE_TEST) $(HOST_SYSTEM_TEST)
	./$(HOST_SAFETY_TEST)
	./$(HOST_L2IP_TEST)
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

$(HOST_UPDATE_TEST): common/src/update_core.c host/tests/test_update_core.c common/include/leshy2/update_core.h
	mkdir -p $(HOST_BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) common/src/update_core.c host/tests/test_update_core.c -o $@

$(HOST_SYSTEM_TEST): common/src/system_model.c common/src/safety_core.c common/src/update_core.c host/tests/test_system_model.c common/include/leshy2/system_model.h common/include/leshy2/safety_core.h common/include/leshy2/update_core.h
	mkdir -p $(HOST_BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) common/src/system_model.c common/src/safety_core.c common/src/update_core.c host/tests/test_system_model.c -o $@

clean:
	rm -f $(HOST_SAFETY_TEST) $(HOST_L2IP_TEST) $(HOST_UPDATE_TEST) $(HOST_SYSTEM_TEST)
