from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.endpoint_request_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📡",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.endpoint_request_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "club", "telemetry", "consent", "endpoint"],
    "description": "Package an advertised telemetry endpoint request before an oradio is allowed to touch it.",
}


def build_endpoint_request_packet(
    name: str,
    kind: str,
    reads: str,
    sensitive: bool,
    consented: bool,
) -> dict[str, Any]:
    return {
        "name": str(name),
        "kind": str(kind),
        "reads": str(reads),
        "sensitive": bool(sensitive),
        "consented": bool(consented),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_endpoint_request_packet(
        name=str(payload.get("name") or ""),
        kind=str(payload.get("kind") or ""),
        reads=str(payload.get("reads") or ""),
        sensitive=bool(payload.get("sensitive")),
        consented=bool(payload.get("consented")),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "endpoint-request-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built endpoint request packet.",
        "refs": [],
        "data": {
            "name": value.get("name", ""),
            "kind": value.get("kind", ""),
            "sensitive": value.get("sensitive", False),
        },
    }]
