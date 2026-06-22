from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.relationship_generation_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔗",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.relationship_generation_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "forkuniverse", "relationship", "generation"],
    "description": "Package the generated relationship rows with seeded pairings, axis values, and concept tags.",
}


def build_relationship_generation_packet(
    brief_seed: str,
    relationship_count: int,
    relationships: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "brief_seed": brief_seed,
        "relationship_count": int(relationship_count),
        "relationships": [dict(item) for item in (relationships or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_relationship_generation_packet(
        brief_seed=str(payload.get("brief_seed") or ""),
        relationship_count=int(payload.get("relationship_count") or 0),
        relationships=list(payload.get("relationships") or []),
    )
    output_packet = {
        "packet_type": "assembly.loom_response.v1",
        "packet_version": "assembly.loom_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "relationship-generation-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built relationship-generation packet.",
        "refs": [],
        "data": {"relationship_count": value.get("relationship_count", 0), "row_count": len(value.get("relationships", []))},
    }]
