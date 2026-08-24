#!/usr/bin/env python3
"""Replace the TI linker's wall-clock map header with SOURCE_DATE_EPOCH."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


LINKED_RE = re.compile(r"^>> Linked .+$", re.MULTILINE)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("map_file", type=Path)
    args = parser.parse_args()
    epoch = os.environ.get("SOURCE_DATE_EPOCH", "")
    if not epoch.isdigit():
        print("ERROR: SOURCE_DATE_EPOCH must be a decimal Unix timestamp", file=sys.stderr)
        return 1
    source = args.map_file.read_text(encoding="utf-8")
    normalized, replacements = LINKED_RE.subn(
        f">> Linked SOURCE_DATE_EPOCH={epoch}", source, count=1
    )
    if replacements != 1:
        print(f"ERROR: TI map timestamp header not found: {args.map_file}", file=sys.stderr)
        return 1
    args.map_file.write_text(normalized, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
