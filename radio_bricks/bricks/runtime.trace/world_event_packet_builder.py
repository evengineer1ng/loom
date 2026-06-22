from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.world_event_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧾",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.world_event_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "world", "event"],
    "description": "Package a ForkUniverse world event with typed family, changes, pressure delta, and audio signature.",
}


def build_world_event_packet(
    event_id: str,
    tick: int,
    family: str,
    event_type: str,
    summary: str,
    subject_ids: list[str] | None,
    location_id: str,
    changes: dict[str, Any] | None,
    pressure_delta: float,
    audio_signature: str,
) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "tick": int(tick),
        "family": family,
        "event_type": event_type,
        "summary": summary,
        "subject_ids": list(subject_ids or []),
        "location_id": location_id,
        "changes": dict(changes or {}),
        "pressure_delta": float(pressure_delta),
        "audio_signature": audio_signature,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_world_event_packet(
        event_id=str(payload.get("event_id") or ""),
        tick=int(payload.get("tick") or 0),
        family=str(payload.get("family") or ""),
        event_type=str(payload.get("event_type") or ""),
        summary=str(payload.get("summary") or ""),
        subject_ids=list(payload.get("subject_ids") or []),
        location_id=str(payload.get("location_id") or ""),
        changes=dict(payload.get("changes") or {}),
        pressure_delta=float(payload.get("pressure_delta") or 0.0),
        audio_signature=str(payload.get("audio_signature") or ""),
    )
    output_packet = {
        "packet_type": "runtime.trace_response.v1",
        "packet_version": "runtime.trace_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "world-event-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built world-event packet.",
        "refs": [],
        "data": {"event_id": value.get("event_id", ""), "family": value.get("family", "")},
    }]
