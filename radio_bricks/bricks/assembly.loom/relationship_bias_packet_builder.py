from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.relationship_bias_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "💞",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.relationship_bias_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "forkuniverse", "relationship", "bias"],
    "description": "Package concept-derived relationship-axis biases such as affection, trust, dependency, resentment, attraction, loyalty, fear, and history depth.",
}


def build_relationship_bias_packet(axes: dict[str, float] | None) -> dict[str, Any]:
    return {"axes": {str(key): float(value) for key, value in (axes or {}).items()}}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_relationship_bias_packet(axes=dict(payload.get("axes") or {}))
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
        "receipt_id": "relationship-bias-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built relationship-bias packet.",
        "refs": [],
        "data": {"axis_count": len(value.get("axes", {}))},
    }]
