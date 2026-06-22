from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.secret.knower_talk_result_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔮",
    "deterministic": True,
    "inputs": ["narrative.secret_request.v1"],
    "outputs": ["narrative.secret_response.v1"],
    "requires": [],
    "provides": ["narrative.knower_talk_result_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "secret", "knower", "talk", "result"],
    "description": "Package the surfaced result of a knower talk action, including event type, extracted fragment fields, and the action-local event window.",
}


def build_knower_talk_result_packet(
    event_type: str,
    events: list[dict[str, Any]] | None,
    payload: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "events": [dict(item) for item in (events or [])],
        "payload": dict(payload or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_knower_talk_result_packet(
        event_type=str(payload.get("event_type") or ""),
        events=list(payload.get("events") or []),
        payload=dict(payload.get("payload") or {}),
    )
    output_packet = {
        "packet_type": "narrative.secret_response.v1",
        "packet_version": "narrative.secret_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "knower-talk-result-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built knower-talk result packet.",
        "refs": [],
        "data": {"event_type": value.get("event_type", ""), "event_count": len(value.get("events", []))},
    }]
