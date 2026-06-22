from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.court.presence_request_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["world.court_request.v1"],
    "outputs": ["world.court_response.v1"],
    "requires": [],
    "provides": ["world.presence_request_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "court", "presence", "request"],
    "description": "Package an Oracle presence request with urgency, source, target location, and decay state.",
}


def build_presence_request_packet(
    request_id: str,
    source_agent_id: str,
    target_location: str,
    reason: str,
    text: str,
    urgency: float,
    is_active: bool = True,
) -> dict[str, Any]:
    return {
        "request_id": request_id,
        "source_agent_id": source_agent_id,
        "target_location": target_location,
        "reason": reason,
        "text": text,
        "urgency": float(urgency),
        "is_active": bool(is_active),
        "priority_band": "critical" if float(urgency) >= 80 else "high" if float(urgency) >= 55 else "routine",
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_presence_request_packet(
        request_id=str(payload.get("request_id") or ""),
        source_agent_id=str(payload.get("source_agent_id") or ""),
        target_location=str(payload.get("target_location") or ""),
        reason=str(payload.get("reason") or ""),
        text=str(payload.get("text") or ""),
        urgency=float(payload.get("urgency") or 0.0),
        is_active=bool(payload.get("is_active", True)),
    )
    output_packet = {
        "packet_type": "world.court_response.v1",
        "packet_version": "world.court_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "presence-request-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built presence request packet.",
        "refs": [],
        "data": {"request_id": value.get("request_id", ""), "priority_band": value.get("priority_band", "")},
    }]
