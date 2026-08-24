#!/usr/bin/env python3
"""Check one-to-one generated BSP consumption by all five target projects."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONSUMPTION_PATH = REPO_ROOT / "config" / "bsp_target_consumption.json"
TARGET_IDS = {"s3", "c5", "rp", "pack", "safety"}
LITERAL_PIN_RE = re.compile(r"\b(?:GPIO|PA)[0-9]+(?:_[A-Za-z0-9_]+)?\b")


def main() -> int:
    data = json.loads(CONSUMPTION_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if data.get("stage") != "F2.3.2" or data.get("status") != "reviewed":
        errors.append("BSP target consumption is not reviewed at F2.3.2")
    projects = data.get("projects", {})
    if set(projects) != TARGET_IDS:
        errors.append("BSP target consumption must contain exactly five projects")

    referenced_sources: list[str] = []
    expected_contacts = {"s3": 33, "c5": 14, "rp": 48, "pack": 13, "safety": 17}
    for target_id, project in projects.items():
        if project.get("contacts") != expected_contacts[target_id]:
            errors.append(f"{target_id}: contact count changed")
        build_path = REPO_ROOT / project.get("build_input", "")
        entry_path = REPO_ROOT / project.get("entrypoint", "")
        if not build_path.is_file() or not entry_path.is_file():
            errors.append(f"{target_id}: build input or entrypoint is missing")
            continue
        build = build_path.read_text(encoding="utf-8")
        entry = entry_path.read_text(encoding="utf-8")
        source_name = Path(project["source"]).name
        if build.count(source_name) != 1:
            errors.append(f"{target_id}: owned generated source must occur once in build input")
        if build.count(project["include_marker"]) != 1:
            errors.append(f"{target_id}: generated include directory must occur once")
        for other_id in TARGET_IDS - {target_id}:
            if f"{other_id}_bsp.c" in build:
                errors.append(f"{target_id}: foreign generated source {other_id}_bsp.c")
        if f'#include "{project["header"]}"' not in entry:
            errors.append(f"{target_id}: entrypoint does not include its generated header")
        if project["domain_symbol"] not in entry:
            errors.append(f"{target_id}: entrypoint does not consume its domain descriptor")
        referenced_sources.append(project["source"])

    if len(referenced_sources) != len(set(referenced_sources)):
        errors.append("one generated source is assigned to multiple target projects")

    copied = [
        path
        for target in TARGET_IDS
        for path in (REPO_ROOT / "targets" / target).rglob("*_bsp.[ch]")
    ]
    if copied:
        errors.append(f"generated BSP files were copied into targets: {copied}")

    for target in TARGET_IDS:
        for path in (REPO_ROOT / "targets" / target).rglob("*"):
            if path.is_file() and path.suffix in {".c", ".h"}:
                for line_number, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), start=1
                ):
                    if LITERAL_PIN_RE.search(line):
                        errors.append(
                            f"{path.relative_to(REPO_ROOT)}:{line_number}: "
                            "hand-authored pin literal outside generated BSP"
                        )

    claims = data.get("claims", {})
    expected_claims = {
        "one_generated_domain_per_project": True,
        "generated_sources_copied_into_targets": False,
        "temporary_or_hand_authored_pins": False,
        "target_configure_run": False,
        "target_builds_run": False,
    }
    if claims != expected_claims:
        errors.append("F2.3.2 claims changed")

    generated_check = subprocess.run(
        ("python3", "tools/generate_hardware_bsp.py", "--check"),
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if generated_check.returncode != 0:
        errors.append("generated BSP is stale")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        "BSP target consumption OK: S3/C5/RP/Pack/Safety each consume one "
        "owned generated table; 0 copied or hand-authored pins"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
