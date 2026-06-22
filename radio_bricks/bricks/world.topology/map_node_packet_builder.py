from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.topology.map_node_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗺️",
    "deterministic": True,
    "inputs": ["world.topology_request.v1"],
    "outputs": ["world.topology_response.v1"],
    "requires": [],
    "provides": ["world.map_node_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "topology", "node", "biome", "neighbors"],
    "description": "Package a Neikos map node with type, region, neighbors, gate detail, and relay/start flags.",
}


def build_map_node_packet(
    node_id: str,
    node_type: str,
    region: str,
    name: str,
    biome: tuple[float, ...] | list[float] | None,
    neighbors: list[str] | None,
    gate_detail: dict[str, Any] | None,
    is_start: bool,
    is_relay_node: bool,
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "node_type": node_type,
        "region": region,
        "name": name,
        "biome": list(biome or []),
        "neighbors": list(neighbors or []),
        "gate_detail": dict(gate_detail or {}),
        "is_start": bool(is_start),
        "is_relay_node": bool(is_relay_node),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_map_node_packet(
        node_id=str(payload.get("node_id") or ""),
        node_type=str(payload.get("node_type") or ""),
        region=str(payload.get("region") or ""),
        name=str(payload.get("name") or ""),
        biome=payload.get("biome") or [],
        neighbors=list(payload.get("neighbors") or []),
        gate_detail=dict(payload.get("gate_detail") or {}),
        is_start=bool(payload.get("is_start", False)),
        is_relay_node=bool(payload.get("is_relay_node", False)),
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
        "receipt_id": "map-node-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built map-node packet.",
        "refs": [],
        "data": {"node_id": value.get("node_id", ""), "node_type": value.get("node_type", "")},
    }]
