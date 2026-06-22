from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.narrative_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧵",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.narrative_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "narrative", "state", "race"],
    "description": "Package in-race narrative state with leader continuity, active battles, player arc, recovery memory, race phase, and cadence stats.",
}


def build_narrative_state_packet(
    leader: str,
    leader_team: str,
    leader_since_lap: int,
    laps_led: int,
    active_battles: list[list[str]] | None,
    player_arc: str,
    player_arc_detail: str,
    race_phase: str,
    green_flag_laps: int,
    total_commentary_lines: int,
    laps_since_commentary: int,
) -> dict[str, Any]:
    return {
        "leader": str(leader),
        "leader_team": str(leader_team),
        "leader_since_lap": int(leader_since_lap),
        "laps_led": int(laps_led),
        "active_battles": [[str(v) for v in item] for item in (active_battles or [])],
        "player_arc": str(player_arc),
        "player_arc_detail": str(player_arc_detail),
        "race_phase": str(race_phase),
        "green_flag_laps": int(green_flag_laps),
        "total_commentary_lines": int(total_commentary_lines),
        "laps_since_commentary": int(laps_since_commentary),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_narrative_state_packet(
        leader=str(payload.get("leader") or ""),
        leader_team=str(payload.get("leader_team") or ""),
        leader_since_lap=int(payload.get("leader_since_lap") or 0),
        laps_led=int(payload.get("laps_led") or 0),
        active_battles=list(payload.get("active_battles") or []),
        player_arc=str(payload.get("player_arc") or ""),
        player_arc_detail=str(payload.get("player_arc_detail") or ""),
        race_phase=str(payload.get("race_phase") or ""),
        green_flag_laps=int(payload.get("green_flag_laps") or 0),
        total_commentary_lines=int(payload.get("total_commentary_lines") or 0),
        laps_since_commentary=int(payload.get("laps_since_commentary") or 0),
    )
    output_packet = {
        "packet_type": "runtime.story_response.v1",
        "packet_version": "runtime.story_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "narrative-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built narrative-state packet.",
        "refs": [],
        "data": {
            "leader": value.get("leader", ""),
            "player_arc": value.get("player_arc", ""),
            "race_phase": value.get("race_phase", ""),
        },
    }]
