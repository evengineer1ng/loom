from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "visual.capture.visual_timeline_ingest_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎞️",
    "deterministic": True,
    "inputs": ["visual.capture_request.v1"],
    "outputs": ["visual.capture_response.v1"],
    "requires": [],
    "provides": ["visual.visual_timeline_ingest_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["visual", "capture", "timeline", "ingest", "futuresight"],
    "description": "Package scheduled visual ingest with capture source, seek position, interpreted description, and tape or event emission context.",
}


def build_visual_timeline_ingest_packet(
    label: str,
    source_type: str,
    source_ref: str,
    seek_sec: float,
    description: str,
    emitted_event_type: str,
) -> dict[str, Any]:
    return {
        "label": str(label),
        "source_type": str(source_type),
        "source_ref": str(source_ref),
        "seek_sec": float(seek_sec),
        "description": str(description),
        "emitted_event_type": str(emitted_event_type),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_visual_timeline_ingest_packet(
        label=str(payload.get("label") or ""),
        source_type=str(payload.get("source_type") or ""),
        source_ref=str(payload.get("source_ref") or ""),
        seek_sec=float(payload.get("seek_sec") or 0.0),
        description=str(payload.get("description") or ""),
        emitted_event_type=str(payload.get("emitted_event_type") or ""),
    )
    output_packet = {
        "packet_type": "visual.capture_response.v1",
        "packet_version": "visual.capture_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "visual-timeline-ingest-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built visual-timeline ingest packet.",
        "refs": [],
        "data": {
            "label": value.get("label", ""),
            "source_type": value.get("source_type", ""),
            "seek_sec": value.get("seek_sec", 0.0),
        },
    }]
