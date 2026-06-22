from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.delivery_status_capture_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚦",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.delivery_status_capture_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "delivery", "capture", "status", "transition"],
    "description": "Map a delivery status to its downstream capture processing state using deterministic delivery rules.",
}


def build_delivery_status_capture_state_packet(status: str) -> dict[str, Any]:
    normalized_status = str(status)
    if normalized_status in {"failed", "cancelled", "expired"}:
        capture_status = "failed"
    elif normalized_status in {"downloaded", "installed"}:
        capture_status = "processed"
    else:
        capture_status = "pending"
    return {
        "delivery_status": normalized_status,
        "capture_status": capture_status,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_delivery_status_capture_state_packet(
        status=str(payload.get("status") or payload.get("delivery_status") or ""),
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
        "receipt_id": "delivery-status-capture-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built delivery-status capture-state packet.",
        "refs": [],
        "data": {
            "delivery_status": value.get("delivery_status", ""),
            "capture_status": value.get("capture_status", ""),
        },
    }]
