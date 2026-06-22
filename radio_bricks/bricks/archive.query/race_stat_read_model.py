from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "archive.query.race_stat_read_model",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["archive.query_request.v1"],
    "outputs": ["archive.query_response.v1"],
    "requires": [],
    "provides": ["archive.race_stat_read_model"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["archive", "query", "race", "stats"],
    "description": "Aggregate archived race results into team and driver stat read models.",
}


def build_race_stat_read_model(
    results: list[dict[str, Any]] | None,
    team_names: list[str] | None = None,
    driver_names: list[str] | None = None,
) -> dict[str, Any]:
    team_filter = set(team_names or [])
    driver_filter = set(driver_names or [])
    team_stats: dict[str, dict[str, Any]] = {}
    driver_stats: dict[str, dict[str, Any]] = {}
    seasons_tracked: set[int] = set()
    rows = [dict(result) for result in (results or [])]
    for result in rows:
        season = result.get("season")
        if season is not None:
            seasons_tracked.add(int(season))
        team_best_positions: dict[str, int] = {}
        team_dnf_flags: dict[str, bool] = {}
        for entry in list(result.get("finish_positions") or []):
            item = dict(entry)
            team = str(item.get("team") or "")
            driver = str(item.get("driver") or item.get("driver_name") or "")
            position = int(item.get("position") or 99)
            status = str(item.get("status") or "finished")
            if team and (not team_filter or team in team_filter):
                current = team_best_positions.get(team)
                if current is None or position < current:
                    team_best_positions[team] = position
                if status != "finished":
                    team_dnf_flags[team] = True
            if driver and (not driver_filter or driver in driver_filter):
                stats = driver_stats.setdefault(driver, {"wins": 0, "podiums": 0, "races": 0, "dnfs": 0, "best_finish": None})
                stats["races"] += 1
                if position == 1:
                    stats["wins"] += 1
                if position <= 3:
                    stats["podiums"] += 1
                if status != "finished":
                    stats["dnfs"] += 1
                if stats["best_finish"] is None or position < int(stats["best_finish"]):
                    stats["best_finish"] = position
        for team, best_position in team_best_positions.items():
            stats = team_stats.setdefault(team, {"wins": 0, "podiums": 0, "races": 0, "dnfs": 0, "best_finish": None})
            stats["races"] += 1
            if best_position == 1:
                stats["wins"] += 1
            if best_position <= 3:
                stats["podiums"] += 1
            if team_dnf_flags.get(team, False):
                stats["dnfs"] += 1
            if stats["best_finish"] is None or best_position < int(stats["best_finish"]):
                stats["best_finish"] = best_position
    return {
        "team_stats": team_stats,
        "driver_stats": driver_stats,
        "race_count": len(rows),
        "seasons_tracked": sorted(seasons_tracked),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_race_stat_read_model(
        results=list(payload.get("results") or []),
        team_names=list(payload.get("team_names") or []),
        driver_names=list(payload.get("driver_names") or []),
    )
    output_packet = {
        "packet_type": "archive.query_response.v1",
        "packet_version": "archive.query_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "race-stat-read-model",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Built race stat read model.",
        "refs": [],
        "data": {"race_count": value.get("race_count", 0)},
    }]
