from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.metrics.active_streak_state_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["history.metrics_request.v1"],
    "outputs": ["history.metrics_response.v1"],
    "requires": [],
    "provides": ["history.active_streak_state"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "metrics", "streaks", "race"],
    "description": "Update points, podium, win, DNF, and top-5 streak state from a fresh race result.",
}


def build_active_streak_state(
    current: dict[str, Any] | None,
    finish_position: int,
    race_id: str,
    season: int,
    tick: int,
    scored_points: bool = True,
    was_dnf: bool = False,
) -> dict[str, Any]:
    source = dict(current or {})
    points_streak = int(source.get("current_points_streak") or 0)
    podium_streak = int(source.get("current_podium_streak") or 0)
    win_streak = int(source.get("current_win_streak") or 0)
    dnf_streak = int(source.get("current_dnf_streak") or 0)
    top5_streak = int(source.get("consecutive_top5_finishes") or 0)
    longest_points = int(source.get("longest_points_streak_ever") or 0)
    longest_win = int(source.get("longest_win_streak_ever") or 0)
    longest_podium = int(source.get("longest_podium_streak_ever") or 0)

    if scored_points:
        points_streak += 1
        dnf_streak = 0
        longest_points = max(longest_points, points_streak)
    else:
        points_streak = 0

    if finish_position == 1:
        win_streak += 1
        podium_streak += 1
        longest_win = max(longest_win, win_streak)
        longest_podium = max(longest_podium, podium_streak)
    else:
        win_streak = 0
        if finish_position <= 3:
            podium_streak += 1
            longest_podium = max(longest_podium, podium_streak)
        else:
            podium_streak = 0

    dnf_streak = dnf_streak + 1 if was_dnf else 0
    top5_streak = top5_streak + 1 if finish_position <= 5 else 0

    return {
        "current_points_streak": points_streak,
        "current_podium_streak": podium_streak,
        "current_win_streak": win_streak,
        "current_dnf_streak": dnf_streak,
        "consecutive_top5_finishes": top5_streak,
        "longest_points_streak_ever": longest_points,
        "longest_win_streak_ever": longest_win,
        "longest_podium_streak_ever": longest_podium,
        "last_points_finish_race": race_id if scored_points else source.get("last_points_finish_race"),
        "last_points_finish_season": season if scored_points else source.get("last_points_finish_season"),
        "last_win_race": race_id if finish_position == 1 else source.get("last_win_race"),
        "last_win_season": season if finish_position == 1 else source.get("last_win_season"),
        "last_podium_race": race_id if finish_position <= 3 else source.get("last_podium_race"),
        "last_podium_season": season if finish_position <= 3 else source.get("last_podium_season"),
        "last_updated_tick": int(tick),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_active_streak_state(
        current=dict(payload.get("current") or {}),
        finish_position=int(payload.get("finish_position") or 0),
        race_id=str(payload.get("race_id") or ""),
        season=int(payload.get("season") or 0),
        tick=int(payload.get("tick") or 0),
        scored_points=bool(payload.get("scored_points", True)),
        was_dnf=bool(payload.get("was_dnf", False)),
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
        "receipt_id": "active-streak-state",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built active streak state.",
        "refs": [],
        "data": {"points_streak": value.get("current_points_streak", 0), "win_streak": value.get("current_win_streak", 0)},
    }]
