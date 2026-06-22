from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.event.oracle_event_priority_queue",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.event_request.v1"],
    "outputs": ["runtime.event_response.v1"],
    "requires": [],
    "provides": ["runtime.oracle_event_priority_queue"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "event", "oracle", "priority"],
    "description": "Sort active kingdom events by severity times urgency for awakening and inspection order.",
}


def build_oracle_event_priority_queue(events: list[dict[str, Any]] | None) -> dict[str, Any]:
    queue = sorted(
        [dict(event) for event in (events or [])],
        key=lambda event: float(event.get("severity") or 0.0) * float(event.get("urgency") or 0.0),
        reverse=True,
    )
    return {
        "queue": queue,
        "next_event": queue[0] if queue else None,
        "event_count": len(queue),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_oracle_event_priority_queue(list(payload.get("events") or []))
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
        "receipt_id": "oracle-event-priority-queue",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built oracle event priority queue.",
        "refs": [],
        "data": {"event_count": value.get("event_count", 0)},
    }]
