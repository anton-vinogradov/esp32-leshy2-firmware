"""Import current H3 diagnostics without turning a review gap into authority.

The hardware repository owns the exact applicability schema. Every direct and
transitive recorded source is checked before retaining even provisional data.
These JSON imports are evidence/requirements, not runtime admission flags.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HW = Path(__file__).resolve().parents[1].parent / "esp32-leshy2"


def hardware_scope():
    path = HW / "hardware/verification/h3_r2_current_scope.py"
    spec = importlib.util.spec_from_file_location("hardware_h3_current_scope", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inspect_current_power(sources):
    """Require complete fresh proof for PASS and review_required alike."""
    owner = hardware_scope()
    canonical_artifacts = {
        (HW / "hardware/verification/generated" / (artifact + ".json")).resolve(): artifact
        for artifact in owner.REQUIREMENTS
    }
    visited, active, proofs, snapshot, proof_paths = set(), set(), {}, {}, {}

    def visit(path, expected_artifact=None):
        path = Path(path).resolve()
        if not path.is_relative_to(HW.resolve()) or not path.is_file():
            raise ValueError("H3 evidence path is outside hardware or missing")
        if path in active:
            raise ValueError("cyclic H3 source evidence")
        raw = path.read_bytes()
        actual_digest = hashlib.sha256(raw).hexdigest()
        if path in snapshot and snapshot[path] != actual_digest:
            raise ValueError("H3 source changed on repeated visit")
        snapshot[path] = actual_digest
        data = json.loads(raw)
        artifact = data.get("artifact")
        if expected_artifact is not None and artifact != expected_artifact:
            raise ValueError("unexpected H3 artifact identity")
        if path in visited:
            return data
        active.add(path)
        if artifact in owner.REQUIREMENTS:
            if artifact in proof_paths and proof_paths[artifact] != path:
                raise ValueError("duplicate H3 artifact identity at distinct paths")
            proof_paths[artifact] = path
            proof = data.get("current_power_scope")
            if not isinstance(proof, dict):
                raise ValueError("H3 current applicability proof is missing")
            field = next((key for key in ("source_sha256", "source_hashes", "sources") if key in data), "source_sha256")
            bindings = data.get(field)
            if (not isinstance(bindings, dict) or bindings != proof.get("source_sha256")
                    or not owner.required_sources(artifact).issubset(bindings)):
                raise ValueError("H3 required source scope is incomplete")
            applicability = proof.get("applicability_checks")
            if not isinstance(applicability, dict):
                raise ValueError("H3 applicability check scope is missing")
            expected = owner._proof(artifact, proof.get("numerical_checks_pass"), applicability)
            expected["source_sha256"] = bindings
            if json.dumps(proof, sort_keys=True) != json.dumps(expected, sort_keys=True):
                raise ValueError("H3 applicability proof is inconsistent")
            if (data.get("status") != expected["status"]
                    or data.get("current_analytical_scope_complete") is not expected["current_analytical_scope_complete"]
                    or data.get("open_analytical_findings") != expected["open_findings"]
                    or data.get("production_release_authorized") is not False
                    or data.get("battery_energization_authorized") is not False
                    or not data.get("authorization")
                    or not all(value is False for value in data["authorization"].values())):
                raise ValueError("H3 closure/authorization contradicts current proof")
            if expected["status"] == "pass" and not owner.admits_current(data, artifact):
                raise ValueError("H3 analytical PASS is not admitted")
            if data.get("errors") != data.get("provisional_numerical_errors", []) + expected["open_findings"]:
                raise ValueError("H3 numerical findings were hidden or changed")
            proofs[artifact] = {
                "status": expected["status"],
                "numerical_status": expected["numerical_status"],
                "open_findings": expected["open_findings"],
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        else:
            bindings = next((data[key] for key in ("source_sha256", "source_hashes") if key in data), {})
        if not isinstance(bindings, dict):
            raise ValueError("H3 source bindings must be a map")
        for relative, digest in bindings.items():
            dependency = HW / relative
            if (Path(relative).is_absolute() or ".." in Path(relative).parts
                    or not dependency.resolve().is_relative_to(HW.resolve())
                    or not dependency.is_file()
                    or hashlib.sha256(dependency.read_bytes()).hexdigest() != digest):
                raise ValueError("stale or invalid H3 dependency: " + relative)
            resolved = dependency.resolve()
            if resolved in snapshot and snapshot[resolved] != digest:
                raise ValueError("H3 source changed between consumers")
            snapshot[resolved] = digest
            if dependency.suffix == ".json":
                child = json.loads(dependency.read_text())
                child_identity = canonical_artifacts.get(dependency.resolve())
                if child_identity is not None or (isinstance(child, dict) and str(child.get("artifact", "")).startswith("H3-")):
                    visit(dependency, child_identity)
        active.remove(path)
        visited.add(path)
        return data

    for path, artifact in sources:
        visit(path, artifact)
    if any(not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest
           for path, digest in snapshot.items()):
        raise ValueError("H3 inputs changed during import")
    complete = bool(proofs) and all(row["status"] == "pass" for row in proofs.values())
    return {
        "schema_version": 1,
        "status": "analytical_scope_imported" if complete else "review_required",
        "current_analytical_scope_complete": complete,
        "artifacts": dict(sorted(proofs.items())),
        "source_files_checked": len(visited),
        "production_release_authorized": False,
        "battery_energization_authorized": False,
        "target_execution_authorized": False,
        "_verified_input_snapshot": {str(path): digest for path, digest in snapshot.items()},
    }


def bind_scope(result, scope):
    scope = dict(scope)
    snapshot = scope.pop("_verified_input_snapshot")
    if any(not Path(path).is_file() or hashlib.sha256(Path(path).read_bytes()).hexdigest() != digest
           for path, digest in snapshot.items()):
        raise ValueError("H3 sources changed after inspection; discard this import")
    result["status"] = scope["status"]
    result["current_hardware_substep"] = "H6.0.3-R1"
    result["current_power_scope"] = scope
    result["evidence_status"] = "provisional" if not scope["current_analytical_scope_complete"] else "analytical_only"
    result["claims"].update(
        current_h3_analytical_scope_complete=scope["current_analytical_scope_complete"],
        target_implementation_or_execution_proven=False,
        production_release_authorized=False,
        battery_energization_authorized=False,
        target_execution_authorized=False,
    )
    if "h3_r2_analytical_scope_imported" in result["claims"]:
        result["claims"]["h3_r2_analytical_scope_imported"] = scope["current_analytical_scope_complete"]
    result["scope_boundary"] = (
        "Retained timing, envelopes and invariants describe requirements and provisional comparisons. "
        "They do not qualify the fitted power cell, authorize RUN/TX or close a hardware phase."
    )
    return result
