from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.event.web_audio_bridge_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌉",
    "deterministic": True,
    "inputs": ["runtime.event_request.v1"],
    "outputs": ["runtime.event_response.v1"],
    "requires": [],
    "provides": ["runtime.web_audio_bridge_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "event", "web", "audio", "bridge"],
    "description": "Package a browser-facing audio bridge message with audio type, metadata, and enriched transport fields like ducking, mute, action, scalar, or variant.",
}


def build_web_audio_bridge_packet(
    audio_type: str,
    metadata: dict[str, Any] | None,
    ducking: bool,
    muted: bool,
    action: str,
    scalar: float,
    variant: str,
) -> dict[str, Any]:
    return {
        "audio_type": str(audio_type),
        "metadata": dict(metadata or {}),
        "ducking": bool(ducking),
        "muted": bool(muted),
        "action": str(action),
        "scalar": float(scalar),
        "variant": str(variant),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_web_audio_bridge_packet(
        audio_type=str(payload.get("audio_type") or ""),
        metadata=dict(payload.get("metadata") or {}),
        ducking=bool(payload.get("ducking")),
        muted=bool(payload.get("muted")),
        action=str(payload.get("action") or ""),
        scalar=float(payload.get("scalar") or 0.0),
        variant=str(payload.get("variant") or ""),
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
        "receipt_id": "web-audio-bridge-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built web-audio bridge packet.",
        "refs": [],
        "data": {
            "audio_type": value.get("audio_type", ""),
            "ducking": value.get("ducking", False),
            "muted": value.get("muted", False),
        },
    }]
