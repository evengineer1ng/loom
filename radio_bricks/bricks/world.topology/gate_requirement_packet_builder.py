from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.topology.gate_requirement_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚧",
    "deterministic": True,
    "inputs": ["world.topology_request.v1"],
    "outputs": ["world.topology_response.v1"],
    "requires": [],
    "provides": ["world.gate_requirement_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "topology", "gate", "threshold", "alternate_path"],
    "description": "Package a topology gate requirement with primary threshold, flex buffer, and alternate-path conditions.",
}


def build_gate_requirement_packet(
    gate_type: str,
    primary_metric: str,
    threshold: float,
    secondary_modifier: str,
    flex_buffer: float,
    alternate_paths: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "gate_type": gate_type,
        "primary_metric": primary_metric,
        "threshold": float(threshold),
        "secondary_modifier": secondary_modifier,
        "flex_buffer": float(flex_buffer),
        "effective_threshold": float(threshold) - float(flex_buffer),
        "alternate_paths": list(alternate_paths or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_gate_requirement_packet(
        gate_type=str(payload.get("gate_type") or ""),
        primary_metric=str(payload.get("primary_metric") or ""),
        threshold=float(payload.get("threshold") or 0.0),
        secondary_modifier=str(payload.get("secondary_modifier") or ""),
        flex_buffer=float(payload.get("flex_buffer") or 0.0),
        alternate_paths=list(payload.get("alternate_paths") or []),
    )
    output_packet = {
        "packet_type": "world.topology_response.v1",
        "packet_version": "world.topology_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "gate-requirement-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built gate-requirement packet.",
        "refs": [],
        "data": {"gate_type": value.get("gate_type", ""), "primary_metric": value.get("primary_metric", "")},
    }]
