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

.PHONY: test host-test matrix-check targets-list target-preflight target-configure target-build target-verify target-artifacts target-clean clean

test: host-test matrix-check
	python3 -m unittest discover -s tests

matrix-check:
	python3 tools/build_targets.py verify-matrix

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
