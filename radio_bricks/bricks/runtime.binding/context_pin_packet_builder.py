from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.context_pin_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📌",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.context_pin_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "context", "pin", "memory"],
    "description": "Package context-memory pin and unpin commands with live segment fallback, payload shaping, and selected pin targeting.",
}


def build_context_pin_packet(
    action: str,
    payload: dict[str, Any] | None,
    selected_pin_id: str,
    pin_count: int,
) -> dict[str, Any]:
    return {
        "action": str(action),
        "payload": dict(payload or {}),
        "selected_pin_id": str(selected_pin_id),
        "pin_count": int(pin_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_context_pin_packet(
        action=str(payload.get("action") or ""),
        payload=dict(payload.get("payload") or {}),
        selected_pin_id=str(payload.get("selected_pin_id") or ""),
        pin_count=int(payload.get("pin_count") or 0),
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
        "receipt_id": "context-pin-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built context-pin packet.",
        "refs": [],
        "data": {
            "action": value.get("action", ""),
            "selected_pin_id": value.get("selected_pin_id", ""),
            "pin_count": value.get("pin_count", 0),
        },
    }]
