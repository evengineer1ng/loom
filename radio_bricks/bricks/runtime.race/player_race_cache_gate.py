from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.race.player_race_cache_gate",
    "kind": "gate",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.race_request.v1"],
    "outputs": ["runtime.race_response.v1"],
    "requires": [],
    "provides": ["runtime.player_race_cache_decision"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "race", "cache", "gate"],
    "description": "Decide whether a race artifact belongs to the player context before caching or playback.",
}


def build_player_race_cache_decision(race_result: dict[str, Any] | None, player_league_id: str | None, leagues: list[dict[str, Any]] | None) -> dict[str, Any]:
    race = dict(race_result or {})
    target_league_id = str(player_league_id or "")
    league_name = str(race.get("league_name") or "")
    matched = False
    matched_league_name = ""
    for league in leagues or []:
        current_id = str(league.get("league_id") or "")
        current_name = str(league.get("name") or "")
        if current_id == target_league_id and current_name == league_name:
            matched = True
            matched_league_name = current_name
            break
    return {
        "cache_allowed": matched and bool(race),
        "player_league_id": target_league_id,
        "race_id": str(race.get("race_id") or ""),
        "race_league_name": league_name,
        "matched_league_name": matched_league_name,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_player_race_cache_decision(
        race_result=dict(payload.get("race_result") or {}),
        player_league_id=str(payload.get("player_league_id") or ""),
        leagues=list(payload.get("leagues") or []),
    )
    output_packet = {
        "packet_type": "runtime.race_response.v1",
        "packet_version": "runtime.race_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "player-race-cache-gate",
        "brick_id": CONCEPT["id"],
        "kind": "decision",
        "label": "Evaluated player-race cache gate.",
        "refs": [],
        "data": {"cache_allowed": value.get("cache_allowed", False)},
    }]
