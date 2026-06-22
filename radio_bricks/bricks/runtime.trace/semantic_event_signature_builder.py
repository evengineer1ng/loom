from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.semantic_event_signature_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧬",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.semantic_event_signature_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "event", "semantic", "signature"],
    "description": "Package a lightweight semantic event signature for duplicate suppression using event type and normalized distinguishing tokens.",
}


def build_semantic_event_signature_packet(
    event_type: str,
    signature: str,
    signature_keys: list[str] | None,
) -> dict[str, Any]:
    return {
        "event_type": str(event_type),
        "signature": str(signature),
        "signature_keys": [str(item) for item in (signature_keys or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_semantic_event_signature_packet(
        event_type=str(payload.get("event_type") or ""),
        signature=str(payload.get("signature") or ""),
        signature_keys=list(payload.get("signature_keys") or []),
    )
    output_packet = {
        "packet_type": "runtime.trace_response.v1",
        "packet_version": "runtime.trace_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "semantic-event-signature-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built semantic event-signature packet.",
        "refs": [],
        "data": {
            "event_type": value.get("event_type", ""),
            "signature": value.get("signature", ""),
        },
    }]
