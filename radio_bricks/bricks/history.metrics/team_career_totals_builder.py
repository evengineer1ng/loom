from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.metrics.team_career_totals_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["history.metrics_request.v1"],
    "outputs": ["history.metrics_response.v1"],
    "requires": [],
    "provides": ["history.team_career_totals_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "metrics", "career", "team"],
    "description": "Aggregate season summaries into team career totals, rates, and title counts.",
}


def build_team_career_totals_packet(team_name: str, season_summaries: list[dict[str, Any]] | None, tick: int) -> dict[str, Any]:
    rows = [dict(row) for row in (season_summaries or []) if str(row.get("team_name") or "") == team_name]
    seasons = len(rows)
    races = sum(int(row.get("races_entered") or 0) for row in rows)
    wins = sum(int(row.get("wins") or 0) for row in rows)
    podiums = sum(int(row.get("podiums") or 0) for row in rows)
    poles = sum(int(row.get("poles") or 0) for row in rows)
    points = sum(float(row.get("total_points") or 0.0) for row in rows)
    championships = sum(1 for row in rows if int(row.get("championship_position") or 999) == 1)
    runner_ups = sum(1 for row in rows if int(row.get("championship_position") or 999) == 2)
    return {
        "team_name": team_name,
        "seasons_entered": seasons,
        "races_entered": races,
        "wins_total": wins,
        "podiums_total": podiums,
        "poles_total": poles,
        "points_total": points,
        "championships_won": championships,
        "runner_up_finishes": runner_ups,
        "win_rate": (wins / races * 100.0) if races > 0 else 0.0,
        "podium_rate": (podiums / races * 100.0) if races > 0 else 0.0,
        "points_per_race_career": (points / races) if races > 0 else 0.0,
        "last_updated_tick": int(tick),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_team_career_totals_packet(
        team_name=str(payload.get("team_name") or ""),
        season_summaries=list(payload.get("season_summaries") or []),
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
        "receipt_id": "team-career-totals-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built team career totals packet.",
        "refs": [],
        "data": {"team_name": value.get("team_name", ""), "championships_won": value.get("championships_won", 0)},
    }]
