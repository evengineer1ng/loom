from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.pending_event_summary_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📚",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.pending_event_summary_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "pending", "event", "summary"],
    "description": "Package a short pending-event summary with snippet list and summary text for low-signal or pre-chapter narration.",
}


def build_pending_event_summary_packet(
    snippets: list[str] | None,
    summary: str,
    event_count: int,
) -> dict[str, Any]:
    return {
        "snippets": [str(item) for item in (snippets or [])],
        "summary": str(summary),
        "event_count": int(event_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_pending_event_summary_packet(
        snippets=list(payload.get("snippets") or []),
        summary=str(payload.get("summary") or ""),
        event_count=int(payload.get("event_count") or 0),
    )
    output_packet = {
        "packet_type": "runtime.narration_response.v1",
        "packet_version": "runtime.narration_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "pending-event-summary-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built pending event-summary packet.",
        "refs": [],
        "data": {
            "event_count": value.get("event_count", 0),
            "summary": value.get("summary", ""),
        },
    }]
