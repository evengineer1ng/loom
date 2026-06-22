from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.neighbor_gate_status_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚧",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.neighbor_gate_status_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "gate", "neighbor", "status"],
    "description": "Package neighboring gate status with metric, threshold, effective threshold, player value, and passability.",
}


def build_neighbor_gate_status_packet(
    node_id: str,
    node_name: str,
    gate_type: str,
    metric: str,
    threshold: float,
    effective_threshold: float,
    player_value: float,
    passable: bool,
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "node_name": node_name,
        "gate_type": gate_type,
        "metric": metric,
        "threshold": float(threshold),
        "effective_threshold": float(effective_threshold),
        "player_value": float(player_value),
        "passable": bool(passable),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_neighbor_gate_status_packet(
        node_id=str(payload.get("node_id") or ""),
        node_name=str(payload.get("node_name") or ""),
        gate_type=str(payload.get("gate_type") or ""),
        metric=str(payload.get("metric") or ""),
        threshold=float(payload.get("threshold") or 0.0),
        effective_threshold=float(payload.get("effective_threshold") or 0.0),
        player_value=float(payload.get("player_value") or 0.0),
        passable=bool(payload.get("passable")),
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
        "receipt_id": "neighbor-gate-status-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built neighbor-gate status packet.",
        "refs": [],
        "data": {"node_id": value.get("node_id", ""), "passable": value.get("passable", False)},
    }]
