from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.league.trainer_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🥊",
    "deterministic": True,
    "inputs": ["runtime.league_request.v1"],
    "outputs": ["runtime.league_response.v1"],
    "requires": [],
    "provides": ["runtime.trainer_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "league", "trainer", "rating", "team"],
    "description": "Package a trainer with rating, tier, team species ids, risk profile, ideology vector, and record.",
}


def build_trainer_packet(
    trainer_id: str,
    name: str,
    is_player: bool,
    rating: float,
    tier: str,
    team_species_ids: list[str] | None,
    risk_profile: float,
    ideology_vector: dict[str, float] | None,
    wins: int,
    losses: int,
) -> dict[str, Any]:
    return {
        "trainer_id": trainer_id,
        "name": name,
        "is_player": bool(is_player),
        "rating": float(rating),
        "tier": tier,
        "team_species_ids": list(team_species_ids or []),
        "risk_profile": float(risk_profile),
        "ideology_vector": {str(key): float(value) for key, value in (ideology_vector or {}).items()},
        "wins": int(wins),
        "losses": int(losses),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_trainer_packet(
        trainer_id=str(payload.get("trainer_id") or ""),
        name=str(payload.get("name") or ""),
        is_player=bool(payload.get("is_player", False)),
        rating=float(payload.get("rating") or 0.0),
        tier=str(payload.get("tier") or ""),
        team_species_ids=list(payload.get("team_species_ids") or []),
        risk_profile=float(payload.get("risk_profile") or 0.0),
        ideology_vector=dict(payload.get("ideology_vector") or {}),
        wins=int(payload.get("wins") or 0),
        losses=int(payload.get("losses") or 0),
    )
    output_packet = {
        "packet_type": "runtime.league_response.v1",
        "packet_version": "runtime.league_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "trainer-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built trainer packet.",
        "refs": [],
        "data": {"trainer_id": value.get("trainer_id", ""), "tier": value.get("tier", "")},
    }]
