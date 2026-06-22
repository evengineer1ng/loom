from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "spatial.sublocation.r_unit_exit_label_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚪",
    "deterministic": True,
    "inputs": ["spatial.sublocation_request.v1"],
    "outputs": ["spatial.sublocation_response.v1"],
    "requires": [],
    "provides": ["spatial.r_unit_exit_label_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["spatial", "sublocation", "r-unit", "exit", "direction"],
    "description": "Package an R-Unit access-hatch exit label with neighbor node id and human direction hint.",
}


def build_r_unit_exit_label_packet(
    neighbor_node_id: str,
    direction_hint: str,
) -> dict[str, Any]:
    return {
        "neighbor_node_id": neighbor_node_id,
        "direction_hint": direction_hint,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_r_unit_exit_label_packet(
        neighbor_node_id=str(payload.get("neighbor_node_id") or ""),
        direction_hint=str(payload.get("direction_hint") or ""),
    )
    output_packet = {
        "packet_type": "spatial.sublocation_response.v1",
        "packet_version": "spatial.sublocation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "r-unit-exit-label-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built R-Unit exit-label packet.",
        "refs": [],
        "data": {"neighbor_node_id": value.get("neighbor_node_id", ""), "direction_hint": value.get("direction_hint", "")},
    }]
