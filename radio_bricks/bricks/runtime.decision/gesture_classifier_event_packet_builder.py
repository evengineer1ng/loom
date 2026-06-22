from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.gesture_classifier_event_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⚡",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.gesture_classifier_event_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "classifier", "gesture", "event"],
    "description": "Package a fired gesture-classifier event with label and confidence for downstream runtime routing.",
}


def build_gesture_classifier_event_packet(label: str, confidence: float) -> dict[str, Any]:
    return {
        "label": str(label),
        "confidence": float(confidence),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_gesture_classifier_event_packet(
        label=str(payload.get("label") or ""),
        confidence=float(payload.get("confidence") or 0.0),
    )
    output_packet = {
        "packet_type": "runtime.decision_response.v1",
        "packet_version": "runtime.decision_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "gesture-classifier-event-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built gesture-classifier event packet.",
        "refs": [],
        "data": {
            "label": value.get("label", ""),
            "confidence": value.get("confidence", 0.0),
        },
    }]
