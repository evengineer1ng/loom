from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.universe_snapshot_restore_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "♻️",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.universe_snapshot_restore_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "snapshot", "restore", "determinism"],
    "description": "Package the exact restore of authoritative universe state from a persisted snapshot, including counters, ledgers, memory, and deterministic continuation fields.",
}


def build_universe_snapshot_restore_packet(
    universe_id: str,
    canonical_seed: str,
    snapshot_digest: str,
    restored_time: dict[str, Any] | None,
    restored_counts: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "universe_id": str(universe_id),
        "canonical_seed": str(canonical_seed),
        "snapshot_digest": str(snapshot_digest),
        "restored_time": dict(restored_time or {}),
        "restored_counts": dict(restored_counts or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_universe_snapshot_restore_packet(
        universe_id=str(payload.get("universe_id") or ""),
        canonical_seed=str(payload.get("canonical_seed") or ""),
        snapshot_digest=str(payload.get("snapshot_digest") or ""),
        restored_time=dict(payload.get("restored_time") or {}),
        restored_counts=dict(payload.get("restored_counts") or {}),
    )
    output_packet = {
        "packet_type": "runtime.save_response.v1",
        "packet_version": "runtime.save_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "universe-snapshot-restore-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built universe-snapshot restore packet.",
        "refs": [],
        "data": {
            "universe_id": value.get("universe_id", ""),
            "snapshot_digest": value.get("snapshot_digest", ""),
            "restored_groups": len(value.get("restored_counts", {})),
        },
    }]
