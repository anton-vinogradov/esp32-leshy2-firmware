#!/usr/bin/env python3
"""Import and verify the exact normalized ESSL component payload."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path, PurePosixPath


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "config" / "f4_0_1_adapter_contract.json"
VENDOR_ROOT = REPO_ROOT / "third_party" / "esp_serial_slave_link"
MANIFEST_PATH = REPO_ROOT / "third_party" / "esp_serial_slave_link.vendor-lock.json"
ARCHIVE_PREFIX = PurePosixPath("esp_serial_slave_link")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_records(records: list[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for name, content in sorted(records):
        encoded = name.encode("utf-8")
        digest.update(struct.pack("<I", len(encoded)))
        digest.update(encoded)
        digest.update(struct.pack("<Q", len(content)))
        digest.update(hashlib.sha256(content).digest())
    return digest.hexdigest()


def archive_records(path: Path) -> list[tuple[str, bytes]]:
    with zipfile.ZipFile(path) as archive:
        records: list[tuple[str, bytes]] = []
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            parsed = PurePosixPath(entry.filename)
            if parsed.is_absolute() or ".." in parsed.parts:
                raise ValueError(f"unsafe archive path: {entry.filename}")
            if not parsed.parts or parsed.parts[0] != str(ARCHIVE_PREFIX):
                raise ValueError(f"unexpected archive root: {entry.filename}")
            records.append((parsed.as_posix(), archive.read(entry)))
    return sorted(records)


def vendor_records() -> list[tuple[str, bytes]]:
    if not VENDOR_ROOT.is_dir():
        return []
    return [
        (
            (ARCHIVE_PREFIX / path.relative_to(VENDOR_ROOT).as_posix()).as_posix(),
            path.read_bytes(),
        )
        for path in sorted(VENDOR_ROOT.rglob("*"))
        if path.is_file()
    ]


def expected_lock() -> dict:
    return load(CONTRACT_PATH)["essl_dependency_lock"]


def validate_records(records: list[tuple[str, bytes]]) -> list[str]:
    lock = expected_lock()
    errors: list[str] = []
    if len(records) != lock["file_count"]:
        errors.append(
            f"ESSL file count differs: expected {lock['file_count']}, got {len(records)}"
        )
    payload_hash = canonical_records(records)
    expected_hash = lock["canonical_payload_hash"]["sha256"]
    if payload_hash != expected_hash:
        errors.append(
            f"ESSL normalized payload differs: expected {expected_hash}, got {payload_hash}"
        )
    names = {name for name, _ in records}
    required = {
        "esp_serial_slave_link/LICENSE",
        "esp_serial_slave_link/CMakeLists.txt",
        "esp_serial_slave_link/idf_component.yml",
        "esp_serial_slave_link/essl.c",
        "esp_serial_slave_link/essl_sdio.c",
        "esp_serial_slave_link/include/esp_serial_slave_link/essl.h",
        "esp_serial_slave_link/include/esp_serial_slave_link/essl_sdio.h",
    }
    missing = required - names
    if missing:
        errors.append("ESSL required files are missing: " + ", ".join(sorted(missing)))
    return errors


def manifest_for(records: list[tuple[str, bytes]]) -> dict:
    lock = expected_lock()
    return {
        "schema_version": 1,
        "stage": "F4.1.0",
        "status": "imported",
        "component": lock["component"],
        "version": lock["version"],
        "license": lock["license"],
        "registry_object_id": lock["registry_object_id"],
        "repository_commit": lock["repository_commit"],
        "repository_path": lock["repository_path"],
        "canonical_payload_sha256": canonical_records(records),
        "producer": "tools/vendor_essl.py",
        "files": [
            {
                "path": "third_party/" + name,
                "bytes": len(content),
                "sha256": sha256_bytes(content),
            }
            for name, content in records
        ],
    }


def import_archive(path: Path) -> None:
    records = archive_records(path)
    errors = validate_records(records)
    if errors:
        raise ValueError("; ".join(errors))
    if VENDOR_ROOT.exists():
        current = vendor_records()
        if current != records:
            raise ValueError("vendor destination exists with different content")
    else:
        for name, content in records:
            relative = PurePosixPath(name).relative_to(ARCHIVE_PREFIX)
            destination = VENDOR_ROOT.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest_for(records), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def check_vendor() -> list[str]:
    records = vendor_records()
    errors = validate_records(records)
    if not MANIFEST_PATH.is_file():
        return errors + ["ESSL vendor manifest is missing"]
    manifest = load(MANIFEST_PATH)
    expected = manifest_for(records)
    if manifest != expected:
        errors.append("ESSL vendor manifest differs from the checked-in payload")
    component_manifest = VENDOR_ROOT / "idf_component.yml"
    if component_manifest.is_file():
        text = component_manifest.read_text(encoding="utf-8")
        lock = expected_lock()
        for token in (
            f"version: {lock['version']}",
            f"commit_sha: {lock['repository_commit']}",
            f"path: {lock['repository_path']}",
        ):
            if token not in text:
                errors.append(f"ESSL component manifest lacks {token!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--verify-archive", type=Path)
    mode.add_argument("--import-archive", type=Path)
    args = parser.parse_args()

    try:
        if args.verify_archive is not None:
            errors = validate_records(archive_records(args.verify_archive))
        elif args.import_archive is not None:
            import_archive(args.import_archive)
            errors = check_vendor()
        else:
            errors = check_vendor()
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        errors = [str(error)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    action = "archive" if args.verify_archive is not None else "vendor tree"
    print(f"ESSL 1.1.2 {action} OK: 30 files, normalized payload hash locked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
