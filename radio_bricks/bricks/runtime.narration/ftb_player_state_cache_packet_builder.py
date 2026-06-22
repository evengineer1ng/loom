from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.ftb_player_state_cache_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.ftb_player_state_cache_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "ftb", "player-state", "cache"],
    "description": "Build the compact player-state cache packet used by narrator queries and event pools.",
}


def build_ftb_player_state_cache_packet(
    budget: float,
    championship_position: int,
    points: float,
    morale: float,
    reputation: float,
    tier: int,
    current_day: int,
    season: int,
) -> dict[str, Any]:
    return {
        "budget": float(budget),
        "championship_position": int(championship_position),
        "points": float(points),
        "morale": float(morale),
        "reputation": float(reputation),
        "tier": int(tier),
        "current_day": int(current_day),
        "season": int(season),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_ftb_player_state_cache_packet(
        budget=float(payload.get("budget") or 0.0),
        championship_position=int(payload.get("championship_position") or 0),
        points=float(payload.get("points") or 0.0),
        morale=float(payload.get("morale") or 50.0),
        reputation=float(payload.get("reputation") or 0.0),
        tier=int(payload.get("tier") or 1),
        current_day=int(payload.get("current_day") or 0),
        season=int(payload.get("season") or 0),
    )
    output_packet = {
        "packet_type": "runtime.narration_response.v1",
        "packet_version": "runtime.narration_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "ftb-player-state-cache",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built FTB player-state cache packet.",
        "refs": [],
        "data": {"season": value.get("season", 0), "championship_position": value.get("championship_position", 0)},
    }]
