from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.influence.operator_input_ripple_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🫸",
    "deterministic": True,
    "inputs": ["world.influence_request.v1"],
    "outputs": ["world.influence_response.v1"],
    "requires": [],
    "provides": ["world.operator_input_ripple_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "influence", "operator", "ripple", "pressure"],
    "description": "Package interpreted operator input as a pressure ripple over a target domain with signed magnitude and emitted event summary.",
}


def build_operator_input_ripple_packet(
    intent: str,
    magnitude: float,
    target_domain: str,
    note: str,
    signed_delta: float,
    event: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "intent": intent,
        "magnitude": float(magnitude),
        "target_domain": target_domain,
        "note": note,
        "signed_delta": float(signed_delta),
        "event": dict(event or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_operator_input_ripple_packet(
        intent=str(payload.get("intent") or ""),
        magnitude=float(payload.get("magnitude") or 0.0),
        target_domain=str(payload.get("target_domain") or ""),
        note=str(payload.get("note") or ""),
        signed_delta=float(payload.get("signed_delta") or 0.0),
        event=dict(payload.get("event") or {}),
    )
    output_packet = {
        "packet_type": "world.influence_response.v1",
        "packet_version": "world.influence_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "operator-input-ripple-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built operator-input ripple packet.",
        "refs": [],
        "data": {"intent": value.get("intent", ""), "target_domain": value.get("target_domain", "")},
    }]
