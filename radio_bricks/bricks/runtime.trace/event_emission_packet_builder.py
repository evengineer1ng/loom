from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.event_emission_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📣",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.event_emission_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "event", "emission", "ledger"],
    "description": "Package authoritative world-event emission with family, subjects, causal changes, pressure delta, audio signature, and character-ledger attribution.",
}


def build_event_emission_packet(
    tick: int,
    family: str,
    event_type: str,
    summary: str,
    subject_ids: list[str] | None,
    changes: dict[str, Any] | None,
    pressure_delta: float,
    audio_signature: str,
    attributed_character_ids: list[str] | None,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "family": str(family),
        "event_type": str(event_type),
        "summary": str(summary),
        "subject_ids": [str(item) for item in (subject_ids or [])],
        "changes": dict(changes or {}),
        "pressure_delta": float(pressure_delta),
        "audio_signature": str(audio_signature),
        "attributed_character_ids": [str(item) for item in (attributed_character_ids or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_event_emission_packet(
        tick=int(payload.get("tick") or 0),
        family=str(payload.get("family") or ""),
        event_type=str(payload.get("event_type") or ""),
        summary=str(payload.get("summary") or ""),
        subject_ids=list(payload.get("subject_ids") or []),
        changes=dict(payload.get("changes") or {}),
        pressure_delta=float(payload.get("pressure_delta") or 0.0),
        audio_signature=str(payload.get("audio_signature") or ""),
        attributed_character_ids=list(payload.get("attributed_character_ids") or []),
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
        "receipt_id": "event-emission-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built event-emission packet.",
        "refs": [],
        "data": {
            "family": value.get("family", ""),
            "event_type": value.get("event_type", ""),
            "attribution_count": len(value.get("attributed_character_ids", [])),
        },
    }]
