from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.race_context_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏁",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.race_context_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "race", "context", "broadcast"],
    "description": "Package race commentary context with lap progress, incident memory, battle zones, momentum shifts, and championship implications.",
}


def build_race_context_packet(
    lap_number: int,
    total_laps: int,
    recent_incidents: list[str] | None,
    battle_zones: list[list[int]] | None,
    momentum_shifts: dict[str, int] | None,
    championship_implications: dict[str, str] | None,
    weather_changing: bool,
    safety_car_active: bool,
    overtake_count: int,
) -> dict[str, Any]:
    return {
        "lap_number": int(lap_number),
        "total_laps": int(total_laps),
        "recent_incidents": [str(item) for item in (recent_incidents or [])],
        "battle_zones": [[int(v) for v in item] for item in (battle_zones or [])],
        "momentum_shifts": {str(k): int(v) for k, v in dict(momentum_shifts or {}).items()},
        "championship_implications": {str(k): str(v) for k, v in dict(championship_implications or {}).items()},
        "weather_changing": bool(weather_changing),
        "safety_car_active": bool(safety_car_active),
        "overtake_count": int(overtake_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_race_context_packet(
        lap_number=int(payload.get("lap_number") or 0),
        total_laps=int(payload.get("total_laps") or 0),
        recent_incidents=list(payload.get("recent_incidents") or []),
        battle_zones=list(payload.get("battle_zones") or []),
        momentum_shifts=dict(payload.get("momentum_shifts") or {}),
        championship_implications=dict(payload.get("championship_implications") or {}),
        weather_changing=bool(payload.get("weather_changing")),
        safety_car_active=bool(payload.get("safety_car_active")),
        overtake_count=int(payload.get("overtake_count") or 0),
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
        "receipt_id": "race-context-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built race-context packet.",
        "refs": [],
        "data": {
            "lap_number": value.get("lap_number", 0),
            "battle_zone_count": len(value.get("battle_zones", [])),
            "overtake_count": value.get("overtake_count", 0),
        },
    }]
