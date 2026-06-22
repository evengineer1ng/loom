from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.topology.gate_threshold_flex_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪜",
    "deterministic": True,
    "inputs": ["world.topology_request.v1"],
    "outputs": ["world.topology_response.v1"],
    "requires": [],
    "provides": ["world.gate_threshold_flex_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "topology", "gate", "flex", "ledger", "faction"],
    "description": "Package dynamic gate-threshold flex from normalized ledger state and dominant faction pressure.",
}


def build_gate_threshold_flex_packet(
    node_id: str,
    gate_type: str,
    base_flex: float,
    dominant_faction_id: str,
    faction_flex: float,
    resulting_flex_buffer: float,
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "gate_type": gate_type,
        "base_flex": float(base_flex),
        "dominant_faction_id": dominant_faction_id,
        "faction_flex": float(faction_flex),
        "resulting_flex_buffer": float(resulting_flex_buffer),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_gate_threshold_flex_packet(
        node_id=str(payload.get("node_id") or ""),
        gate_type=str(payload.get("gate_type") or ""),
        base_flex=float(payload.get("base_flex") or 0.0),
        dominant_faction_id=str(payload.get("dominant_faction_id") or ""),
        faction_flex=float(payload.get("faction_flex") or 0.0),
        resulting_flex_buffer=float(payload.get("resulting_flex_buffer") or 0.0),
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
        "receipt_id": "gate-threshold-flex-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built gate-threshold flex packet.",
        "refs": [],
        "data": {"node_id": value.get("node_id", ""), "gate_type": value.get("gate_type", "")},
    }]
