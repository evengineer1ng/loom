from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.scored_race_event_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏎️",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.scored_race_event_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "race", "event", "scored"],
    "description": "Package a classified race event with base weight, final weight, driver/team identity, player-team flag, and metadata for beat selection.",
}


def build_scored_race_event_packet(
    event_class: str,
    base_weight: float,
    final_weight: float,
    lap: int,
    driver: str,
    team: str,
    is_player_team: bool,
    description: str,
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "event_class": str(event_class),
        "base_weight": float(base_weight),
        "final_weight": float(final_weight),
        "lap": int(lap),
        "driver": str(driver),
        "team": str(team),
        "is_player_team": bool(is_player_team),
        "description": str(description),
        "metadata": dict(metadata or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_scored_race_event_packet(
        event_class=str(payload.get("event_class") or ""),
        base_weight=float(payload.get("base_weight") or 0.0),
        final_weight=float(payload.get("final_weight") or 0.0),
        lap=int(payload.get("lap") or 0),
        driver=str(payload.get("driver") or ""),
        team=str(payload.get("team") or ""),
        is_player_team=bool(payload.get("is_player_team")),
        description=str(payload.get("description") or ""),
        metadata=dict(payload.get("metadata") or {}),
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
        "receipt_id": "scored-race-event-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built scored race-event packet.",
        "refs": [],
        "data": {
            "event_class": value.get("event_class", ""),
            "driver": value.get("driver", ""),
            "final_weight": value.get("final_weight", 0.0),
        },
    }]
