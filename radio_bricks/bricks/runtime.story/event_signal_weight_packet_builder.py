from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.event_signal_weight_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⚖️",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.event_signal_weight_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "event", "signal", "weight"],
    "description": "Package narrative signal weight for an event, including base weight, adjustment reason, and final evidence score.",
}


def build_event_signal_weight_packet(
    event_type: str,
    base_weight: float,
    adjustment: float,
    final_weight: float,
    reason: str,
) -> dict[str, Any]:
    return {
        "event_type": str(event_type),
        "base_weight": float(base_weight),
        "adjustment": float(adjustment),
        "final_weight": float(final_weight),
        "reason": str(reason),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_event_signal_weight_packet(
        event_type=str(payload.get("event_type") or ""),
        base_weight=float(payload.get("base_weight") or 0.0),
        adjustment=float(payload.get("adjustment") or 0.0),
        final_weight=float(payload.get("final_weight") or 0.0),
        reason=str(payload.get("reason") or ""),
    )
    output_packet = {
        "packet_type": "runtime.story_response.v1",
        "packet_version": "runtime.story_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "event-signal-weight-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built event signal-weight packet.",
        "refs": [],
        "data": {
            "event_type": value.get("event_type", ""),
            "final_weight": value.get("final_weight", 0.0),
        },
    }]
