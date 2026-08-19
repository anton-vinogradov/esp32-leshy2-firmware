#!/usr/bin/env python3
"""Apply the Leshy2 S3 image-size contract to a linked application binary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LIMITS_PATH = REPO_ROOT / "config/s3_image_limits.json"


def load_limits() -> dict[str, int | str]:
    return json.loads(LIMITS_PATH.read_text(encoding="utf-8"))


def classify(size: int, limits: dict[str, int | str]) -> str:
    maximum = int(limits["maximum_image_bytes"])
    warning = int(limits["warning_bytes"])
    if size > maximum:
        return "reject"
    if size > warning:
        return "warning"
    return "ok"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path, help="linked S3 application binary")
    args = parser.parse_args()

    limits = load_limits()
    size = args.image.stat().st_size
    result = classify(size, limits)
    report = {
        "image": str(args.image),
        "size_bytes": size,
        "result": result,
        "warning_bytes": limits["warning_bytes"],
        "maximum_image_bytes": limits["maximum_image_bytes"],
        "slot_bytes": limits["slot_bytes"],
    }
    print(json.dumps(report, sort_keys=True))
    return 2 if result == "reject" else 0


if __name__ == "__main__":
    raise SystemExit(main())
