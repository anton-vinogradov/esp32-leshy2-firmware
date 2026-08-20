#!/usr/bin/env python3
"""Check a linked Leshy2 domain image against its machine-readable slot limit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_LIMITS = {
    "s3": REPO_ROOT / "config/s3_image_limits.json",
    "c5": REPO_ROOT / "config/c5_image_limits.json",
    "rp2354b": REPO_ROOT / "config/rp2354b_image_limits.json",
    "pack": REPO_ROOT / "config/mspm0c1106_memory.json",
    "safety": REPO_ROOT / "config/mspm0c1106_memory.json",
}


def load_limits(target: str) -> dict[str, int | str]:
    return json.loads(TARGET_LIMITS[target].read_text(encoding="utf-8"))


def classify(size: int, limits: dict[str, int | str]) -> str:
    if size > int(limits["maximum_image_bytes"]):
        return "reject"
    if size > int(limits["warning_bytes"]):
        return "warning"
    return "ok"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", choices=tuple(TARGET_LIMITS))
    parser.add_argument("image", type=Path, help="linked or packaged target image")
    args = parser.parse_args()

    limits = load_limits(args.target)
    size = args.image.stat().st_size
    result = classify(size, limits)
    print(
        json.dumps(
            {
                "target": args.target,
                "image": str(args.image),
                "size_bytes": size,
                "result": result,
                "warning_bytes": limits["warning_bytes"],
                "maximum_image_bytes": limits["maximum_image_bytes"],
                "slot_bytes": limits["slot_bytes"],
            },
            sort_keys=True,
        )
    )
    return 2 if result == "reject" else 0


if __name__ == "__main__":
    raise SystemExit(main())
