from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.tape_priority_inference_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📈",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.tape_priority_inference_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "tape", "priority", "loom"],
    "description": "Package Loom tape priority inference from text and base score into a clamped urgency-weighted priority.",
}


def build_tape_priority_inference_packet(text: str, base: float, priority: float) -> dict[str, Any]:
    return {
        "text": str(text),
        "base": float(base),
        "priority": float(priority),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_tape_priority_inference_packet(
        text=str(payload.get("text") or ""),
        base=float(payload.get("base") or 0.0),
        priority=float(payload.get("priority") or 0.0),
    )
    output_packet = {
        "packet_type": "math.interpretation_response.v1",
        "packet_version": "math.interpretation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "tape-priority-inference-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built tape priority-inference packet.",
        "refs": [],
        "data": {
            "base": value.get("base", 0.0),
            "priority": value.get("priority", 0.0),
        },
    }]
