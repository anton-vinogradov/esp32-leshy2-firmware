#!/usr/bin/env python3
"""Refresh or verify the current R2 firmware hash chain and generated BSP.

The hardware projection is an input to this tool.  Generate it first with
``sync_h0_r2_contract.py --write``; this tool deliberately never reads the
hardware repository and never regenerates that projection.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "tools" / "generate_f2_r2_bsp.py"

PROJECTION = "config/h0_r2_hardware_contract.json"
F0_REVIEW = "config/f0_r2_review.json"
F1_PORTABLE = "config/f1_r2_portable_rebaseline.json"
F2_REBASELINE = "config/f2_r2_target_rebaseline.json"
F2_MATRIX = "config/f2_r2_build_matrix.json"
F2_PROJECTS = "config/f2_r2_target_projects.json"
F2_BSP_MODEL = "config/f2_r2_bsp_generation.json"

CONFIG_OUTPUTS = (
    F0_REVIEW,
    F1_PORTABLE,
    F2_REBASELINE,
    F2_MATRIX,
    F2_PROJECTS,
    F2_BSP_MODEL,
)
EXPECTED_BSP_OUTPUTS = {
    "root": "generated/r2/hardware",
    "include_root": "generated/r2/hardware/include",
    "source_root": "generated/r2/hardware/src",
    "manifest": "generated/r2/source_manifest.json",
}
HEX_DIGEST_RE = re.compile(r"[0-9a-f]{64}")


class ChainError(ValueError):
    """The checked-in hash graph is malformed or unsafe to update."""


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_text(root: Path, relative: str) -> str:
    path = root / relative
    if not path.is_file():
        raise ChainError(f"missing required input: {relative}")
    return path.read_text(encoding="utf-8")


def load_json(text: str, relative: str) -> dict:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise ChainError(f"invalid JSON in {relative}: {error}") from error
    if not isinstance(value, dict):
        raise ChainError(f"top-level JSON value is not an object: {relative}")
    return value


def nested_record(data: dict, keys: tuple[str, ...], relative: str) -> dict:
    value: object = data
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            raise ChainError(f"missing {'/'.join(keys)} in {relative}")
        value = value[key]
    if not isinstance(value, dict):
        raise ChainError(f"{'/'.join(keys)} is not an object in {relative}")
    return value


def require_identity(data: dict, relative: str, key: str, expected: str) -> None:
    if data.get(key) != expected:
        raise ChainError(
            f"{relative} {key} changed: expected {expected!r}, got {data.get(key)!r}"
        )


def replace_direct_digest(
    text: str,
    *,
    relative: str,
    key: str,
    expected: str,
) -> str:
    data = load_json(text, relative)
    old = data.get(key)
    if not isinstance(old, str) or HEX_DIGEST_RE.fullmatch(old) is None:
        raise ChainError(f"{key} is not a lowercase SHA-256 in {relative}")
    pattern = re.compile(
        rf'("{re.escape(key)}"\s*:\s*")([0-9a-f]{{64}})(")'
    )
    updated, count = pattern.subn(rf"\g<1>{expected}\g<3>", text)
    if count != 1:
        raise ChainError(f"expected one textual {key} field in {relative}, found {count}")
    if load_json(updated, relative).get(key) != expected:
        raise ChainError(f"failed to update {key} in {relative}")
    return updated


def replace_locked_digest(
    text: str,
    *,
    relative: str,
    keys: tuple[str, ...],
    expected_path: str,
    expected_digest: str,
) -> str:
    data = load_json(text, relative)
    record = nested_record(data, keys, relative)
    if record.get("path") != expected_path:
        raise ChainError(
            f"{'/'.join(keys)} path changed in {relative}: {record.get('path')!r}"
        )
    old = record.get("sha256")
    if not isinstance(old, str) or HEX_DIGEST_RE.fullmatch(old) is None:
        raise ChainError(
            f"{'/'.join(keys)}/sha256 is not a lowercase SHA-256 in {relative}"
        )
    encoded_path = re.escape(json.dumps(expected_path, ensure_ascii=False))
    pattern = re.compile(
        rf'("path"\s*:\s*{encoded_path}\s*,\s*"sha256"\s*:\s*")'
        rf'([0-9a-f]{{64}})(")'
    )
    updated, count = pattern.subn(rf"\g<1>{expected_digest}\g<3>", text)
    if count != 1:
        raise ChainError(
            f"expected one lock for {expected_path} in {relative}, found {count}"
        )
    updated_record = nested_record(load_json(updated, relative), keys, relative)
    if updated_record.get("sha256") != expected_digest:
        raise ChainError(f"failed to update {'/'.join(keys)} in {relative}")
    return updated


def load_bsp_renderer() -> Callable[[dict, dict], dict[str, str]]:
    spec = importlib.util.spec_from_file_location("generate_f2_r2_bsp", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise ChainError("cannot load tools/generate_f2_r2_bsp.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render_all


def validate_bsp_paths(model: dict, rendered: dict[str, str]) -> None:
    if model.get("outputs") != EXPECTED_BSP_OUTPUTS:
        raise ChainError("F2 BSP output roots changed; refusing an unbounded write")
    if len(rendered) != 14:
        raise ChainError(f"F2 BSP renderer returned {len(rendered)} files instead of 14")
    manifest = EXPECTED_BSP_OUTPUTS["manifest"]
    for relative, content in rendered.items():
        if not isinstance(relative, str) or not isinstance(content, str):
            raise ChainError("F2 BSP renderer returned a non-text output")
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            raise ChainError(f"unsafe generated BSP path: {relative!r}")
        if relative != manifest and not relative.startswith("generated/r2/hardware/"):
            raise ChainError(f"generated BSP path escapes its fixed tree: {relative}")


def expected_outputs(
    root: Path = ROOT,
    *,
    render_bsp: Callable[[dict, dict], dict[str, str]] | None = None,
) -> dict[str, str]:
    """Build every expected changed file in memory, following dependency order."""

    projection_text = read_text(root, PROJECTION)
    projection = load_json(projection_text, PROJECTION)
    require_identity(projection, PROJECTION, "id", "FW-H0-R2")
    hardware_source_digest = projection.get("hardware_source_sha256")
    if (
        not isinstance(hardware_source_digest, str)
        or HEX_DIGEST_RE.fullmatch(hardware_source_digest) is None
    ):
        raise ChainError(f"hardware_source_sha256 is invalid in {PROJECTION}")
    functional = nested_record(
        projection, ("hardware_sources", "functional"), PROJECTION
    )
    if functional.get("sha256") != hardware_source_digest:
        raise ChainError("projection functional source and compatibility source hashes differ")
    projection_digest = digest_text(projection_text)

    original_f0_text = read_text(root, F0_REVIEW)
    original_f0 = load_json(original_f0_text, F0_REVIEW)
    require_identity(original_f0, F0_REVIEW, "stage", "F0-R2")
    if original_f0.get("hardware_source") != projection.get("hardware_source"):
        raise ChainError("F0 review and projection identify different hardware sources")
    f0_text = replace_direct_digest(
        original_f0_text,
        relative=F0_REVIEW,
        key="hardware_source_sha256",
        expected=hardware_source_digest,
    )
    f0_digest = digest_text(f0_text)

    original_f1_text = read_text(root, F1_PORTABLE)
    require_identity(
        load_json(original_f1_text, F1_PORTABLE),
        F1_PORTABLE,
        "stage",
        "F1-R2.0",
    )
    f1_text = replace_locked_digest(
        original_f1_text,
        relative=F1_PORTABLE,
        keys=("inputs", "f0_review"),
        expected_path=F0_REVIEW,
        expected_digest=f0_digest,
    )

    original_rebaseline_text = read_text(root, F2_REBASELINE)
    require_identity(
        load_json(original_rebaseline_text, F2_REBASELINE),
        F2_REBASELINE,
        "stage",
        "F2-R2.0",
    )
    rebaseline_text = replace_locked_digest(
        original_rebaseline_text,
        relative=F2_REBASELINE,
        keys=("inputs", "r2_hardware_projection"),
        expected_path=PROJECTION,
        expected_digest=projection_digest,
    )
    rebaseline_digest = digest_text(rebaseline_text)

    original_matrix_text = read_text(root, F2_MATRIX)
    require_identity(
        load_json(original_matrix_text, F2_MATRIX),
        F2_MATRIX,
        "stage",
        "F2-R2.1",
    )
    matrix_text = replace_locked_digest(
        original_matrix_text,
        relative=F2_MATRIX,
        keys=("inputs", "rebaseline_plan"),
        expected_path=F2_REBASELINE,
        expected_digest=rebaseline_digest,
    )
    matrix_digest = digest_text(matrix_text)

    original_projects_text = read_text(root, F2_PROJECTS)
    require_identity(
        load_json(original_projects_text, F2_PROJECTS),
        F2_PROJECTS,
        "stage",
        "F2-R2.2",
    )
    projects_text = replace_locked_digest(
        original_projects_text,
        relative=F2_PROJECTS,
        keys=("inputs", "r2_hardware_projection"),
        expected_path=PROJECTION,
        expected_digest=projection_digest,
    )
    projects_text = replace_locked_digest(
        projects_text,
        relative=F2_PROJECTS,
        keys=("inputs", "build_matrix"),
        expected_path=F2_MATRIX,
        expected_digest=matrix_digest,
    )

    original_bsp_model_text = read_text(root, F2_BSP_MODEL)
    require_identity(
        load_json(original_bsp_model_text, F2_BSP_MODEL),
        F2_BSP_MODEL,
        "stage",
        "F2-R2.3",
    )
    bsp_model_text = replace_locked_digest(
        original_bsp_model_text,
        relative=F2_BSP_MODEL,
        keys=("source",),
        expected_path=PROJECTION,
        expected_digest=projection_digest,
    )
    bsp_model = load_json(bsp_model_text, F2_BSP_MODEL)
    renderer = render_bsp if render_bsp is not None else load_bsp_renderer()
    try:
        generated = renderer(bsp_model, projection)
    except (KeyError, TypeError, ValueError) as error:
        raise ChainError(f"BSP generation input is invalid: {error}") from error
    validate_bsp_paths(bsp_model, generated)

    outputs = {
        F0_REVIEW: f0_text,
        F1_PORTABLE: f1_text,
        F2_REBASELINE: rebaseline_text,
        F2_MATRIX: matrix_text,
        F2_PROJECTS: projects_text,
        F2_BSP_MODEL: bsp_model_text,
    }
    outputs.update(generated)
    return outputs


def run(
    *,
    root: Path = ROOT,
    write: bool = False,
    render_bsp: Callable[[dict, dict], dict[str, str]] | None = None,
) -> int:
    outputs = expected_outputs(root, render_bsp=render_bsp)
    stale = [
        relative
        for relative, expected in outputs.items()
        if not (root / relative).is_file()
        or (root / relative).read_text(encoding="utf-8") != expected
    ]
    if not write:
        if stale:
            for relative in stale:
                print(f"stale: {relative}")
            return 1
        print("R2 hash chain and generated BSP are current")
        return 0

    for relative in stale:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(outputs[relative], encoding="utf-8")
        print(f"updated: {relative}")
    if not stale:
        print("R2 hash chain and generated BSP are already current")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify the current R2 hash cascade and BSP, or update it explicitly. "
            "The default is read-only."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify without writing (default)")
    mode.add_argument("--write", action="store_true", help="update locks and generated BSP")
    args = parser.parse_args(argv)
    try:
        return run(write=args.write)
    except (ChainError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
