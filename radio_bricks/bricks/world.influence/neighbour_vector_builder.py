from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.influence.neighbour_vector_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["world.influence_request.v1"],
    "outputs": ["world.influence_response.v1"],
    "requires": [],
    "provides": ["world.neighbour_influence_vector"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "influence", "neighbour", "vector"],
    "description": "Derive a lazy neighbour pressure vector from baseline dispositions and player-state posture.",
}


def build_neighbour_vector(
    baseline_aggression: float,
    baseline_trade_interest: float,
    baseline_cultural_export: float,
    baseline_faith_competition: float,
    player_strength: float,
    player_military: float,
    player_trade: float,
    player_faith: float,
    player_cultural_confidence: float,
    player_interpretation_divergence: float,
    drift: float,
    neighbour_id: str,
) -> dict[str, Any]:
    military_pressure = baseline_aggression * 30.0 + (1.0 - player_strength) * 20.0 - player_military * 15.0 + drift * 5.0
    trade_pressure = baseline_trade_interest * 20.0 + player_trade * 10.0 - (1.0 - player_strength) * 5.0 + drift * 3.0
    cultural_pressure = baseline_cultural_export * 15.0 - player_cultural_confidence * 0.1 + drift * 4.0
    myth_pressure = baseline_faith_competition * 20.0 - player_faith * 10.0 + player_interpretation_divergence * 0.2 + drift * 3.0
    diplomatic_stance = max(-1.0, min(1.0, -baseline_aggression * 0.5 + baseline_trade_interest * 0.3 + player_strength * 0.3 - 0.1 + drift))
    return {
        "kingdom_id": neighbour_id,
        "trade_pressure": trade_pressure,
        "cultural_pressure": cultural_pressure,
        "military_pressure": military_pressure,
        "myth_pressure": myth_pressure,
        "diplomatic_stance": diplomatic_stance,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_neighbour_vector(
        baseline_aggression=float(payload.get("baseline_aggression") or 0.0),
        baseline_trade_interest=float(payload.get("baseline_trade_interest") or 0.0),
        baseline_cultural_export=float(payload.get("baseline_cultural_export") or 0.0),
        baseline_faith_competition=float(payload.get("baseline_faith_competition") or 0.0),
        player_strength=float(payload.get("player_strength") or 0.0),
        player_military=float(payload.get("player_military") or 0.0),
        player_trade=float(payload.get("player_trade") or 0.0),
        player_faith=float(payload.get("player_faith") or 0.0),
        player_cultural_confidence=float(payload.get("player_cultural_confidence") or 0.0),
        player_interpretation_divergence=float(payload.get("player_interpretation_divergence") or 0.0),
        drift=float(payload.get("drift") or 0.0),
        neighbour_id=str(payload.get("neighbour_id") or ""),
    )
    output_packet = {
        "packet_type": "world.influence_response.v1",
        "packet_version": "world.influence_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "neighbour-vector",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built neighbour influence vector.",
        "refs": [],
        "data": {"kingdom_id": value.get("kingdom_id", "")},
    }]
