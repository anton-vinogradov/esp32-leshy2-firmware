#!/usr/bin/env python3
"""Validate reviewed target-project structures without claiming SDK execution."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "config" / "target_projects.json"
PIN_RE = re.compile(r"\b(?:GPIO_NUM_|GPIO\d+|PIN_[A-Z0-9_]+)\b")


def check_esp_sdk_warning_boundary(source: str, target: str, errors: list[str]) -> None:
    required = (
        '#pragma GCC diagnostic push',
        '#pragma GCC diagnostic ignored "-Wundef"',
        '#include "esp_chip_info.h"',
        '#include "esp_log.h"',
        '#pragma GCC diagnostic pop',
    )
    offsets = [source.find(token) for token in required]
    if any(offset < 0 for offset in offsets) or offsets != sorted(offsets):
        errors.append(
            f"{target} entry point must isolate upstream ESP-IDF headers from -Wundef"
        )


def main() -> int:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    projects = registry.get("projects", {})
    if set(projects) != {"s3", "c5", "rp", "pack", "safety"}:
        errors.append("target-project registry must contain all five domains")

    s3 = projects.get("s3", {})
    if s3.get("substep") != "F2.2.0" or s3.get("status") != "reviewed_structure":
        errors.append("S3 project structure is not reviewed at F2.2.0")
    if s3.get("sdk_target") != "esp32s3" or s3.get("project_name") != "leshy2_s3":
        errors.append("S3 target or project identity changed")
    for claim in ("pins_consumed", "configure_run", "build_run"):
        if s3.get(claim) is not False:
            errors.append(f"S3 F2.2.0 must keep {claim}=false")

    declared_files = set(s3.get("files", []))
    actual_files = {
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "targets/s3").rglob("*")
        if path.is_file()
    }
    if actual_files != declared_files:
        errors.append(
            f"S3 project file registry mismatch: missing={sorted(declared_files - actual_files)}, "
            f"extra={sorted(actual_files - declared_files)}"
        )

    root_cmake = (REPO_ROOT / "targets/s3/CMakeLists.txt").read_text(encoding="utf-8")
    if "project(leshy2_s3)" not in root_cmake or "IDF_COMPONENT_MANAGER" not in root_cmake:
        errors.append("S3 root project identity/offline policy is incomplete")

    main_cmake = (REPO_ROOT / "targets/s3/main/CMakeLists.txt").read_text(encoding="utf-8")
    portable_cmake = (
        REPO_ROOT / "targets/s3/components/leshy2_portable/CMakeLists.txt"
    ).read_text(encoding="utf-8")
    required_project_flags = {
        "-std=c17",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-Wformat=2",
        "-Wshadow",
        "-Wundef",
        "-ffunction-sections",
        "-fdata-sections",
        "-fstack-usage",
        "-ffile-prefix-map",
        "-fdebug-prefix-map",
    }
    for name, content in (("main", main_cmake), ("portable", portable_cmake)):
        missing = {flag for flag in required_project_flags if flag not in content}
        if missing:
            errors.append(f"S3 {name} component misses flags: {sorted(missing)}")
    for flag in ("-Wconversion", "-Wdouble-promotion", "-Wmissing-prototypes", "-Wpedantic", "-Wstrict-prototypes"):
        if flag not in portable_cmake:
            errors.append(f"S3 portable component misses {flag}")

    app_main = (REPO_ROOT / "targets/s3/main/app_main.c").read_text(encoding="utf-8")
    check_esp_sdk_warning_boundary(app_main, "S3", errors)
    if "l2_system_model_init" not in app_main or "leshy2/system_model.h" not in app_main:
        errors.append("S3 entry point does not consume the portable core")
    if PIN_RE.search(app_main):
        errors.append("S3 entry point contains a temporary pin assignment before F2.3")

    defaults = (REPO_ROOT / "targets/s3/sdkconfig.defaults").read_text(encoding="utf-8")
    for required in (
        "CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y",
        'CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="../../config/partitions_16m.csv"',
        "CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE=y",
        "CONFIG_SPIRAM_MODE_OCT=y",
        "CONFIG_SPIRAM_ECC_ENABLE=y",
    ):
        if required not in defaults:
            errors.append(f"S3 defaults miss {required}")
    debug = (REPO_ROOT / "targets/s3/sdkconfig.debug").read_text(encoding="utf-8")
    release = (REPO_ROOT / "targets/s3/sdkconfig.release").read_text(encoding="utf-8")
    if "CONFIG_COMPILER_OPTIMIZATION_DEBUG=y" not in debug:
        errors.append("S3 debug configuration does not select -Og")
    if "CONFIG_COMPILER_OPTIMIZATION_SIZE=y" not in release:
        errors.append("S3 release configuration does not select -Os")
    if "CONFIG_COMPILER_OPTIMIZATION_ASSERTIONS_DISABLE=y" not in release:
        errors.append("S3 release configuration does not disable assertions")

    c5 = projects.get("c5", {})
    if c5.get("substep") != "F2.2.1" or c5.get("status") != "reviewed_structure":
        errors.append("C5 project structure is not reviewed at F2.2.1")
    if c5.get("sdk_target") != "esp32c5" or c5.get("project_name") != "leshy2_c5":
        errors.append("C5 target or project identity changed")
    for claim in ("pins_consumed", "configure_run", "build_run"):
        if c5.get(claim) is not False:
            errors.append(f"C5 F2.2.1 must keep {claim}=false")

    c5_declared = set(c5.get("files", []))
    c5_actual = {
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "targets/c5").rglob("*")
        if path.is_file()
    }
    if c5_actual != c5_declared:
        errors.append(
            f"C5 project file registry mismatch: missing={sorted(c5_declared - c5_actual)}, "
            f"extra={sorted(c5_actual - c5_declared)}"
        )

    c5_root = (REPO_ROOT / "targets/c5/CMakeLists.txt").read_text(encoding="utf-8")
    if "project(leshy2_c5)" not in c5_root or "IDF_COMPONENT_MANAGER" not in c5_root:
        errors.append("C5 root project identity/offline policy is incomplete")
    c5_main_cmake = (REPO_ROOT / "targets/c5/main/CMakeLists.txt").read_text(encoding="utf-8")
    c5_portable_cmake = (
        REPO_ROOT / "targets/c5/components/leshy2_portable/CMakeLists.txt"
    ).read_text(encoding="utf-8")
    for name, content in (("main", c5_main_cmake), ("portable", c5_portable_cmake)):
        missing = {flag for flag in required_project_flags if flag not in content}
        if missing:
            errors.append(f"C5 {name} component misses flags: {sorted(missing)}")
    for flag in ("-Wconversion", "-Wdouble-promotion", "-Wmissing-prototypes", "-Wpedantic", "-Wstrict-prototypes"):
        if flag not in c5_portable_cmake:
            errors.append(f"C5 portable component misses {flag}")

    c5_main = (REPO_ROOT / "targets/c5/main/app_main.c").read_text(encoding="utf-8")
    check_esp_sdk_warning_boundary(c5_main, "C5", errors)
    if "l2ip_replay_guard_reset" not in c5_main or "leshy2/l2ip.h" not in c5_main:
        errors.append("C5 entry point does not consume the portable core")
    if PIN_RE.search(c5_main):
        errors.append("C5 entry point contains a temporary pin assignment before F2.3")

    c5_defaults = (REPO_ROOT / "targets/c5/sdkconfig.defaults").read_text(encoding="utf-8")
    for required in (
        "CONFIG_ESPTOOLPY_FLASHSIZE_8MB=y",
        'CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="../../config/partitions_8m_c5.csv"',
        "CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE=y",
        "CONFIG_SPIRAM=y",
        "CONFIG_SPIRAM_USE_MALLOC=y",
    ):
        if required not in c5_defaults:
            errors.append(f"C5 defaults miss {required}")
    c5_debug = (REPO_ROOT / "targets/c5/sdkconfig.debug").read_text(encoding="utf-8")
    c5_release = (REPO_ROOT / "targets/c5/sdkconfig.release").read_text(encoding="utf-8")
    if "CONFIG_COMPILER_OPTIMIZATION_DEBUG=y" not in c5_debug:
        errors.append("C5 debug configuration does not select -Og")
    if "CONFIG_COMPILER_OPTIMIZATION_SIZE=y" not in c5_release:
        errors.append("C5 release configuration does not select -Os")
    if "CONFIG_COMPILER_OPTIMIZATION_ASSERTIONS_DISABLE=y" not in c5_release:
        errors.append("C5 release configuration does not disable assertions")

    rp = projects.get("rp", {})
    if rp.get("substep") != "F2.2.2" or rp.get("status") != "reviewed_structure":
        errors.append("RP project structure is not reviewed at F2.2.2")
    expected_rp_identity = {
        "sdk_target": "rp2350-arm-s",
        "device": "SC1512-A4 (RP2354B)",
        "project_name": "leshy2_rp",
        "board": "leshy2_rp2354b",
        "flash_bytes": 2097152,
        "partition_source": "config/rp2354b_partitions.json",
    }
    for key, value in expected_rp_identity.items():
        if rp.get(key) != value:
            errors.append(f"RP {key} changed: expected {value!r}")
    for claim in ("pins_consumed", "configure_run", "build_run"):
        if rp.get(claim) is not False:
            errors.append(f"RP F2.2.2 must keep {claim}=false")

    rp_declared = set(rp.get("files", []))
    rp_actual = {
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "targets/rp").rglob("*")
        if path.is_file()
    }
    if rp_actual != rp_declared:
        errors.append(
            f"RP project file registry mismatch: missing={sorted(rp_declared - rp_actual)}, "
            f"extra={sorted(rp_actual - rp_declared)}"
        )

    rp_cmake = (REPO_ROOT / "targets/rp/CMakeLists.txt").read_text(encoding="utf-8")
    for required in (
        "PICO_SDK_FETCH_FROM_GIT OFF",
        "PICO_BOARD_HEADER_DIRS",
        "project(leshy2_rp C CXX ASM)",
        "pico_sdk_init()",
        "rp2354b_partitions.json",
        "pico_add_extra_outputs(leshy2_rp)",
        "-Wl,-Map=${CMAKE_BINARY_DIR}/leshy2_rp.map",
        "$<$<CONFIG:Debug>:-Og>",
        "$<$<CONFIG:Release>:-Os>",
    ):
        if required not in rp_cmake:
            errors.append(f"RP CMake input misses {required}")
    for flag in required_project_flags | {
        "-Wconversion",
        "-Wdouble-promotion",
        "-Wmissing-prototypes",
        "-Wpedantic",
        "-Wstrict-prototypes",
    }:
        if flag not in rp_cmake:
            errors.append(f"RP target misses {flag}")

    rp_board = (REPO_ROOT / "targets/rp/boards/leshy2_rp2354b.h").read_text(encoding="utf-8")
    for required in (
        "pico_board_cmake_set(PICO_PLATFORM, rp2350-arm-s)",
        "#define PICO_RP2350A 0",
        "PICO_FLASH_SIZE_BYTES, (2 * 1024 * 1024)",
        "#define PICO_BOOT_STAGE2_CHOOSE_W25Q080 1",
    ):
        if required not in rp_board:
            errors.append(f"RP2354B board identity misses {required}")
    for forbidden in (
        "PICO_DEFAULT_UART_TX_PIN",
        "PICO_DEFAULT_UART_RX_PIN",
        "PICO_DEFAULT_I2C_SDA_PIN",
        "PICO_DEFAULT_I2C_SCL_PIN",
        "PICO_DEFAULT_SPI_SCK_PIN",
        "PICO_DEFAULT_LED_PIN",
    ):
        if forbidden in rp_board:
            errors.append(f"RP board invents pre-F2.3 peripheral pin: {forbidden}")

    rp_main = (REPO_ROOT / "targets/rp/main.c").read_text(encoding="utf-8")
    if "l2ip_replay_guard_reset" not in rp_main or "tight_loop_contents" not in rp_main:
        errors.append("RP entry point does not consume portable core and idle safely")
    if PIN_RE.search(rp_main):
        errors.append("RP entry point contains a temporary pin assignment before F2.3")

    pack = projects.get("pack", {})
    if pack.get("substep") != "F2.2.3" or pack.get("status") != "reviewed_structure":
        errors.append("Pack project structure is not reviewed at F2.2.3")
    expected_pack_identity = {
        "sdk_target": "MSPM0C1106",
        "device": "MSPM0C1106SDGS20R",
        "package": "VSSOP-20(DGS20)",
        "project_name": "leshy2_pack",
        "boot_image": "leshy2_pack_boot",
        "application_image": "leshy2_pack",
    }
    for key, value in expected_pack_identity.items():
        if pack.get(key) != value:
            errors.append(f"Pack {key} changed: expected {value!r}")
    if pack.get("boot_flash") != {"origin": 0, "bytes": 16384}:
        errors.append("Pack boot-manager region changed")
    if pack.get("application_flash") != {"origin": 16384, "bytes": 22528}:
        errors.append("Pack application-slot region changed")
    if pack.get("sram") != {"origin": 536870912, "bytes": 8192}:
        errors.append("Pack SRAM region changed")
    for claim in ("pins_consumed", "configure_run", "build_run"):
        if pack.get(claim) is not False:
            errors.append(f"Pack F2.2.3 must keep {claim}=false")

    pack_declared = set(pack.get("files", []))
    pack_actual = {
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "targets/pack").rglob("*")
        if path.is_file()
    }
    if pack_actual != pack_declared:
        errors.append(
            f"Pack project file registry mismatch: missing={sorted(pack_declared - pack_actual)}, "
            f"extra={sorted(pack_actual - pack_declared)}"
        )

    pack_make = (REPO_ROOT / "targets/pack/Makefile").read_text(encoding="utf-8")
    for required in (
        "startup_mspm0c1105_c1106_ticlang.c",
        "mspm0c1105_c1106/driverlib.a",
        "sysconfig_cli.sh",
        "-D__MSPM0C1106__",
        "-mcpu=cortex-m0plus",
        "-march=thumbv6m",
        "-Wl,--emit_warnings_as_errors",
        "tiarmobjcopy",
        "leshy2_pack_boot.out",
        "leshy2_pack.out",
    ):
        if required not in pack_make:
            errors.append(f"Pack Makefile misses {required}")
    for flag in required_project_flags | {
        "-Wconversion",
        "-Wdouble-promotion",
        "-Wmissing-prototypes",
        "-Wpedantic",
        "-Wstrict-prototypes",
    }:
        if flag not in pack_make:
            errors.append(f"Pack project misses {flag}")

    pack_syscfg = (REPO_ROOT / "targets/pack/pack.syscfg").read_text(encoding="utf-8")
    for required in (
        '--device "MSPM0C1106"',
        '--package "VSSOP-20(DGS20)"',
        'ProjectConfig.deviceSpin = "MSPM0C1106"',
    ):
        if required not in pack_syscfg:
            errors.append(f"Pack SysConfig identity misses {required}")
    if ".$assign" in pack_syscfg:
        errors.append("Pack SysConfig invents a pre-F2.3 pin assignment")

    pack_boot_link = (REPO_ROOT / "targets/pack/boot_manager.cmd").read_text(encoding="utf-8")
    pack_app_link = (REPO_ROOT / "targets/pack/slot_a.cmd").read_text(encoding="utf-8")
    for content, origin, length, label in (
        (pack_boot_link, "0x00000000", "0x00004000", "boot"),
        (pack_app_link, "0x00004000", "0x00005800", "application"),
    ):
        if f"origin = {origin}, length = {length}" not in content:
            errors.append(f"Pack {label} linker region changed")
        if "origin = 0x20000000, length = 0x00002000" not in content:
            errors.append(f"Pack {label} linker SRAM region changed")

    for relative in ("targets/pack/main.c", "targets/pack/boot_main.c"):
        if PIN_RE.search((REPO_ROOT / relative).read_text(encoding="utf-8")):
            errors.append(f"{relative} contains a temporary pin assignment before F2.3")

    safety = projects.get("safety", {})
    if safety.get("substep") != "F2.2.4" or safety.get("status") != "reviewed_structure":
        errors.append("Safety project structure is not reviewed at F2.2.4")
    expected_safety_identity = {
        "sdk_target": "MSPM0C1106",
        "device": "MSPM0C1106SDGS20R",
        "package": "VSSOP-20(DGS20)",
        "project_name": "leshy2_safety",
        "boot_image": "leshy2_safety_boot",
        "application_image": "leshy2_safety",
    }
    for key, value in expected_safety_identity.items():
        if safety.get(key) != value:
            errors.append(f"Safety {key} changed: expected {value!r}")
    if safety.get("boot_flash") != {"origin": 0, "bytes": 16384}:
        errors.append("Safety boot-manager region changed")
    if safety.get("application_flash") != {"origin": 16384, "bytes": 22528}:
        errors.append("Safety application-slot region changed")
    if safety.get("sram") != {"origin": 536870912, "bytes": 8192}:
        errors.append("Safety SRAM region changed")
    for claim in ("pins_consumed", "configure_run", "build_run"):
        if safety.get(claim) is not False:
            errors.append(f"Safety F2.2.4 must keep {claim}=false")

    safety_declared = set(safety.get("files", []))
    safety_actual = {
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "targets/safety").rglob("*")
        if path.is_file()
    }
    if safety_actual != safety_declared:
        errors.append(
            "Safety project file registry mismatch: "
            f"missing={sorted(safety_declared - safety_actual)}, "
            f"extra={sorted(safety_actual - safety_declared)}"
        )

    safety_make = (REPO_ROOT / "targets/safety/Makefile").read_text(encoding="utf-8")
    for required in (
        "startup_mspm0c1105_c1106_ticlang.c",
        "mspm0c1105_c1106/driverlib.a",
        "sysconfig_cli.sh",
        "-D__MSPM0C1106__",
        "-mcpu=cortex-m0plus",
        "-march=thumbv6m",
        "-Wl,--emit_warnings_as_errors",
        "tiarmobjcopy",
        "leshy2_safety_boot.out",
        "leshy2_safety.out",
    ):
        if required not in safety_make:
            errors.append(f"Safety Makefile misses {required}")
    for flag in required_project_flags | {
        "-Wconversion",
        "-Wdouble-promotion",
        "-Wmissing-prototypes",
        "-Wpedantic",
        "-Wstrict-prototypes",
    }:
        if flag not in safety_make:
            errors.append(f"Safety project misses {flag}")

    safety_syscfg = (REPO_ROOT / "targets/safety/safety.syscfg").read_text(encoding="utf-8")
    for required in (
        '--device "MSPM0C1106"',
        '--package "VSSOP-20(DGS20)"',
        'ProjectConfig.deviceSpin = "MSPM0C1106"',
    ):
        if required not in safety_syscfg:
            errors.append(f"Safety SysConfig identity misses {required}")
    if ".$assign" in safety_syscfg:
        errors.append("Safety SysConfig invents a pre-F2.3 pin assignment")

    safety_boot_link = (REPO_ROOT / "targets/safety/boot_manager.cmd").read_text(encoding="utf-8")
    safety_app_link = (REPO_ROOT / "targets/safety/slot_a.cmd").read_text(encoding="utf-8")
    for content, origin, length, label in (
        (safety_boot_link, "0x00000000", "0x00004000", "boot"),
        (safety_app_link, "0x00004000", "0x00005800", "application"),
    ):
        if f"origin = {origin}, length = {length}" not in content:
            errors.append(f"Safety {label} linker region changed")
        if "origin = 0x20000000, length = 0x00002000" not in content:
            errors.append(f"Safety {label} linker SRAM region changed")

    safety_main = (REPO_ROOT / "targets/safety/main.c").read_text(encoding="utf-8")
    if "l2_safety_init" not in safety_main or "safety_supervisor" not in safety_main:
        errors.append("Safety entry point does not instantiate the portable safety core")
    if "L2_UNCONFIGURED_TEMPERATURE_LIMIT_DECI_C = 0" not in safety_main:
        errors.append("Safety entry point does not default the absent F2.3 limit fail-closed")
    if "l2_safety_set_run" in safety_main:
        errors.append("Safety F2.2.4 entry point may not arm before the F2.3 BSP exists")
    for relative in ("targets/safety/main.c", "targets/safety/boot_main.c"):
        if PIN_RE.search((REPO_ROOT / relative).read_text(encoding="utf-8")):
            errors.append(f"{relative} contains a temporary pin assignment before F2.3")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("target projects OK: S3/C5/RP/Pack/Safety structures reviewed; 0 builds claimed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
