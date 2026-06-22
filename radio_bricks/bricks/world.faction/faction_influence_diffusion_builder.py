from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.faction.faction_influence_diffusion_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🕸️",
    "deterministic": True,
    "inputs": ["world.faction_request.v1"],
    "outputs": ["world.faction_response.v1"],
    "requires": [],
    "provides": ["world.faction_influence_diffusion_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "faction", "influence", "diffusion", "territory"],
    "description": "Package one faction-influence diffusion step with local influence, adjacent pull, node amplification, and opposition pressure.",
}


def build_faction_influence_diffusion_packet(
    node_id: str,
    faction_id: str,
    local_influence: float,
    adjacent_average: float,
    amplification: float,
    opposition_pressure: float,
    diffusion_factor: float,
    new_value: float,
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "faction_id": faction_id,
        "local_influence": float(local_influence),
        "adjacent_average": float(adjacent_average),
        "amplification": float(amplification),
        "opposition_pressure": float(opposition_pressure),
        "diffusion_factor": float(diffusion_factor),
        "new_value": float(new_value),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_faction_influence_diffusion_packet(
        node_id=str(payload.get("node_id") or ""),
        faction_id=str(payload.get("faction_id") or ""),
        local_influence=float(payload.get("local_influence") or 0.0),
        adjacent_average=float(payload.get("adjacent_average") or 0.0),
        amplification=float(payload.get("amplification") or 1.0),
        opposition_pressure=float(payload.get("opposition_pressure") or 0.0),
        diffusion_factor=float(payload.get("diffusion_factor") or 0.15),
        new_value=float(payload.get("new_value") or 0.0),
    )
    output_packet = {
        "packet_type": "world.faction_response.v1",
        "packet_version": "world.faction_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "faction-influence-diffusion",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built faction-influence diffusion packet.",
        "refs": [],
        "data": {"node_id": value.get("node_id", ""), "faction_id": value.get("faction_id", "")},
    }]
