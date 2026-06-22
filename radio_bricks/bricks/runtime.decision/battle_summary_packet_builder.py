from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.battle_summary_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⚔️",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.battle_summary_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "battle", "summary", "rating"],
    "description": "Package a battle action summary with winner, remaining combatants, turn count, move usage, rating output, and event context.",
}


def build_battle_summary_packet(
    ok: bool,
    winner: str,
    player_remaining: int,
    opponent_remaining: int,
    turns: int,
    moves_used: list[str] | None,
    player_rating: float | None,
    opponent_name: str,
    tick: int | None,
    events: list[dict[str, Any]] | None,
    error: str = "",
) -> dict[str, Any]:
    packet = {
        "ok": bool(ok),
        "winner": winner,
        "player_remaining": int(player_remaining),
        "opponent_remaining": int(opponent_remaining),
        "turns": int(turns),
        "moves_used": list(moves_used or []),
        "opponent_name": opponent_name,
        "events": [dict(item) for item in (events or [])],
    }
    if player_rating is not None:
        packet["player_rating"] = float(player_rating)
    if tick is not None:
        packet["tick"] = int(tick)
    if error:
        packet["error"] = error
    return packet


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_battle_summary_packet(
        ok=bool(payload.get("ok")),
        winner=str(payload.get("winner") or ""),
        player_remaining=int(payload.get("player_remaining") or 0),
        opponent_remaining=int(payload.get("opponent_remaining") or 0),
        turns=int(payload.get("turns") or 0),
        moves_used=list(payload.get("moves_used") or []),
        player_rating=payload.get("player_rating"),
        opponent_name=str(payload.get("opponent_name") or ""),
        tick=payload.get("tick"),
        events=list(payload.get("events") or []),
        error=str(payload.get("error") or ""),
    )
    output_packet = {
        "packet_type": "runtime.decision_response.v1",
        "packet_version": "runtime.decision_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "battle-summary-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built battle-summary packet.",
        "refs": [],
        "data": {"winner": value.get("winner", ""), "turns": value.get("turns", 0)},
    }]
