from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.booth_event_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎙️",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.booth_event_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "booth", "event", "tape"],
    "description": "Package a booth-compatible tape event with actor, action, object, valence, lap, priority, and optional time/source/feed context.",
}


def build_booth_event_packet(
    actor: str,
    action: str,
    object_value: str,
    valence: str,
    lap: int,
    priority: float,
    time_value: str,
    source: str,
    feed: str,
) -> dict[str, Any]:
    return {
        "actor": str(actor),
        "action": str(action),
        "object": str(object_value),
        "valence": str(valence),
        "lap": int(lap),
        "priority": float(priority),
        "time": str(time_value),
        "source": str(source),
        "feed": str(feed),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_booth_event_packet(
        actor=str(payload.get("actor") or ""),
        action=str(payload.get("action") or ""),
        object_value=str(payload.get("object") or ""),
        valence=str(payload.get("valence") or ""),
        lap=int(payload.get("lap") or 0),
        priority=float(payload.get("priority") or 0.0),
        time_value=str(payload.get("time") or ""),
        source=str(payload.get("source") or ""),
        feed=str(payload.get("feed") or ""),
    )
    output_packet = {
        "packet_type": "assembly.loom_response.v1",
        "packet_version": "assembly.loom_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "booth-event-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built booth-event packet.",
        "refs": [],
        "data": {
            "actor": value.get("actor", ""),
            "action": value.get("action", ""),
            "lap": value.get("lap", 0),
        },
    }]
