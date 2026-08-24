PROJECT_ROOT := $(abspath ../..)
BUILD_DIR ?= $(PROJECT_ROOT)/build/targets/pack/debug
CONFIG ?= debug
MSPM0_SDK_PATH ?=
TI_ARM_CLANG_PATH ?=
SYSCONFIG_PATH ?=

CC := $(TI_ARM_CLANG_PATH)/bin/tiarmclang
OBJCOPY := $(TI_ARM_CLANG_PATH)/bin/tiarmobjcopy
SYSCONFIG_CLI := $(SYSCONFIG_PATH)/sysconfig_cli.sh
STARTUP := $(MSPM0_SDK_PATH)/source/ti/devices/msp/m0p/startup_system_files/ticlang/startup_mspm0c1105_c1106_ticlang.c
DRIVERLIB := $(MSPM0_SDK_PATH)/source/ti/driverlib/lib/ticlang/m0p/mspm0c1105_c1106/driverlib.a
COMMON := $(PROJECT_ROOT)/common
GENERATED_HW := $(PROJECT_ROOT)/generated/hardware
SYSCONFIG_STAMP := $(BUILD_DIR)/sysconfig.stamp

ARCH_FLAGS := -D__MSPM0C1106__ -mcpu=cortex-m0plus -march=thumbv6m -mfloat-abi=soft -mthumb
INCLUDE_FLAGS := -I$(BUILD_DIR) -I$(COMMON)/include -I$(GENERATED_HW)/include -I$(MSPM0_SDK_PATH)/source/third_party/CMSIS/Core/Include -I$(MSPM0_SDK_PATH)/source
PROJECT_WARNINGS := -Wall -Wextra -Werror -Wformat=2 -Wshadow -Wundef -Wconversion -Wdouble-promotion -Wmissing-prototypes -Wpedantic -Wstrict-prototypes
PROJECT_CODEGEN := -std=c17 -ffunction-sections -fdata-sections -fstack-usage -ffile-prefix-map=$(PROJECT_ROOT)=. -fdebug-prefix-map=$(PROJECT_ROOT)=.

ifeq ($(CONFIG),debug)
OPT_FLAGS := -Og -gdwarf-3
else ifeq ($(CONFIG),release)
OPT_FLAGS := -Os -g1 -DNDEBUG=1
else
$(error CONFIG must be debug or release)
endif

PROJECT_CFLAGS := $(ARCH_FLAGS) $(INCLUDE_FLAGS) $(PROJECT_WARNINGS) $(PROJECT_CODEGEN) $(OPT_FLAGS)
SDK_CFLAGS := $(ARCH_FLAGS) $(INCLUDE_FLAGS) $(OPT_FLAGS)
LINK_FLAGS := $(ARCH_FLAGS) -Wl,--rom_model -Wl,--warn_sections -Wl,--emit_warnings_as_errors
APP_OUT := $(BUILD_DIR)/leshy2_pack.out
APP_BIN := $(BUILD_DIR)/leshy2_pack.bin
APP_MAP := $(BUILD_DIR)/leshy2_pack.map
BOOT_OUT := $(BUILD_DIR)/leshy2_pack_boot.out
BOOT_BIN := $(BUILD_DIR)/leshy2_pack_boot.bin
BOOT_MAP := $(BUILD_DIR)/leshy2_pack_boot.map
APP_OBJECTS := $(BUILD_DIR)/pack_main.obj $(BUILD_DIR)/safety_core.obj $(BUILD_DIR)/pack_bsp.obj $(BUILD_DIR)/ti_msp_dl_config.obj $(BUILD_DIR)/startup.obj
BOOT_OBJECTS := $(BUILD_DIR)/pack_boot_main.obj $(BUILD_DIR)/startup.obj

.PHONY: all configure clean

all: $(APP_BIN) $(BOOT_BIN)

configure: $(SYSCONFIG_STAMP)

$(BUILD_DIR):
	mkdir -p $@

$(SYSCONFIG_STAMP): pack.syscfg | $(BUILD_DIR)
	$(SYSCONFIG_CLI) --compiler ticlang --product $(MSPM0_SDK_PATH)/.metadata/product.json --output $(BUILD_DIR) $<
	touch $@

$(BUILD_DIR)/pack_main.obj: main.c $(SYSCONFIG_STAMP)
	$(CC) $(PROJECT_CFLAGS) @$(BUILD_DIR)/device.opt -c $< -o $@

$(BUILD_DIR)/safety_core.obj: $(COMMON)/src/safety_core.c $(COMMON)/include/leshy2/safety_core.h | $(BUILD_DIR)
	$(CC) $(PROJECT_CFLAGS) -c $< -o $@

$(BUILD_DIR)/pack_bsp.obj: $(GENERATED_HW)/src/pack_bsp.c $(GENERATED_HW)/include/leshy2/hardware/pack_bsp.h $(GENERATED_HW)/include/leshy2/hardware/bsp_types.h | $(BUILD_DIR)
	$(CC) $(PROJECT_CFLAGS) -c $< -o $@

$(BUILD_DIR)/ti_msp_dl_config.obj: $(SYSCONFIG_STAMP)
	$(CC) $(SDK_CFLAGS) @$(BUILD_DIR)/device.opt -c $(BUILD_DIR)/ti_msp_dl_config.c -o $@

$(BUILD_DIR)/startup.obj: $(STARTUP) | $(BUILD_DIR)
	$(CC) $(SDK_CFLAGS) -c $< -o $@

$(BUILD_DIR)/pack_boot_main.obj: boot_main.c | $(BUILD_DIR)
	$(CC) $(PROJECT_CFLAGS) -c $< -o $@

$(APP_OUT): $(APP_OBJECTS) slot_a.cmd $(DRIVERLIB)
	$(CC) $(LINK_FLAGS) -Wl,-u,_c_int00 -Wl,-m,$(APP_MAP) $(APP_OBJECTS) $(DRIVERLIB) -L$(BUILD_DIR) -ldevice.cmd.genlibs slot_a.cmd -o $@

$(BOOT_OUT): $(BOOT_OBJECTS) boot_manager.cmd $(DRIVERLIB)
	$(CC) $(LINK_FLAGS) -Wl,-u,_c_int00 -Wl,-m,$(BOOT_MAP) $(BOOT_OBJECTS) $(DRIVERLIB) boot_manager.cmd -o $@

$(APP_BIN): $(APP_OUT)
	$(OBJCOPY) -O binary $< $@

$(BOOT_BIN): $(BOOT_OUT)
	$(OBJCOPY) -O binary $< $@

clean:
	$(RM) $(APP_OBJECTS) $(BOOT_OBJECTS) $(APP_OUT) $(APP_BIN) $(APP_MAP) $(BOOT_OUT) $(BOOT_BIN) $(BOOT_MAP) $(SYSCONFIG_STAMP)
