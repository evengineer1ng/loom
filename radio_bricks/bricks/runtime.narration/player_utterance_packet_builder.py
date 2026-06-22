from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.player_utterance_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗣️",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.player_utterance_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "player", "utterance", "speech"],
    "description": "Package a transcribed player utterance with source, event type, priority, and cleaned text for conversational reply systems.",
}


def build_player_utterance_packet(
    source: str,
    event_type: str,
    priority: float,
    text: str,
) -> dict[str, Any]:
    return {
        "source": str(source),
        "event_type": str(event_type),
        "priority": float(priority),
        "text": str(text),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_player_utterance_packet(
        source=str(payload.get("source") or ""),
        event_type=str(payload.get("event_type") or ""),
        priority=float(payload.get("priority") or 0.0),
        text=str(payload.get("text") or ""),
    )
    output_packet = {
        "packet_type": "runtime.narration_response.v1",
        "packet_version": "runtime.narration_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "player-utterance-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built player utterance packet.",
        "refs": [],
        "data": {
            "source": value.get("source", ""),
            "event_type": value.get("event_type", ""),
            "priority": value.get("priority", 0.0),
        },
    }]
