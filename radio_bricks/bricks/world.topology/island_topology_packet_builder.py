from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.topology.island_topology_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏝️",
    "deterministic": True,
    "inputs": ["world.topology_request.v1"],
    "outputs": ["world.topology_response.v1"],
    "requires": [],
    "provides": ["world.island_topology_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "topology", "island", "relay", "anomaly"],
    "description": "Package high-level island topology metadata including climate, start, depth entrances, active types, relay nodes, and anomaly zones.",
}


def build_island_topology_packet(
    seed: int,
    island_name: str,
    climate: str,
    start_node_id: str,
    depth_entrance_ids: list[str] | None,
    sub_islet_ids: list[list[str]] | None,
    active_types: list[str] | None,
    relay_node_ids: list[str] | None,
    anomaly_zone_ids: list[str] | None,
    node_count: int,
) -> dict[str, Any]:
    return {
        "seed": int(seed),
        "island_name": island_name,
        "climate": climate,
        "start_node_id": start_node_id,
        "depth_entrance_ids": list(depth_entrance_ids or []),
        "sub_islet_ids": list(sub_islet_ids or []),
        "active_types": list(active_types or []),
        "relay_node_ids": list(relay_node_ids or []),
        "anomaly_zone_ids": list(anomaly_zone_ids or []),
        "node_count": int(node_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_island_topology_packet(
        seed=int(payload.get("seed") or 0),
        island_name=str(payload.get("island_name") or ""),
        climate=str(payload.get("climate") or ""),
        start_node_id=str(payload.get("start_node_id") or ""),
        depth_entrance_ids=list(payload.get("depth_entrance_ids") or []),
        sub_islet_ids=list(payload.get("sub_islet_ids") or []),
        active_types=list(payload.get("active_types") or []),
        relay_node_ids=list(payload.get("relay_node_ids") or []),
        anomaly_zone_ids=list(payload.get("anomaly_zone_ids") or []),
        node_count=int(payload.get("node_count") or 0),
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
        "receipt_id": "island-topology-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built island-topology packet.",
        "refs": [],
        "data": {"island_name": value.get("island_name", ""), "node_count": value.get("node_count", 0)},
    }]
