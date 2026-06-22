from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.secret.knower_dialogue_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📡",
    "deterministic": True,
    "inputs": ["narrative.secret_request.v1"],
    "outputs": ["narrative.secret_response.v1"],
    "requires": [],
    "provides": ["narrative.knower_dialogue_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "secret", "knower", "dialogue", "fragment"],
    "description": "Package an unlocked Hidden Knower dialogue fragment with pagination and render context hints.",
}


def build_knower_dialogue_packet(
    name: str,
    archetype: str,
    fragment_index: int,
    fragment: str,
    total_fragments: int,
    context: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "name": name,
        "archetype": archetype,
        "fragment_index": int(fragment_index),
        "fragment": fragment,
        "total_fragments": int(total_fragments),
        "context": dict(context or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_knower_dialogue_packet(
        name=str(payload.get("name") or ""),
        archetype=str(payload.get("archetype") or ""),
        fragment_index=int(payload.get("fragment_index") or 0),
        fragment=str(payload.get("fragment") or ""),
        total_fragments=int(payload.get("total_fragments") or 0),
        context=dict(payload.get("context") or {}),
    )
    output_packet = {
        "packet_type": "narrative.secret_response.v1",
        "packet_version": "narrative.secret_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "knower-dialogue-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Hidden Knower dialogue packet.",
        "refs": [],
        "data": {"name": value.get("name", ""), "fragment_index": value.get("fragment_index", 0)},
    }]
