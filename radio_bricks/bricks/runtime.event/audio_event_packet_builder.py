from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.event.audio_event_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔊",
    "deterministic": True,
    "inputs": ["runtime.event_request.v1"],
    "outputs": ["runtime.event_response.v1"],
    "requires": [],
    "provides": ["runtime.audio_event_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "event", "audio", "playback", "routing"],
    "description": "Package an audio event with type, file path, gain/fade controls, loop flag, priority, and metadata payload.",
}


def build_audio_event_packet(
    audio_type: str,
    file_path: str,
    volume: float,
    fade_in: float,
    fade_out: float,
    loop: bool,
    priority: int,
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "audio_type": str(audio_type),
        "file_path": str(file_path),
        "volume": float(volume),
        "fade_in": float(fade_in),
        "fade_out": float(fade_out),
        "loop": bool(loop),
        "priority": int(priority),
        "metadata": dict(metadata or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_audio_event_packet(
        audio_type=str(payload.get("audio_type") or ""),
        file_path=str(payload.get("file_path") or ""),
        volume=float(payload.get("volume") or 0.0),
        fade_in=float(payload.get("fade_in") or 0.0),
        fade_out=float(payload.get("fade_out") or 0.0),
        loop=bool(payload.get("loop")),
        priority=int(payload.get("priority") or 0),
        metadata=dict(payload.get("metadata") or {}),
    )
    output_packet = {
        "packet_type": "runtime.event_response.v1",
        "packet_version": "runtime.event_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "audio-event-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built audio-event packet.",
        "refs": [],
        "data": {
            "audio_type": value.get("audio_type", ""),
            "priority": value.get("priority", 0),
            "loop": value.get("loop", False),
        },
    }]
