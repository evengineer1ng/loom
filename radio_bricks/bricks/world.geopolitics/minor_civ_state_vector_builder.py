from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.geopolitics.minor_civ_state_vector_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌱",
    "deterministic": True,
    "inputs": ["world.geopolitics_request.v1"],
    "outputs": ["world.geopolitics_response.v1"],
    "requires": [],
    "provides": ["world.minor_civ_state_vector"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "geopolitics", "minor_civ", "deep_field", "vector"],
    "description": "Build a Deep Field minor-civ state vector packet with vital signs, hidden macro engines, era flags, and lifecycle markers.",
}


def build_minor_civ_state_vector(
    civ_id: str,
    name: str,
    population: float,
    wealth_index: float,
    stability: float,
    cultural_alignment: float,
    influence_score: float,
    military_strength: float,
    trade_dependency: float,
    momentum: float,
    volatility: float,
    alignment_drift: float,
    shock_potential: float,
    importance: float,
    rank: int,
    era_flag: str,
    is_promoted: bool,
    biome: str,
    geographic_region: int,
) -> dict[str, Any]:
    return {
        "civ_id": civ_id,
        "name": name,
        "population": float(population),
        "wealth_index": float(wealth_index),
        "stability": float(stability),
        "cultural_alignment": float(cultural_alignment),
        "influence_score": float(influence_score),
        "military_strength": float(military_strength),
        "trade_dependency": float(trade_dependency),
        "momentum": float(momentum),
        "volatility": float(volatility),
        "alignment_drift": float(alignment_drift),
        "shock_potential": float(shock_potential),
        "importance": float(importance),
        "rank": int(rank),
        "era_flag": era_flag,
        "is_promoted": bool(is_promoted),
        "biome": biome,
        "geographic_region": int(geographic_region),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_minor_civ_state_vector(
        civ_id=str(payload.get("civ_id") or ""),
        name=str(payload.get("name") or ""),
        population=float(payload.get("population") or 0.0),
        wealth_index=float(payload.get("wealth_index") or 0.0),
        stability=float(payload.get("stability") or 0.0),
        cultural_alignment=float(payload.get("cultural_alignment") or 0.0),
        influence_score=float(payload.get("influence_score") or 0.0),
        military_strength=float(payload.get("military_strength") or 0.0),
        trade_dependency=float(payload.get("trade_dependency") or 0.0),
        momentum=float(payload.get("momentum") or 0.0),
        volatility=float(payload.get("volatility") or 0.0),
        alignment_drift=float(payload.get("alignment_drift") or 0.0),
        shock_potential=float(payload.get("shock_potential") or 0.0),
        importance=float(payload.get("importance") or 0.0),
        rank=int(payload.get("rank") or 0),
        era_flag=str(payload.get("era_flag") or ""),
        is_promoted=bool(payload.get("is_promoted", False)),
        biome=str(payload.get("biome") or ""),
        geographic_region=int(payload.get("geographic_region") or 0),
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
        "receipt_id": "minor-civ-state-vector",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built minor-civ state vector.",
        "refs": [],
        "data": {"civ_id": value.get("civ_id", ""), "era_flag": value.get("era_flag", "")},
    }]
