from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.command_event_poll_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⏱️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.command_event_poll_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "command", "poll", "events"],
    "description": "Package the queued-command poll contract with pre-action event sequence, deadline, new-event slice, and action result context.",
}


def build_command_event_poll_packet(
    action: str,
    before_seq: int,
    after_seq: int,
    deadline_ms: int,
    poll_interval_ms: int,
    new_event_count: int,
    events: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "action": action,
        "before_seq": int(before_seq),
        "after_seq": int(after_seq),
        "deadline_ms": int(deadline_ms),
        "poll_interval_ms": int(poll_interval_ms),
        "new_event_count": int(new_event_count),
        "events": [dict(item) for item in (events or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_command_event_poll_packet(
        action=str(payload.get("action") or ""),
        before_seq=int(payload.get("before_seq") or 0),
        after_seq=int(payload.get("after_seq") or 0),
        deadline_ms=int(payload.get("deadline_ms") or 0),
        poll_interval_ms=int(payload.get("poll_interval_ms") or 20),
        new_event_count=int(payload.get("new_event_count") or 0),
        events=list(payload.get("events") or []),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "command-event-poll-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built command-event poll packet.",
        "refs": [],
        "data": {"action": value.get("action", ""), "new_event_count": value.get("new_event_count", 0)},
    }]
