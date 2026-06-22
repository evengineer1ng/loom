from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.thread_event_projection_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧵",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.thread_event_projection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "thread", "event", "projection"],
    "description": "Project a story thread into a broadcast-facing event summary with heat, urgency, and status.",
}


def build_thread_event_projection_packet(title: str, mode: str, heat: float, urgency: float, status: str) -> dict[str, Any]:
    summary = f"{title} is still in motion." if mode == "active_listen" else f"{title} remains one of the most important unresolved developments."
    return {
        "event_type": "thread_status",
        "title": title,
        "summary": summary,
        "heat": float(heat),
        "urgency": float(urgency),
        "status": status,
        "mode": mode,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_thread_event_projection_packet(
        title=str(payload.get("title") or ""),
        mode=str(payload.get("mode") or ""),
        heat=float(payload.get("heat") or 0.0),
        urgency=float(payload.get("urgency") or 0.0),
        status=str(payload.get("status") or ""),
    )
    output_packet = {
        "packet_type": "runtime.story_response.v1",
        "packet_version": "runtime.story_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "thread-event-projection",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built thread-event projection packet.",
        "refs": [],
        "data": {"title": value.get("title", ""), "status": value.get("status", "")},
    }]
