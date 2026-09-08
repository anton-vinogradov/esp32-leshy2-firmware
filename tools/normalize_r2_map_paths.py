#!/usr/bin/env python3
"""Exact checkout-prefix publication step, not a comparison-time filter.

Only map bytes are rewritten. Original maps are retained, and every other byte
(including section addresses, symbols, unknown roots and timestamps) is kept.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


HOST_ROOT = re.compile(rb"(?<![A-Za-z0-9_.:/])/(?:Users|home|private|tmp|var|opt|workspace|workspaces|builds)/[^\x00\r\n\"<>]*")
ABSOLUTE_PATH = re.compile(rb"(?<![A-Za-z0-9_.:/])/[A-Za-z_][A-Za-z0-9_.+\-]*(?:/[A-Za-z0-9_.+\-]+)+/?")
WINDOWS_PATH = re.compile(rb"(?<![A-Za-z0-9_])[A-Za-z]:[\\/][^\x00\r\n\"<>]+")
SOURCE_PATH = re.compile(
    rb"(?<![A-Za-z0-9_.:/])(?:/[A-Za-z0-9_ .+\-]+)+\.(?:c|cc|cpp|cxx|h|hpp|s|S|a|ld|o)(?=[\x00\s\"():]|$)"
)
VIRTUAL_ROOT = re.compile(rb"^/(?:IDF(?:_PROJECT|_BUILD)?|COMPONENT_[A-Za-z0-9_]+_DIR|TOOLCHAIN)(?:/|$)")
TI_HEADER = re.compile(rb"^>> Linked [^\r\n]+", re.MULTILINE)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_checkout_prefix(source: bytes, prefix: bytes) -> tuple[bytes, int]:
    """A checkout path is not the prefix of a sibling directory's name."""
    if not prefix:
        raise ValueError("empty checkout prefix")
    expression = re.compile(re.escape(prefix) + rb"(?=/|[\x00\s\"'():]|$)")
    return expression.subn(b".", source)


def source_path_findings(data: bytes, checkout_root: Path) -> list[str]:
    """Conservatively reject non-virtual absolute source/directory strings.

Directory attributes need no extension. Unknown roots trigger review, not an
automatic rewrite or silent runtime-path exception. Virtual SDK prefixes are
the only allowlist. Ordinary relative paths and URLs are not absolute roots.
"""
    found: set[str] = set()
    root = str(checkout_root.resolve()).encode()
    if root in data:
        found.add("exact checkout root")
    for expression in (HOST_ROOT, SOURCE_PATH, ABSOLUTE_PATH, WINDOWS_PATH):
        for match in expression.finditer(data):
            path = match.group()
            if not VIRTUAL_ROOT.match(path):
                found.add(path.decode("utf-8", errors="replace")[:240])
    # A DWARF string can be a whole directory containing spaces. Byte scanning
    # the NUL-delimited field avoids assuming comp_dir ends in a source suffix.
    for field in data.split(b"\x00"):
        if field.startswith(b"/") and b"/" in field[1:] and not VIRTUAL_ROOT.match(field):
            candidate = field.split(b"\n", 1)[0].split(b"\r", 1)[0]
            # Machine-code bytes can begin with '/' accidentally. This fallback
            # is for whole ordinary directory strings, not binary/control data.
            if re.fullmatch(rb"/[A-Za-z_][A-Za-z0-9_. +~/-]*", candidate):
                found.add(candidate.decode("utf-8", errors="replace")[:240])
    return sorted(found)


def ti_epoch_bytes(source: bytes, epoch: str) -> bytes:
    if not epoch.isdigit() or len(TI_HEADER.findall(source)) != 1:
        raise ValueError("TI raw map must have exactly one known Linked header and decimal epoch")
    return TI_HEADER.sub(b">> Linked SOURCE_DATE_EPOCH=" + epoch.encode(), source)


def publish_map(path: Path, raw_path: Path, checkout_root: Path) -> dict:
    if path.suffix != ".map" or path.is_symlink() or not path.is_file():
        raise ValueError("only an existing real declared map can be normalized")
    if raw_path.exists() or raw_path.is_symlink():
        raise ValueError("raw map recovery must never be overwritten")
    source = path.read_bytes()
    prefix = str(checkout_root.resolve()).encode()
    published, count = replace_checkout_prefix(source, prefix)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with raw_path.open("xb") as recovery:
        recovery.write(source)
    path.write_bytes(published)
    return {
        "raw_sha256": digest(source),
        "published_sha256": digest(published),
        "replacement_count": count,
        "other_bytes_unchanged": True,
    }


def publication_errors(record: dict, raw: bytes, published: bytes, prefix: bytes) -> list[str]:
    if not prefix:
        return ["empty checkout prefix"]
    expected_bytes, count = replace_checkout_prefix(raw, prefix)
    expected = {
        "raw_sha256": digest(raw),
        "published_sha256": digest(published),
        "replacement_count": count,
        "other_bytes_unchanged": True,
    }
    errors = []
    if any(record.get(key) != value for key, value in expected.items()):
        errors.append("map publication hashes/counts changed")
    if expected_bytes != published:
        errors.append("map publication changed bytes other than its exact checkout prefix")
    return errors
