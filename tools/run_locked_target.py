#!/usr/bin/env python3
"""Run one canonical target action inside the reviewed local toolchain."""

from __future__ import annotations

import argparse
import subprocess
import sys

from review_f2_4_preflight import REPO_ROOT, local_environment


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=("preflight", "configure", "build", "clean", "verify", "artifacts")
    )
    parser.add_argument(
        "--target", choices=("all", "s3", "c5", "rp", "pack", "safety"), default="all"
    )
    parser.add_argument("--config", choices=("debug", "release"), default="debug")
    args = parser.parse_args()
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/build_targets.py"),
            args.action,
            "--target",
            args.target,
            "--config",
            args.config,
        ],
        cwd=REPO_ROOT,
        env=local_environment(),
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
