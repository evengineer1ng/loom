from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.metrics.driver_career_stat_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["history.metrics_request.v1"],
    "outputs": ["history.metrics_response.v1"],
    "requires": [],
    "provides": ["history.driver_career_stat_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "metrics", "career", "driver"],
    "description": "Build driver career totals from archived finish positions, including wins, podiums, and points-per-race.",
}


def build_driver_career_stat_packet(driver_name: str, race_results: list[dict[str, Any]] | None, tick: int) -> dict[str, Any]:
    starts = 0
    wins = 0
    podiums = 0
    points = 0.0
    seasons: set[int] = set()
    teams: set[str] = set()
    for race in race_results or []:
        season = int(dict(race).get("season") or 0)
        for result in list(dict(race).get("finish_positions") or []):
            entry = dict(result)
            name = str(entry.get("driver_name") or entry.get("driver") or "")
            if name != driver_name:
                continue
            starts += 1
            seasons.add(season)
            if entry.get("team"):
                teams.add(str(entry.get("team")))
            position = int(entry.get("position") or 99)
            if position == 1:
                wins += 1
            if position <= 3:
                podiums += 1
            if position <= 10:
                points += max(0, 25 - (position - 1) * 2)
    return {
        "driver_name": driver_name,
        "career_starts": starts,
        "career_wins": wins,
        "career_podiums": podiums,
        "career_points": points,
        "career_teams_driven_for": len(teams),
        "win_rate_career": (wins / starts * 100.0) if starts > 0 else 0.0,
        "podium_rate_career": (podiums / starts * 100.0) if starts > 0 else 0.0,
        "points_per_race_career": (points / starts) if starts > 0 else 0.0,
        "seasons_active": len(seasons),
        "last_updated_tick": int(tick),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_driver_career_stat_packet(
        driver_name=str(payload.get("driver_name") or ""),
        race_results=list(payload.get("race_results") or []),
        tick=int(payload.get("tick") or 0),
    )
    output_packet = {
        "packet_type": "history.metrics_response.v1",
        "packet_version": "history.metrics_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "driver-career-stat-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built driver career stat packet.",
        "refs": [],
        "data": {"driver_name": value.get("driver_name", ""), "career_starts": value.get("career_starts", 0)},
    }]
