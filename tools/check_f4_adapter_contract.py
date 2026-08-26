#!/usr/bin/env python3
"""Fail-closed review of the F4.0.1 transport-adapter contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "config" / "f4_0_1_adapter_contract.json"
PROTOCOL_PATH = REPO_ROOT / "config" / "interdomain_protocol.json"
CAPABILITY_PATH = REPO_ROOT / "config" / "f4_0_transport_capability_matrix.json"
S3_CMAKE_PATH = REPO_ROOT / "targets" / "s3" / "CMakeLists.txt"


def canonical_component_payload(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    with zipfile.ZipFile(path) as archive:
        files = sorted(
            (entry for entry in archive.infolist() if not entry.is_dir()),
            key=lambda entry: entry.filename,
        )
        for entry in files:
            name = entry.filename.encode("utf-8")
            content = archive.read(entry)
            digest.update(struct.pack("<I", len(name)))
            digest.update(name)
            digest.update(struct.pack("<Q", len(content)))
            digest.update(hashlib.sha256(content).digest())
    return len(files), digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--essl-archive",
        type=Path,
        help="also verify a downloaded Registry ZIP against the normalized lock",
    )
    args = parser.parse_args()

    errors: list[str] = []
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    capability = json.loads(CAPABILITY_PATH.read_text(encoding="utf-8"))

    if contract.get("stage") != "F4.0.1" or contract.get("status") != "reviewed":
        errors.append("F4.0.1 adapter contract is not reviewed")
    if contract.get("inputs") != [
        "config/interdomain_protocol.json",
        "config/f4_0_transport_capability_matrix.json",
    ]:
        errors.append("F4.0.1 input set changed")

    dependency = contract.get("essl_dependency_lock", {})
    selected = capability.get("dependency_decision", {})
    if dependency.get("component") != selected.get("component"):
        errors.append("ESSL component differs from F4.0.0")
    if dependency.get("version") != selected.get("selected_exact_version"):
        errors.append("ESSL exact version differs from F4.0.0")
    if dependency.get("floating_constraint_allowed"):
        errors.append("floating ESSL dependency is forbidden")
    if dependency.get("repository_commit") != "a93734f00aef26d6e8a3132bc20de869c75426f5":
        errors.append("ESSL upstream commit lock changed")
    if dependency.get("registry_object_id") != "dedb3ae6-e261-489e-8109-ff5445fec9a1":
        errors.append("ESSL Registry object lock changed")
    if dependency.get("file_count") != 30:
        errors.append("ESSL normalized file count changed")
    expected_payload_hash = "9f217846a90d97a4897350b0c8cfafd4bbe1a2dd8af5619fd3463ea9dbe36053"
    if dependency.get("canonical_payload_hash", {}).get("sha256") != expected_payload_hash:
        errors.append("ESSL normalized payload hash changed")
    observation = dependency.get("registry_archive_observation", {})
    if observation.get("raw_zip_is_reproducible") is not False:
        errors.append("dynamic Registry ZIP must not be treated as reproducible")
    if len(set(observation.get("observed_raw_sha256", []))) < 2:
        errors.append("ESSL dynamic-archive evidence is incomplete")
    if 'set(ENV{IDF_COMPONENT_MANAGER} "0")' not in S3_CMAKE_PATH.read_text(encoding="utf-8"):
        errors.append("S3 build no longer enforces offline component resolution")
    if args.essl_archive is not None:
        try:
            file_count, payload_hash = canonical_component_payload(args.essl_archive)
        except (OSError, zipfile.BadZipFile) as exc:
            errors.append(f"cannot inspect ESSL archive: {exc}")
        else:
            if file_count != dependency.get("file_count"):
                errors.append("downloaded ESSL file count differs from lock")
            if payload_hash != expected_payload_hash:
                errors.append("downloaded ESSL payload differs from lock")

    lifecycle = contract.get("common_lifecycle", {})
    states = lifecycle.get("states", [])
    expected_states = {
        "DOWN", "STARTING", "NEGOTIATING", "READY", "QUIESCING", "FAULTED", "RESETTING"
    }
    if len(states) != len(set(states)) or set(states) != expected_states:
        errors.append("adapter lifecycle state set changed")
    transitions = lifecycle.get("allowed_transitions", {})
    if set(transitions) != expected_states:
        errors.append("adapter transitions do not cover every lifecycle state")
    for source, destinations in transitions.items():
        if not set(destinations).issubset(expected_states):
            errors.append(f"{source} has an unknown lifecycle destination")
    if any("READY" in transitions.get(state, []) for state in expected_states - {"NEGOTIATING"}):
        errors.append("READY must be reachable only through NEGOTIATING")
    if set(lifecycle.get("side_effect_closed_states", [])) != expected_states - {"READY"}:
        errors.append("every non-READY lifecycle state must close side effects")

    high_speed = contract.get("high_speed_adapters", {})
    if set(high_speed.get("transports", [])) != {"S3_C5", "S3_RP"}:
        errors.append("high-speed transport set changed")
    protocol_transports = {row["id"]: row for row in protocol["transports"]}
    for transport_id in high_speed.get("transports", []):
        row = protocol_transports[transport_id]
        if high_speed.get("cell_bytes") != row["maximum_transfer_bytes"]:
            errors.append(f"{transport_id} cell size differs from L2IP")
        if high_speed.get("payload_bytes_max") != row["maximum_payload_bytes"]:
            errors.append(f"{transport_id} payload size differs from L2IP")

    pool = high_speed.get("per_direction_pool", {})
    classes = {row["priority"]: row for row in pool.get("classes", [])}
    expected_buffers = {0: 4, 1: 8, 2: 8, 3: 4, 4: 8}
    if {key: row["buffers"] for key, row in classes.items()} != expected_buffers:
        errors.append("high-speed queue reservations changed")
    if pool.get("buffers") != sum(expected_buffers.values()):
        errors.append("high-speed pool total does not match queue reservations")
    if pool.get("bytes") != pool.get("buffers", 0) * high_speed.get("cell_bytes", 0):
        errors.append("high-speed pool byte count is inconsistent")
    if pool.get("borrowing_allowed"):
        errors.append("priority queue borrowing must remain forbidden")
    protocol_priorities = {row["id"]: row for row in protocol["scheduling"]["priorities"]}
    for priority in (0, 1, 2):
        if classes.get(priority, {}).get("buffers") != protocol_priorities[priority]["reserved_frames_each_direction"]:
            errors.append(f"priority {priority} reservation differs from L2IP")
    if "drop oldest" not in classes.get(3, {}).get("overflow", ""):
        errors.append("telemetry must preserve newest data on overflow")
    if "receiver credit" not in classes.get(4, {}).get("overflow", ""):
        errors.append("bulk overflow must stop on receiver credit")

    tx = high_speed.get("tx_buffer_ownership", {})
    rx = high_speed.get("rx_buffer_ownership", {})
    if tx.get("normal_cycle") != ["FREE", "APP_OWNED", "QUEUED", "PHY_OWNED", "FREE"]:
        errors.append("TX ownership cycle changed")
    if rx.get("normal_cycle") != ["FREE", "PHY_OWNED", "VALIDATING", "DISPATCHED", "FREE"]:
        errors.append("RX ownership cycle changed")
    if rx.get("invalid_cycle") != ["FREE", "PHY_OWNED", "VALIDATING", "FREE"]:
        errors.append("invalid RX ownership cycle changed")

    credit = high_speed.get("bulk_credit", {})
    if credit.get("initial_granted_total") != 0 or credit.get("initial_consumed_total") != 0:
        errors.append("bulk-credit counters must reset to zero")
    if credit.get("maximum_outstanding") != classes.get(4, {}).get("buffers"):
        errors.append("bulk-credit reset or maximum changed")
    if credit.get("counter_width_bits") != 32:
        errors.append("bulk-credit counter width changed")
    if "before" not in credit.get("consume_rule", "") or "FREE" not in credit.get("replenish_rule", ""):
        errors.append("bulk-credit ownership ordering is incomplete")
    if "granted_total minus locally consumed_total" not in credit.get("update_rule", ""):
        errors.append("bulk credit must remain duplicate-safe with cells in flight")
    if "do not wrap" not in credit.get("wrap_rule", ""):
        errors.append("bulk-credit wrap boundary is missing")

    duplicates = high_speed.get("duplicate_and_result_policy", {})
    if duplicates.get("maximum_outstanding_side_effect_requests") != 8:
        errors.append("side-effect pending bound changed")
    if duplicates.get("typed_result_cache_entries_per_direction") != 8:
        errors.append("typed result-cache bound changed")
    if "never execute" not in duplicates.get("stale_or_evicted", ""):
        errors.append("stale side effects are not fail-closed")
    deadline = high_speed.get("deadline_policy", {})
    if deadline.get("start") != "complete validated receipt of the request":
        errors.append("deadline origin changed")
    if "never restart or extend" not in deadline.get("queue_rule", ""):
        errors.append("retry may incorrectly extend a deadline")
    liveness = high_speed.get("liveness", {})
    timing = protocol["safety_timing"]
    if liveness.get("ping_period_ms") != timing["heartbeat_period_ms"]:
        errors.append("high-speed liveness period differs from safety cadence")
    if liveness.get("valid_pong_gap_ms_max") != timing["heartbeat_gap_ms_max"]:
        errors.append("high-speed liveness gap differs from reviewed bound")
    if liveness.get("missed_periods_max") * liveness.get("ping_period_ms") != liveness.get("valid_pong_gap_ms_max"):
        errors.append("high-speed missed-period bound is inconsistent")

    mailbox = contract.get("mailbox_adapters", {})
    mailbox_rows = {row["id"]: row for row in mailbox.get("transports", [])}
    if set(mailbox_rows) != {"S3_PACK", "S3_SAFETY"}:
        errors.append("mailbox transport set changed")
    protocol_addresses = {"S3_PACK": "0x2A", "S3_SAFETY": "0x2B"}
    for transport_id, address in protocol_addresses.items():
        if mailbox_rows.get(transport_id, {}).get("address_7bit") != address:
            errors.append(f"{transport_id} mailbox address changed")
    protocol_mailbox = protocol["i2c_mailbox"]
    for field in ("command_bytes", "status_bytes", "update_window_bytes"):
        if mailbox.get(field) != protocol_mailbox[field]:
            errors.append(f"mailbox {field} differs from L2IP")
    if mailbox_rows.get("S3_SAFETY", {}).get("heartbeat_gap_ms_max") != timing["heartbeat_gap_ms_max"]:
        errors.append("SAFETY mailbox heartbeat gap changed")
    if "at most one" not in mailbox.get("command_ownership", ""):
        errors.append("mailbox command ownership is not bounded")
    if "exactly one" not in mailbox.get("update_credit", ""):
        errors.append("mailbox update credit is not bounded")

    actions = {row["transport"]: row for row in contract.get("link_loss_actions", [])}
    expected_transports = set(protocol_transports)
    if set(actions) != expected_transports:
        errors.append("link-loss actions do not cover all production transports")
    if "100 ms" not in actions.get("S3_C5", {}).get("required_action", ""):
        errors.append("C5 owner-local lease bound is missing")
    if "100 ms" not in actions.get("S3_RP", {}).get("required_action", ""):
        errors.append("RP owner-local lease bound is missing")
    if "cannot admit" not in actions.get("S3_PACK", {}).get("required_action", ""):
        errors.append("PACK link-loss authority is unclear")
    if "FAULT_KILL" not in actions.get("S3_SAFETY", {}).get("required_action", ""):
        errors.append("SAFETY link-loss action is not fail-closed")

    counts = contract.get("counts", {})
    expected_counts = {
        "production_transports": 4,
        "lifecycle_states": 7,
        "high_speed_buffers_each_direction": 32,
        "high_speed_bytes_each_direction": 16384,
        "protected_queue_buffers_each_direction": 20,
        "physical_transport_runs": 0,
    }
    if counts != expected_counts:
        errors.append("F4.0.1 reviewed counts changed")
    if contract.get("next") != "F4.0.2":
        errors.append("F4.0.1 next marker changed")
    if any(contract.get("authorization", {}).values()):
        errors.append("F4.0.1 may not authorize hardware work")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    archive_note = " plus verified ESSL archive" if args.essl_archive else ""
    print(
        "F4.0.1 adapter contract OK: 7 states, 4 transports, "
        "32 buffers/direction, 0 physical runs" + archive_note
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
