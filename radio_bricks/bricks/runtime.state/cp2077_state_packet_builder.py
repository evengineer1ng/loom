from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.cp2077_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌆",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.cp2077_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "cp2077", "snapshot", "game"],
    "description": "Package a Cyberpunk 2077 game-state snapshot with health, combat, wanted level, location, quest, vehicle, and nearby world context.",
}


def build_cp2077_state_packet(
    player_name: str,
    health_pct: float,
    is_alive: bool,
    in_combat: bool,
    wanted_level: int,
    district: str,
    location: str,
    active_quest: str,
    in_vehicle: bool,
    nearby_poi: str,
) -> dict[str, Any]:
    return {
        "player_name": str(player_name),
        "health_pct": float(health_pct),
        "is_alive": bool(is_alive),
        "in_combat": bool(in_combat),
        "wanted_level": int(wanted_level),
        "district": str(district),
        "location": str(location),
        "active_quest": str(active_quest),
        "in_vehicle": bool(in_vehicle),
        "nearby_poi": str(nearby_poi),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_cp2077_state_packet(
        player_name=str(payload.get("player_name") or ""),
        health_pct=float(payload.get("health_pct") or 0.0),
        is_alive=bool(payload.get("is_alive")),
        in_combat=bool(payload.get("in_combat")),
        wanted_level=int(payload.get("wanted_level") or 0),
        district=str(payload.get("district") or ""),
        location=str(payload.get("location") or ""),
        active_quest=str(payload.get("active_quest") or ""),
        in_vehicle=bool(payload.get("in_vehicle")),
        nearby_poi=str(payload.get("nearby_poi") or ""),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "cp2077-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built CP2077-state packet.",
        "refs": [],
        "data": {
            "player_name": value.get("player_name", ""),
            "in_combat": value.get("in_combat", False),
            "location": value.get("location", ""),
        },
    }]
