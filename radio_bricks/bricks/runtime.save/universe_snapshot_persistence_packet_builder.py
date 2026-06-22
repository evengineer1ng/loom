from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.universe_snapshot_persistence_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "💾",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.universe_snapshot_persistence_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "snapshot", "persist", "json"],
    "description": "Package the persistence of all authoritative universe layers into one JSON snapshot document suitable for exact round-trips.",
}


def build_universe_snapshot_persistence_packet(
    universe_id: str,
    snapshot_digest: str,
    path_hint: str,
    included_layers: list[str] | None,
    snapshot_counts: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "universe_id": str(universe_id),
        "snapshot_digest": str(snapshot_digest),
        "path_hint": str(path_hint),
        "included_layers": [str(item) for item in (included_layers or [])],
        "snapshot_counts": dict(snapshot_counts or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_universe_snapshot_persistence_packet(
        universe_id=str(payload.get("universe_id") or ""),
        snapshot_digest=str(payload.get("snapshot_digest") or ""),
        path_hint=str(payload.get("path_hint") or ""),
        included_layers=list(payload.get("included_layers") or []),
        snapshot_counts=dict(payload.get("snapshot_counts") or {}),
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
        "receipt_id": "universe-snapshot-persistence-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built universe-snapshot persistence packet.",
        "refs": [],
        "data": {
            "universe_id": value.get("universe_id", ""),
            "layer_count": len(value.get("included_layers", [])),
            "snapshot_digest": value.get("snapshot_digest", ""),
        },
    }]
