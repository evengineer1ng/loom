from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.coherence.material_state_classifier",
    "kind": "evaluator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["world.coherence_request.v1"],
    "outputs": ["world.coherence_response.v1"],
    "requires": [],
    "provides": ["world.material_state"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "coherence", "material", "classifier"],
    "description": "Classify the macro material condition of a kingdom from food, infrastructure, and trade.",
}


def classify_material_state(food_stores: float, infrastructure: float, trade_volume: float) -> str:
    if float(food_stores) > 60 and float(infrastructure) > 50 and float(trade_volume) > 40:
        return "THRIVING"
    if float(food_stores) > 30 and float(infrastructure) > 25:
        return "FUNCTIONAL"
    if float(food_stores) > 10 or float(infrastructure) > 10:
        return "STRAINED"
    return "COLLAPSED"


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {
        "material_state": classify_material_state(
            food_stores=float(payload.get("food_stores") or 0.0),
            infrastructure=float(payload.get("infrastructure") or 0.0),
            trade_volume=float(payload.get("trade_volume") or 0.0),
        )
    }
    output_packet = {
        "packet_type": "world.coherence_response.v1",
        "packet_version": "world.coherence_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "material-state",
        "brick_id": CONCEPT["id"],
        "kind": "evaluate",
        "label": "Classified material state.",
        "refs": [],
        "data": {"material_state": value.get("material_state", "UNKNOWN")},
    }]
