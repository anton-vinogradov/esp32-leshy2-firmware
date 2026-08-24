#!/usr/bin/env python3
"""Fail when portable, generated and target-local source boundaries blur."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LAYOUT_PATH = REPO_ROOT / "config" / "source_layout.json"
MANIFEST_PATH = REPO_ROOT / "generated" / "source_manifest.json"
INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]')


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    layout = load(LAYOUT_PATH)
    manifest = load(MANIFEST_PATH)
    errors: list[str] = []

    if layout.get("status") != "reviewed":
        errors.append("source layout is not reviewed")
    principles = layout.get("principles", {})
    expected_principles = {
        "one_owner_per_path": True,
        "portable_code_has_target_pins": False,
        "generated_files_are_hand_edited": False,
        "build_outputs_are_source_inputs": False,
    }
    if principles != expected_principles:
        errors.append("source-layout principles changed")

    expected = set(layout.get("expected_portable_files", []))
    actual = {
        str(path.relative_to(REPO_ROOT))
        for root in (REPO_ROOT / "common/include", REPO_ROOT / "common/src")
        for path in root.rglob("*")
        if path.is_file()
    }
    if actual != expected:
        errors.append(
            f"portable file registry mismatch: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )

    forbidden = tuple(layout.get("portable_forbidden_include_prefixes", []))
    for relative in sorted(actual):
        for line_number, line in enumerate(
            (REPO_ROOT / relative).read_text(encoding="utf-8").splitlines(), start=1
        ):
            match = INCLUDE_RE.match(line)
            if match and match.group(1).startswith(forbidden):
                errors.append(
                    f"{relative}:{line_number}: target include {match.group(1)} "
                    "is forbidden in portable code"
                )

    if manifest.get("producer") != "tools/generate_hardware_bsp.py":
        errors.append("generated manifest has an unexpected producer")
    if manifest.get("status") != "boundary_only" or manifest.get("files") != []:
        errors.append("hardware sources must remain empty until F2.3")

    imported = {
        area["path"]: area
        for area in layout.get("areas", [])
        if area.get("owner") == "hardware_contract_importer"
    }
    for relative in (
        "config/hardware_bsp_contract.json",
        "config/hardware_integration_contract.json",
    ):
        if relative not in imported or not (REPO_ROOT / relative).is_file():
            errors.append(f"missing importer-owned hardware contract: {relative}")
        elif imported[relative].get("hand_maintained") is not False:
            errors.append(f"{relative}: generated contract cannot be hand maintained")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        f"source layout OK: {len(actual)} portable files, "
        "generated hardware boundary empty until F2.3"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
