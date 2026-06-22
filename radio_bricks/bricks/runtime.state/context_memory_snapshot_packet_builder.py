from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.context_memory_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧷",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.context_memory_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "context", "memory", "snapshot"],
    "description": "Package live context-memory snapshot stats with producer candidate count, timeline depth, recent tags, audio state, and visible pins.",
}


def build_context_memory_snapshot_packet(
    audio_volume: float,
    audio_speed: float,
    producer_candidates: int,
    timeline_depth: int,
    recent_tags: list[str] | None,
    pins: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "audio_volume": float(audio_volume),
        "audio_speed": float(audio_speed),
        "producer_candidates": int(producer_candidates),
        "timeline_depth": int(timeline_depth),
        "recent_tags": [str(item) for item in (recent_tags or [])],
        "pins": [dict(item) for item in (pins or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_context_memory_snapshot_packet(
        audio_volume=float(payload.get("audio_volume") or 0.0),
        audio_speed=float(payload.get("audio_speed") or 0.0),
        producer_candidates=int(payload.get("producer_candidates") or 0),
        timeline_depth=int(payload.get("timeline_depth") or 0),
        recent_tags=list(payload.get("recent_tags") or []),
        pins=list(payload.get("pins") or []),
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
        "receipt_id": "context-memory-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built context-memory snapshot packet.",
        "refs": [],
        "data": {
            "producer_candidates": value.get("producer_candidates", 0),
            "timeline_depth": value.get("timeline_depth", 0),
            "pin_count": len(value.get("pins", [])),
        },
    }]
