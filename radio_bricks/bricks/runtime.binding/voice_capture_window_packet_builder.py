from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.voice_capture_window_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗣️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.voice_capture_window_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "voice", "capture", "vad"],
    "description": "Package a voice-capture window with sample rate, frame sizing, silence threshold, minimum speech duration, and speech-ready state.",
}


def build_voice_capture_window_packet(
    sample_rate: int,
    frame_ms: int,
    frame_size: int,
    silence_frames_needed: int,
    min_speech_frames: int,
    in_speech: bool,
    silence_count: int,
    ready_frame_count: int,
) -> dict[str, Any]:
    return {
        "sample_rate": int(sample_rate),
        "frame_ms": int(frame_ms),
        "frame_size": int(frame_size),
        "silence_frames_needed": int(silence_frames_needed),
        "min_speech_frames": int(min_speech_frames),
        "in_speech": bool(in_speech),
        "silence_count": int(silence_count),
        "ready_frame_count": int(ready_frame_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_voice_capture_window_packet(
        sample_rate=int(payload.get("sample_rate") or 0),
        frame_ms=int(payload.get("frame_ms") or 0),
        frame_size=int(payload.get("frame_size") or 0),
        silence_frames_needed=int(payload.get("silence_frames_needed") or 0),
        min_speech_frames=int(payload.get("min_speech_frames") or 0),
        in_speech=bool(payload.get("in_speech")),
        silence_count=int(payload.get("silence_count") or 0),
        ready_frame_count=int(payload.get("ready_frame_count") or 0),
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
        "receipt_id": "voice-capture-window-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built voice-capture window packet.",
        "refs": [],
        "data": {
            "sample_rate": value.get("sample_rate", 0),
            "ready_frame_count": value.get("ready_frame_count", 0),
            "in_speech": value.get("in_speech", False),
        },
    }]
