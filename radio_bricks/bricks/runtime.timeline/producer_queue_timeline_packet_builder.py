from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.timeline.producer_queue_timeline_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📊",
    "deterministic": True,
    "inputs": ["runtime.timeline_request.v1"],
    "outputs": ["runtime.timeline_response.v1"],
    "requires": [],
    "provides": ["runtime.producer_queue_timeline_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "timeline", "producer", "queue", "segments"],
    "description": "Package a producer queue timeline view with queued, claimed, and done segments plus source and priority readouts for observer surfaces.",
}


def build_producer_queue_timeline_packet(
    segments: list[dict[str, Any]] | None,
    status_counts: dict[str, Any] | None,
    source_counts: dict[str, Any] | None,
    selected_view: str,
) -> dict[str, Any]:
    return {
        "segments": [dict(item) for item in (segments or [])],
        "status_counts": dict(status_counts or {}),
        "source_counts": dict(source_counts or {}),
        "selected_view": str(selected_view),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_producer_queue_timeline_packet(
        segments=list(payload.get("segments") or []),
        status_counts=dict(payload.get("status_counts") or {}),
        source_counts=dict(payload.get("source_counts") or {}),
        selected_view=str(payload.get("selected_view") or ""),
    )
    output_packet = {
        "packet_type": "runtime.timeline_response.v1",
        "packet_version": "runtime.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "producer-queue-timeline-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built producer-queue timeline packet.",
        "refs": [],
        "data": {
            "segment_count": len(value.get("segments", [])),
            "status_bucket_count": len(value.get("status_counts", {})),
            "selected_view": value.get("selected_view", ""),
        },
    }]
