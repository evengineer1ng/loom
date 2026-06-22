from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.ftb_narrator_state_snapshot_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.ftb_narrator_state_snapshot"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "ftb", "snapshot"],
    "description": "Build a narrator-facing FTB state snapshot from player, league, budget, morale, and recent trend state.",
}


def build_ftb_narrator_state_snapshot(
    tick: int,
    player_team: str,
    player_role: str,
    league_tier: int,
    league_name: str,
    championship_position: int,
    championship_points: float,
    budget: int,
    budget_status: str,
    driver_names: list[str] | None,
    morale_level: str,
    organizational_posture: str,
    has_financial_crisis: bool,
    has_morale_crisis: bool,
    current_day: int,
    current_season: int,
    environment_crowded: bool,
    recent_trend: str,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "player_team": player_team,
        "player_role": player_role,
        "league_tier": int(league_tier),
        "league_name": league_name,
        "championship_position": int(championship_position),
        "championship_points": float(championship_points),
        "budget": int(budget),
        "budget_status": budget_status,
        "driver_names": list(driver_names or []),
        "staff_names": [],
        "car_exists": True,
        "morale_level": morale_level,
        "organizational_posture": organizational_posture,
        "has_financial_crisis": bool(has_financial_crisis),
        "has_morale_crisis": bool(has_morale_crisis),
        "current_day": int(current_day),
        "current_season": int(current_season),
        "environment_crowded": bool(environment_crowded),
        "recent_trend": recent_trend,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_ftb_narrator_state_snapshot(
        tick=int(payload.get("tick") or 0),
        player_team=str(payload.get("player_team") or ""),
        player_role=str(payload.get("player_role") or "Manager"),
        league_tier=int(payload.get("league_tier") or 1),
        league_name=str(payload.get("league_name") or "Unknown"),
        championship_position=int(payload.get("championship_position") or 0),
        championship_points=float(payload.get("championship_points") or 0.0),
        budget=int(payload.get("budget") or 0),
        budget_status=str(payload.get("budget_status") or "unknown"),
        driver_names=list(payload.get("driver_names") or []),
        morale_level=str(payload.get("morale_level") or "unknown"),
        organizational_posture=str(payload.get("organizational_posture") or "unknown"),
        has_financial_crisis=bool(payload.get("has_financial_crisis", False)),
        has_morale_crisis=bool(payload.get("has_morale_crisis", False)),
        current_day=int(payload.get("current_day") or 0),
        current_season=int(payload.get("current_season") or 0),
        environment_crowded=bool(payload.get("environment_crowded", False)),
        recent_trend=str(payload.get("recent_trend") or "unknown"),
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
        "receipt_id": "ftb-narrator-state-snapshot",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built FTB narrator state snapshot.",
        "refs": [],
        "data": {"player_team": value.get("player_team", ""), "budget_status": value.get("budget_status", "")},
    }]
