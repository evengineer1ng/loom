from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.event.event_cooldown_gate_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚦",
    "deterministic": True,
    "inputs": ["runtime.event_request.v1"],
    "outputs": ["runtime.event_response.v1"],
    "requires": [],
    "provides": ["runtime.event_cooldown_gate_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "event", "cooldown", "gate", "emission"],
    "description": "Package per-event cooldown gating with minute buckets, prior emission minute, cooldown window, and allow or block result.",
}


def build_event_cooldown_gate_packet(
    event_type: str,
    now_minute: int,
    last_emit_minute: int,
    cooldown_minutes: int,
    allowed: bool,
) -> dict[str, Any]:
    return {
        "event_type": str(event_type),
        "now_minute": int(now_minute),
        "last_emit_minute": int(last_emit_minute),
        "cooldown_minutes": int(cooldown_minutes),
        "allowed": bool(allowed),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_event_cooldown_gate_packet(
        event_type=str(payload.get("event_type") or ""),
        now_minute=int(payload.get("now_minute") or 0),
        last_emit_minute=int(payload.get("last_emit_minute") or 0),
        cooldown_minutes=int(payload.get("cooldown_minutes") or 0),
        allowed=bool(payload.get("allowed")),
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
        "receipt_id": "event-cooldown-gate-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built event-cooldown gate packet.",
        "refs": [],
        "data": {
            "event_type": value.get("event_type", ""),
            "cooldown_minutes": value.get("cooldown_minutes", 0),
            "allowed": value.get("allowed", False),
        },
    }]
