from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.map_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗺️",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.map_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "map", "snapshot", "nodes"],
    "description": "Package a map snapshot with node list, start/current markers, neighbor set, and player gate-state comparison data.",
}


def build_map_snapshot_packet(
    nodes: list[dict[str, Any]] | None,
    start: str,
    current: str,
    neighbors: list[str] | None,
    player_gate_state: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "nodes": [dict(item) for item in (nodes or [])],
        "start": start,
        "current": current,
        "neighbors": list(neighbors or []),
        "player_gate_state": dict(player_gate_state or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_map_snapshot_packet(
        nodes=list(payload.get("nodes") or []),
        start=str(payload.get("start") or ""),
        current=str(payload.get("current") or ""),
        neighbors=list(payload.get("neighbors") or []),
        player_gate_state=dict(payload.get("player_gate_state") or {}),
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
        "receipt_id": "map-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built map snapshot packet.",
        "refs": [],
        "data": {"current": value.get("current", ""), "neighbor_count": len(value.get("neighbors", []))},
    }]
