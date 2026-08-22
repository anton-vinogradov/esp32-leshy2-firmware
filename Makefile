CC ?= cc
CFLAGS ?= -std=c17 -O2 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?= -Icommon/include
HOST_BUILD := build_host
HOST_SAFETY_TEST := $(HOST_BUILD)/test_safety_core
HOST_L2IP_TEST := $(HOST_BUILD)/test_l2ip
HOST_UPDATE_TEST := $(HOST_BUILD)/test_update_core
HOST_SYSTEM_TEST := $(HOST_BUILD)/test_system_model

.PHONY: host-test clean

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
