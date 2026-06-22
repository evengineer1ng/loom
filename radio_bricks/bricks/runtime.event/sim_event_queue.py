from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.event.sim_event_queue",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.event_request.v1"],
    "outputs": ["runtime.event_response.v1"],
    "requires": [],
    "provides": ["runtime.prioritized_event_queue"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "event", "queue", "priority"],
    "description": "Sort simulation events into a deterministic priority queue with preserved history.",
}


def build_sim_event_queue(events: list[dict[str, Any]] | None) -> dict[str, Any]:
    queue = sorted(
        [dict(event) for event in (events or [])],
        key=lambda event: (float(event.get("priority") or 0.0), int(event.get("ts") or 0), int(event.get("event_id") or 0)),
        reverse=True,
    )
    return {
        "queue": queue,
        "next_event": queue[0] if queue else None,
        "history": [dict(event) for event in (events or [])],
        "counts_by_type": _counts(queue, "event_type"),
        "counts_by_category": _counts(queue, "category"),
    }


def _counts(events: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        label = str(event.get(key) or "unknown")
        counts[label] = counts.get(label, 0) + 1
    return counts


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_sim_event_queue(list(payload.get("events") or []))
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
        "receipt_id": "sim-event-queue",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built prioritized event queue.",
        "refs": [],
        "data": {"queued_events": len(value.get("queue", []))},
    }]
