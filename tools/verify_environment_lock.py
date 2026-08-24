#!/usr/bin/env python3
"""Validate the F2 build-environment lock and optionally verify an archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = REPO_ROOT / "environment" / "toolchains.lock.json"
SHA256_RE = re.compile(r"[0-9a-f]{64}")
COMMIT_RE = re.compile(r"[0-9a-f]{40}")
ALLOWED_DOWNLOAD_HOSTS = {
    "armkeil.blob.core.windows.net",
    "dr-download.ti.com",
    "github.com",
}
REQUIRED_TOOLS = {
    "shared": {"cmake", "ninja"},
    "esp_idf": {
        "xtensa-esp-elf",
        "riscv32-esp-elf",
        "xtensa-esp-elf-gdb",
        "riscv32-esp-elf-gdb",
        "esp32ulp-elf",
        "openocd-esp32",
        "esp-rom-elfs",
    },
    "pico_sdk": {"arm-none-eabi"},
    "ti_mspm0_sdk": {"mspm0-sdk", "ti-arm-clang", "sysconfig"},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_lock(path: Path) -> dict:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def validate(lock: dict) -> list[str]:
    errors: list[str] = []
    if lock.get("status") != "reviewed":
        errors.append("lock status must be reviewed")
    if lock.get("policy", {}).get("floating_versions_allowed") is not False:
        errors.append("floating versions must be forbidden")

    profiles = set(lock.get("host_profiles", {}))
    if profiles != {"linux_x86_64", "macos_arm64"}:
        errors.append(f"unexpected host profiles: {sorted(profiles)}")

    for source in lock.get("source_revisions", []):
        if not COMMIT_RE.fullmatch(source.get("commit", "")):
            errors.append(f"{source.get('id')}: invalid commit")
        if not source.get("repository", "").startswith("https://"):
            errors.append(f"{source.get('id')}: repository must use HTTPS")

    archive_ids: set[str] = set()
    coverage = {
        profile: {family: set() for family in REQUIRED_TOOLS}
        for profile in profiles
    }
    for archive in lock.get("archives", []):
        archive_id = archive.get("id", "")
        if archive_id in archive_ids:
            errors.append(f"duplicate archive id: {archive_id}")
        archive_ids.add(archive_id)

        url = archive.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme != "https":
            errors.append(f"{archive_id}: URL must use HTTPS")
        if parsed.hostname not in ALLOWED_DOWNLOAD_HOSTS:
            errors.append(f"{archive_id}: unapproved download host {parsed.hostname}")
        if not SHA256_RE.fullmatch(archive.get("sha256", "")):
            errors.append(f"{archive_id}: invalid SHA-256")
        if not archive.get("version"):
            errors.append(f"{archive_id}: missing version")

        host = archive.get("host")
        family = archive.get("family")
        if host not in profiles:
            errors.append(f"{archive_id}: unknown host {host}")
        elif family not in REQUIRED_TOOLS:
            errors.append(f"{archive_id}: unknown family {family}")
        else:
            coverage[host][family].add(archive.get("tool"))

    for host, families in coverage.items():
        for family, required in REQUIRED_TOOLS.items():
            missing = required - families[family]
            if missing:
                errors.append(f"{host}/{family}: missing {sorted(missing)}")

    for local in lock.get("local_locks", []):
        relative = Path(local.get("path", ""))
        path = REPO_ROOT / relative
        if not path.is_file():
            errors.append(f"{local.get('id')}: missing {relative}")
            continue
        actual = sha256(path)
        if actual != local.get("sha256"):
            errors.append(
                f"{local.get('id')}: SHA-256 {actual} != {local.get('sha256')}"
            )

    return errors


def verify_archive(lock: dict, archive_id: str, path: Path) -> str | None:
    archive = next(
        (item for item in lock.get("archives", []) if item.get("id") == archive_id),
        None,
    )
    if archive is None:
        return f"unknown archive id: {archive_id}"
    if not path.is_file():
        return f"archive does not exist: {path}"
    actual = sha256(path)
    expected = archive["sha256"]
    if actual != expected:
        return f"{archive_id}: SHA-256 {actual} != {expected}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument(
        "--archive",
        nargs=2,
        metavar=("ID", "PATH"),
        help="also verify one downloaded archive against its lock entry",
    )
    args = parser.parse_args()

    lock = load_lock(args.lock)
    errors = validate(lock)
    if args.archive:
        archive_error = verify_archive(lock, args.archive[0], Path(args.archive[1]))
        if archive_error:
            errors.append(archive_error)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        f"environment lock OK: {len(lock['archives'])} archives, "
        f"{len(lock['source_revisions'])} source revisions, "
        f"{len(lock['local_locks'])} local locks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
