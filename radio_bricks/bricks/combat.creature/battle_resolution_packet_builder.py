from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "combat.creature.battle_resolution_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⚔️",
    "deterministic": True,
    "inputs": ["combat.creature_request.v1"],
    "outputs": ["combat.creature_response.v1"],
    "requires": [],
    "provides": ["combat.battle_resolution_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["combat", "creature", "battle", "result", "fatigue"],
    "description": "Package a Neikos battle result with winner, remaining team counts, turns, fatigue delta, and move log.",
}


def build_battle_resolution_packet(
    winner: str,
    player_remaining: int,
    opponent_remaining: int,
    turns: int,
    fatigue_delta: float,
    moves_used: list[str] | None,
) -> dict[str, Any]:
    return {
        "winner": winner,
        "player_remaining": int(player_remaining),
        "opponent_remaining": int(opponent_remaining),
        "turns": int(turns),
        "fatigue_delta": float(fatigue_delta),
        "moves_used": list(moves_used or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_battle_resolution_packet(
        winner=str(payload.get("winner") or ""),
        player_remaining=int(payload.get("player_remaining") or 0),
        opponent_remaining=int(payload.get("opponent_remaining") or 0),
        turns=int(payload.get("turns") or 0),
        fatigue_delta=float(payload.get("fatigue_delta") or 0.0),
        moves_used=list(payload.get("moves_used") or []),
    )
    output_packet = {
        "packet_type": "combat.creature_response.v1",
        "packet_version": "combat.creature_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "battle-resolution-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built battle-resolution packet.",
        "refs": [],
        "data": {"winner": value.get("winner", ""), "turns": value.get("turns", 0)},
    }]
