from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.tape_valence_inference_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎭",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.tape_valence_inference_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "tape", "valence", "loom"],
    "description": "Package Loom tape valence inference from text into alarm, hype, or calm classification.",
}


def build_tape_valence_inference_packet(text: str, valence: str) -> dict[str, Any]:
    return {
        "text": str(text),
        "valence": str(valence),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_tape_valence_inference_packet(
        text=str(payload.get("text") or ""),
        valence=str(payload.get("valence") or ""),
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
        "receipt_id": "tape-valence-inference-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built tape valence-inference packet.",
        "refs": [],
        "data": {
            "valence": value.get("valence", ""),
        },
    }]
