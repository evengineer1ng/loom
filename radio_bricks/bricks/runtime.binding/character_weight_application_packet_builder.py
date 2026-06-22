from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.character_weight_application_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎚️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.character_weight_application_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "character", "weight", "selection"],
    "description": "Package application of character slider weights to base selection scores for voice balancing.",
}


def build_character_weight_application_packet(
    base_scores: dict[str, Any] | None,
    weights: dict[str, Any] | None,
    adjusted_scores: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "base_scores": dict(base_scores or {}),
        "weights": dict(weights or {}),
        "adjusted_scores": dict(adjusted_scores or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_character_weight_application_packet(
        base_scores=dict(payload.get("base_scores") or {}),
        weights=dict(payload.get("weights") or {}),
        adjusted_scores=dict(payload.get("adjusted_scores") or {}),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "character-weight-application-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built character-weight application packet.",
        "refs": [],
        "data": {
            "base_count": len(value.get("base_scores", {})),
            "weight_count": len(value.get("weights", {})),
            "adjusted_count": len(value.get("adjusted_scores", {})),
        },
    }]
