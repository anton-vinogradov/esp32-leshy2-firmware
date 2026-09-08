#!/usr/bin/env python3
"""Fail configure when IDF silently drops the existing N8R8 memory contract.

Authority: config/sdkconfig.defaults.esp32c5 and docs/memory.md. The module has
8 MiB physical quad PSRAM. Keep the IDF 6.0.2 default 40 MHz and ECC disabled.
This checks configuration only, not detected capacity, allocator free space,
initialization, memory integrity, GPIO wiring, or powered-hardware readiness.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]
CONTRACT_DEFAULTS = ROOT / "config/sdkconfig.defaults.esp32c5"
REQUIRED_TRUE = (
    "CONFIG_ESPTOOLPY_FLASHSIZE_8MB",
    "CONFIG_PARTITION_TABLE_CUSTOM",
    "CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE",
    "CONFIG_SPIRAM",
    "CONFIG_SPIRAM_BOOT_INIT",
    "CONFIG_SPIRAM_USE_MALLOC",
)
# These must not bypass required RAM or change the accepted quad-flash/quad-RAM
# interface. Unset Kconfig booleans are normally emitted as comments (or absent).
REQUIRED_FALSE = (
    "CONFIG_SPIRAM_IGNORE_NOTFOUND",
    "CONFIG_SPIRAM_MODE_OCT",
    "CONFIG_SPIRAM_ECC_ENABLE",
    "CONFIG_SPIRAM_SPEED_80M",
    "CONFIG_SPIRAM_SPEED_120M",
    "CONFIG_ESPTOOLPY_OCT_FLASH",
)


def parse_config(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        disabled = re.fullmatch(r"# (CONFIG_[A-Z0-9_]+) is not set", line)
        assigned = re.fullmatch(r"(CONFIG_[A-Z0-9_]+)=(.*)", line)
        if disabled:
            key, value = disabled[1], "n"
        elif assigned:
            key, value = assigned[1], assigned[2]
        elif not line or line.startswith("#"):
            continue
        else:
            raise ValueError(f"invalid sdkconfig line {number}: {line}")
        if key in values:
            raise ValueError(f"duplicate sdkconfig key: {key}")
        values[key] = value
    return values


def configuration_errors(
    config: dict[str, str], components: list[str],
    canonical: dict[str, str], target_defaults: dict[str, str],
    project: Path = PROJECT, root: Path = ROOT,
) -> list[str]:
    errors: list[str] = []
    if "esp_psram" not in components:
        errors.append("esp_psram is absent from IDF BUILD_COMPONENTS")
    for key in REQUIRED_TRUE:
        for label, values in (("canonical defaults", canonical),
                              ("C5 defaults", target_defaults), ("resolved sdkconfig", config)):
            if values.get(key) != "y":
                errors.append(f"{label}: {key} must be y (got {values.get(key)!r})")
    for key in REQUIRED_FALSE:
        for label, values in (("canonical defaults", canonical),
                              ("C5 defaults", target_defaults), ("resolved sdkconfig", config)):
            if values.get(key, "n") != "n":
                errors.append(f"{label}: {key} must be disabled")
    # BOOT_HW_INIT and numeric/string values are IDF-derived, not new defaults.
    for key, value in {
        "CONFIG_IDF_TARGET": '"esp32c5"',
        "CONFIG_SPIRAM_BOOT_HW_INIT": "y",
        "CONFIG_SPIRAM_MODE_QUAD": "y",
        "CONFIG_SPIRAM_SPEED_40M": "y",
        "CONFIG_SPIRAM_SPEED": "40",
        "CONFIG_ESPTOOLPY_FLASHSIZE": '"8MB"',
    }.items():
        if config.get(key) != value:
            errors.append(f"resolved sdkconfig: {key} must be {value} (got {config.get(key)!r})")
    expected_partition = (root / "config/partitions_8m_c5.csv").resolve()
    for label, values, base in (("canonical defaults", canonical, root),
                                ("C5 defaults", target_defaults, project),
                                ("resolved sdkconfig", config, project)):
        value = values.get("CONFIG_PARTITION_TABLE_CUSTOM_FILENAME", "")
        if not (value.startswith('"') and value.endswith('"')):
            errors.append(f"{label}: quoted custom partition filename is required")
        elif (base / value[1:-1]).resolve() != expected_partition:
            errors.append(f"{label}: custom partition must resolve to config/partitions_8m_c5.csv")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdkconfig", type=Path, required=True)
    parser.add_argument("--components", nargs="+", required=True)
    arguments = parser.parse_args()
    try:
        errors = configuration_errors(
            parse_config(arguments.sdkconfig.read_text()), arguments.components,
            parse_config(CONTRACT_DEFAULTS.read_text()),
            parse_config((PROJECT / "sdkconfig.defaults").read_text()),
        )
    except (OSError, ValueError) as error:
        errors = [str(error)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("C5 resolved configuration: 8-MiB flash, quad PSRAM 40 MHz, boot init + malloc, ECC disabled; "
          "capacity and runtime checks remain open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

