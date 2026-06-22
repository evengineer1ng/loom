from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "music.flow.narrator_ducking_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎙️",
    "deterministic": True,
    "inputs": ["music.flow_request.v1"],
    "outputs": ["music.flow_response.v1"],
    "requires": [],
    "provides": ["music.narrator_ducking_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["music", "flow", "narrator", "ducking", "bridge"],
    "description": "Package narrator-ducking bridge state with active flag, duck start time, and delayed music restore cadence.",
}


def build_narrator_ducking_packet(
    is_narrator_active: bool,
    duck_start_time: float,
    restore_delay: float,
    should_restore_music: bool,
) -> dict[str, Any]:
    return {
        "is_narrator_active": bool(is_narrator_active),
        "duck_start_time": float(duck_start_time),
        "restore_delay": float(restore_delay),
        "should_restore_music": bool(should_restore_music),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_narrator_ducking_packet(
        is_narrator_active=bool(payload.get("is_narrator_active")),
        duck_start_time=float(payload.get("duck_start_time") or 0.0),
        restore_delay=float(payload.get("restore_delay") or 0.0),
        should_restore_music=bool(payload.get("should_restore_music")),
    )
    output_packet = {
        "packet_type": "music.flow_response.v1",
        "packet_version": "music.flow_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "narrator-ducking-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built narrator-ducking packet.",
        "refs": [],
        "data": {
            "is_narrator_active": value.get("is_narrator_active", False),
            "restore_delay": value.get("restore_delay", 0.0),
        },
    }]
