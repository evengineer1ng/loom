from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.event.event_window_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪟",
    "deterministic": True,
    "inputs": ["runtime.event_request.v1"],
    "outputs": ["runtime.event_response.v1"],
    "requires": [],
    "provides": ["runtime.event_window_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "event", "window", "recent", "slice"],
    "description": "Package a recent-event slice emitted by a single command window, preserving chronological action-local context.",
}


def build_event_window_packet(
    action: str,
    events: list[dict[str, Any]] | None,
    event_types: list[str] | None,
    count: int,
) -> dict[str, Any]:
    return {
        "action": action,
        "events": [dict(item) for item in (events or [])],
        "event_types": list(event_types or []),
        "count": int(count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_event_window_packet(
        action=str(payload.get("action") or ""),
        events=list(payload.get("events") or []),
        event_types=list(payload.get("event_types") or []),
        count=int(payload.get("count") or 0),
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
        "receipt_id": "event-window-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built event-window packet.",
        "refs": [],
        "data": {"action": value.get("action", ""), "count": value.get("count", 0)},
    }]
