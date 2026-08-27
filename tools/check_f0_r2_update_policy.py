#!/usr/bin/env python3
"""Check the reviewed six-target bundle activation and compensation policy."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "update_policy.json"
MEMORY_PATH = ROOT / "config" / "f0_r2_memory_rollback_contract.json"


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    memory = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    expected_order = ["pack", "safety", "c5", "rf_rp", "hub_rp", "s3"]
    memory_ids = {row["id"] for row in memory.get("targets", [])}

    if policy.get("stage") != "F0-R2.3" or policy.get("status") != "reviewed_contract":
        return fail("update policy is not reviewed at F0-R2.3")
    if policy.get("application_targets") != expected_order or set(expected_order) != memory_ids:
        return fail("update policy is not target-complete for the six memory owners")
    if policy.get("pending_boot_order") != expected_order:
        return fail("pending boot order changed")
    if policy.get("commit_order") != expected_order:
        return fail("commit order changed")
    if policy.get("coordinator", {}).get("target") != "s3":
        return fail("S3 is not the bundle coordinator")
    if not policy.get("coordinator", {}).get("journal", "").startswith("duplicated power-loss-safe"):
        return fail("bundle transaction journal is not power-loss-safe and duplicated")

    required_manifest = {
        "product_id", "bundle_id", "previous_bundle_id", "hardware_revision_range",
        "target_id", "image_length", "image_sha256", "build_id",
        "protocol_compatibility", "transition_compatibility",
        "minimum_power_policy", "signing_key_id",
    }
    if set(policy.get("manifest_required_fields", [])) != required_manifest:
        return fail("target or transition binding disappeared from the manifest")
    signature = policy.get("signature_contract", {})
    if signature.get("algorithm") != "ECDSA P-256 over SHA-256":
        return fail("reviewed package signature algorithm changed")
    if signature.get("accepted_roots") != ["release", "locally_enrolled_owner"]:
        return fail("owner-open trust roots changed")
    if signature.get("irreversible_secure_boot_or_debug_lock_default") is not False:
        return fail("irreversible lock became the default")

    preconditions = " ".join(policy.get("preconditions", [])).lower()
    for token in ("run is in kill", "actual-tx", "qualified usb", "all six", "transition_compatibility"):
        if token not in preconditions:
            return fail(f"missing update precondition: {token}")
    if len(policy.get("staging", [])) != 5 or "before any pending boot" not in " ".join(policy["staging"]):
        return fail("all-slot staging before activation is no longer explicit")
    if "commits itself last" not in policy.get("commit_rule", ""):
        return fail("S3-last global commit rule disappeared")

    deadline = policy.get("deadline", {})
    if deadline.get("rp2350_tbyb_window_ms") != 16700:
        return fail("RP2350 TBYB window changed")
    if deadline.get("starts_at") != "RF RP pending boot":
        return fail("the bounded activation window starts too early or too late")
    if deadline.get("measured_budget_required") is not True or deadline.get("qualified_budget_ms") is not None:
        return fail("unmeasured activation timing is being presented as qualified")

    failures = policy.get("failure_policy", {})
    if set(failures) != {"before_any_commit", "during_commit", "hub_loss", "s3_loss", "unrecoverable_target"}:
        return fail("a bundle failure interval lost its recovery policy")
    if "bridge bundle" not in policy.get("bridge_rule", ""):
        return fail("breaking IPC upgrades no longer require an intermediate bridge")
    if policy.get("open_recovery", {}).get("irreversible_secure_boot_or_debug_lock_default") is not False:
        return fail("physical owner recovery became irreversibly locked")

    expected_claims = {
        "six_target_activation_order_reviewed": True,
        "six_target_commit_order_reviewed": True,
        "power_loss_resume_and_compensation_reviewed": True,
        "transition_bridge_rule_reviewed": True,
        "r2_target_builds_run": False,
        "target_flash_transitions_run": 0,
        "qualified_activation_budget_measured": False,
        "production_signature_verifier_fit_proven": False,
    }
    if policy.get("claims") != expected_claims:
        return fail("F0-R2.3 claims changed or overstate execution evidence")

    print(
        "F0-R2.3 update policy OK: 6 staged/pending/commit targets, S3 last, "
        "bridge rule present; 0 flash transitions and 0 qualified timing claims"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
