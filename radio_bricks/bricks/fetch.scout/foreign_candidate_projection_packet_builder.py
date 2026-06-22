from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.scout.foreign_candidate_projection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📡",
    "deterministic": True,
    "inputs": ["fetch.scout_request.v1"],
    "outputs": ["fetch.scout_response.v1"],
    "requires": [],
    "provides": ["fetch.foreign_candidate_projection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "scout", "candidate", "projection", "foreign-json"],
    "description": "Package projection of a foreign JSON item into a normalized Radio-OS candidate with id, title, body, priority, timestamp, and tags.",
}


def build_foreign_candidate_projection_packet(
    source: str,
    field_map: dict[str, Any] | None,
    raw_item: dict[str, Any] | None,
    candidate: dict[str, Any] | None,
    default_priority: float,
) -> dict[str, Any]:
    return {
        "source": str(source),
        "field_map": dict(field_map or {}),
        "raw_item": dict(raw_item or {}),
        "candidate": dict(candidate or {}),
        "default_priority": float(default_priority),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_foreign_candidate_projection_packet(
        source=str(payload.get("source") or ""),
        field_map=dict(payload.get("field_map") or {}),
        raw_item=dict(payload.get("raw_item") or {}),
        candidate=dict(payload.get("candidate") or {}),
        default_priority=float(payload.get("default_priority") or 0.0),
    )
    output_packet = {
        "packet_type": "fetch.scout_response.v1",
        "packet_version": "fetch.scout_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "foreign-candidate-projection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built foreign-candidate projection packet.",
        "refs": [],
        "data": {
            "source": value.get("source", ""),
            "candidate_id": dict(value.get("candidate") or {}).get("post_id", ""),
            "field_map_size": len(value.get("field_map", {})),
        },
    }]
