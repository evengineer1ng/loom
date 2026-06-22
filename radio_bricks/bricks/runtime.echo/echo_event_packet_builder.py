from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.echo.echo_event_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔊",
    "deterministic": True,
    "inputs": ["runtime.echo_request.v1"],
    "outputs": ["runtime.echo_response.v1"],
    "requires": [],
    "provides": ["runtime.echo_event_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "echo", "memory", "motif", "node"],
    "description": "Package a memory echo event with node placement, echo type, motif code, and rendered description.",
}


def build_echo_event_packet(node_id: str, echo_type: str, motif_code: str, description: str) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "echo_type": echo_type,
        "motif_code": motif_code,
        "description": description,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_echo_event_packet(
        node_id=str(payload.get("node_id") or ""),
        echo_type=str(payload.get("echo_type") or ""),
        motif_code=str(payload.get("motif_code") or ""),
        description=str(payload.get("description") or ""),
    )
    output_packet = {
        "packet_type": "runtime.echo_response.v1",
        "packet_version": "runtime.echo_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "echo-event-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built echo-event packet.",
        "refs": [],
        "data": {"node_id": value.get("node_id", ""), "motif_code": value.get("motif_code", "")},
    }]
