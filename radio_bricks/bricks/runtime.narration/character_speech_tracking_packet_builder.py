from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.character_speech_tracking_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗣️",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.character_speech_tracking_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "character", "speech", "tracking"],
    "description": "Package character speech tracking with utterance-count updates, rolling recent history, and canonicalized character keys.",
}


def build_character_speech_tracking_packet(
    character: str,
    canonical_key: str,
    utterance_count: int,
    history_depth: int,
    recent_history: list[str] | None,
) -> dict[str, Any]:
    return {
        "character": str(character),
        "canonical_key": str(canonical_key),
        "utterance_count": int(utterance_count),
        "history_depth": int(history_depth),
        "recent_history": [str(item) for item in (recent_history or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_character_speech_tracking_packet(
        character=str(payload.get("character") or ""),
        canonical_key=str(payload.get("canonical_key") or ""),
        utterance_count=int(payload.get("utterance_count") or 0),
        history_depth=int(payload.get("history_depth") or 0),
        recent_history=list(payload.get("recent_history") or []),
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
        "receipt_id": "character-speech-tracking-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built character-speech tracking packet.",
        "refs": [],
        "data": {
            "canonical_key": value.get("canonical_key", ""),
            "utterance_count": value.get("utterance_count", 0),
            "history_depth": value.get("history_depth", 0),
        },
    }]
