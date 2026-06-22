from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.brick_wire_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪢",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.brick_wire_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "brick", "wire", "pipeline", "packet-type"],
    "description": "Package a type-checked wire between two bricks, including shared packet types and compatibility status.",
}


def build_brick_wire_packet(
    producer_id: str,
    consumer_id: str,
    producer_outputs: list[str] | None,
    consumer_inputs: list[str] | None,
    shared_packet_types: list[str] | None,
) -> dict[str, Any]:
    shared = [str(item) for item in (shared_packet_types or [])]
    return {
        "producer_id": str(producer_id),
        "consumer_id": str(consumer_id),
        "producer_outputs": [str(item) for item in (producer_outputs or [])],
        "consumer_inputs": [str(item) for item in (consumer_inputs or [])],
        "shared_packet_types": shared,
        "compatible": bool(shared),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_brick_wire_packet(
        producer_id=str(payload.get("producer_id") or ""),
        consumer_id=str(payload.get("consumer_id") or ""),
        producer_outputs=list(payload.get("producer_outputs") or []),
        consumer_inputs=list(payload.get("consumer_inputs") or []),
        shared_packet_types=list(payload.get("shared_packet_types") or []),
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
        "receipt_id": "brick-wire-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built brick wire packet.",
        "refs": [],
        "data": {
            "producer_id": value.get("producer_id", ""),
            "consumer_id": value.get("consumer_id", ""),
            "compatible": value.get("compatible", False),
        },
    }]
