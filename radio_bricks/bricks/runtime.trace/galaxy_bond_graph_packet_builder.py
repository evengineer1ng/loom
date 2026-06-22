from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.galaxy_bond_graph_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌌",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.galaxy_bond_graph_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "galaxy", "graph", "oradio", "bond"],
    "description": "Package the shell galaxy read model with nodes, authored edges, and genesis-bond interpretation.",
}


def build_galaxy_bond_graph_packet(
    nodes: list[dict[str, Any]] | None,
    edges: list[dict[str, Any]] | None,
    focus: int,
    sun_label: str = "home loop",
    genesis_bond_policy: str = "all_nodes_bond_to_home_loop_by_default",
) -> dict[str, Any]:
    return {
        "nodes": [dict(item) for item in (nodes or [])],
        "edges": [dict(item) for item in (edges or [])],
        "focus": int(focus),
        "sun_label": str(sun_label),
        "genesis_bond_policy": str(genesis_bond_policy),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_galaxy_bond_graph_packet(
        nodes=list(payload.get("nodes") or []),
        edges=list(payload.get("edges") or []),
        focus=int(payload.get("focus") or 0),
        sun_label=str(payload.get("sun_label") or "home loop"),
        genesis_bond_policy=str(payload.get("genesis_bond_policy") or "all_nodes_bond_to_home_loop_by_default"),
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
        "receipt_id": "galaxy-bond-graph-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built galaxy bond-graph packet.",
        "refs": [],
        "data": {
            "node_count": len(value.get("nodes") or []),
            "edge_count": len(value.get("edges") or []),
        },
    }]
