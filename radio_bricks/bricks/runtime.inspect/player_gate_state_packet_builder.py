from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.player_gate_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🛂",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.player_gate_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "gate", "player", "state"],
    "description": "Package the player's current gate-relevant metrics for map comparisons and move rejection explanations.",
}


def build_player_gate_state_packet(
    trainer_rating: float,
    faction_standing: float,
    research_milestones: float,
    ecological_balance: float,
    anomaly_exposure: float,
    economic_investment: float,
    exploration_score: float,
    league_tier: float,
) -> dict[str, Any]:
    return {
        "trainer_rating": float(trainer_rating),
        "faction_standing": float(faction_standing),
        "research_milestones": float(research_milestones),
        "ecological_balance": float(ecological_balance),
        "anomaly_exposure": float(anomaly_exposure),
        "economic_investment": float(economic_investment),
        "exploration_score": float(exploration_score),
        "league_tier": float(league_tier),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_player_gate_state_packet(
        trainer_rating=float(payload.get("trainer_rating") or 0.0),
        faction_standing=float(payload.get("faction_standing") or 0.0),
        research_milestones=float(payload.get("research_milestones") or 0.0),
        ecological_balance=float(payload.get("ecological_balance") or 0.0),
        anomaly_exposure=float(payload.get("anomaly_exposure") or 0.0),
        economic_investment=float(payload.get("economic_investment") or 0.0),
        exploration_score=float(payload.get("exploration_score") or 0.0),
        league_tier=float(payload.get("league_tier") or 0.0),
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
        "receipt_id": "player-gate-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built player gate-state packet.",
        "refs": [],
        "data": {"trainer_rating": value.get("trainer_rating", 0.0), "league_tier": value.get("league_tier", 0.0)},
    }]
