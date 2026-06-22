from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.loom_transport_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎞️",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.loom_transport_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "loom", "transport", "playback", "tick"],
    "description": "Package Loom playback transport state with play flag, tick cadence, ribbon phase, and elapsed media time.",
}


def build_loom_transport_packet(
    playing: bool,
    tick_ms: int,
    media_refresh_ms: int,
    thumbnail_refresh_ms: int,
    ribbon_phase: float,
    media_time: float,
) -> dict[str, Any]:
    return {
        "playing": bool(playing),
        "tick_ms": int(tick_ms),
        "media_refresh_ms": int(media_refresh_ms),
        "thumbnail_refresh_ms": int(thumbnail_refresh_ms),
        "ribbon_phase": float(ribbon_phase),
        "media_time": float(media_time),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_loom_transport_packet(
        playing=bool(payload.get("playing")),
        tick_ms=int(payload.get("tick_ms") or 0),
        media_refresh_ms=int(payload.get("media_refresh_ms") or 0),
        thumbnail_refresh_ms=int(payload.get("thumbnail_refresh_ms") or 0),
        ribbon_phase=float(payload.get("ribbon_phase") or 0.0),
        media_time=float(payload.get("media_time") or 0.0),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "loom-transport-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Loom transport packet.",
        "refs": [],
        "data": {
            "playing": value.get("playing", False),
            "tick_ms": value.get("tick_ms", 0),
        },
    }]
