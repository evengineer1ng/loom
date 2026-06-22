from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.metrics.team_peak_valley_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["history.metrics_request.v1"],
    "outputs": ["history.metrics_response.v1"],
    "requires": [],
    "provides": ["history.team_peak_valley_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "metrics", "peak", "valley", "team"],
    "description": "Summarize a team's best season, worst season, best points year, and win drought.",
}


def build_team_peak_valley_packet(team_name: str, season_summaries: list[dict[str, Any]] | None, tick: int) -> dict[str, Any]:
    rows = [dict(row) for row in (season_summaries or []) if str(row.get("team_name") or "") == team_name]
    with_positions = [row for row in rows if row.get("championship_position") is not None]
    best = min(with_positions, key=lambda row: (int(row.get("championship_position") or 999), -float(row.get("total_points") or 0.0)), default=None)
    worst = max(with_positions, key=lambda row: (int(row.get("championship_position") or -1), -float(-(float(row.get("total_points") or 0.0)))), default=None)
    best_points = max(rows, key=lambda row: float(row.get("total_points") or 0.0), default=None)
    current_season = max((int(row.get("season") or 0) for row in rows), default=0)
    win_seasons = [int(row.get("season") or 0) for row in rows if int(row.get("wins") or 0) > 0]
    current_win_drought = current_season - max(win_seasons) if win_seasons else len(rows)
    return {
        "team_name": team_name,
        "best_season_finish": int(best.get("championship_position")) if best else None,
        "best_season_finish_year": int(best.get("season")) if best else None,
        "worst_season_finish": int(worst.get("championship_position")) if worst else None,
        "worst_season_finish_year": int(worst.get("season")) if worst else None,
        "best_single_season_points": float(best_points.get("total_points") or 0.0) if best_points else 0.0,
        "best_season_points_year": int(best_points.get("season")) if best_points else None,
        "current_win_drought": current_win_drought,
        "last_updated_tick": int(tick),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_team_peak_valley_packet(
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
        "receipt_id": "team-peak-valley-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built team peak-valley packet.",
        "refs": [],
        "data": {"team_name": value.get("team_name", ""), "current_win_drought": value.get("current_win_drought", 0)},
    }]
