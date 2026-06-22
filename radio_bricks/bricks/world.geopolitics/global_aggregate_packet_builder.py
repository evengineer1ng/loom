from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.geopolitics.global_aggregate_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌍",
    "deterministic": True,
    "inputs": ["world.geopolitics_request.v1"],
    "outputs": ["world.geopolitics_response.v1"],
    "requires": [],
    "provides": ["world.global_aggregate_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "geopolitics", "aggregate", "trade", "ideology"],
    "description": "Package world-level trade, ideology, population, and conflict aggregates across the three-layer geopolitical field.",
}


def build_global_aggregate_packet(
    global_trade_index: float,
    global_ideology_field: float,
    global_population: float,
    global_conflict_tension: float,
    leaderboard: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "global_trade_index": float(global_trade_index),
        "global_ideology_field": float(global_ideology_field),
        "global_population": float(global_population),
        "global_conflict_tension": float(global_conflict_tension),
        "leaderboard": list(leaderboard or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_global_aggregate_packet(
        global_trade_index=float(payload.get("global_trade_index") or 0.0),
        global_ideology_field=float(payload.get("global_ideology_field") or 0.0),
        global_population=float(payload.get("global_population") or 0.0),
        global_conflict_tension=float(payload.get("global_conflict_tension") or 0.0),
        leaderboard=list(payload.get("leaderboard") or []),
    )
    output_packet = {
        "packet_type": "world.geopolitics_response.v1",
        "packet_version": "world.geopolitics_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "global-aggregate-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built geopolitical aggregate packet.",
        "refs": [],
        "data": {"leaderboard_size": len(value.get("leaderboard", []))},
    }]
