from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.race.race_heat_resolution_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔥",
    "deterministic": True,
    "inputs": ["runtime.race_request.v1"],
    "outputs": ["runtime.race_response.v1"],
    "requires": [],
    "provides": ["runtime.race_heat_resolution_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "race", "heat", "resolution", "priority"],
    "description": "Package race heat resolution from state and event types into a simplified urgency level for downstream narration or routing.",
}


def build_race_heat_resolution_packet(
    race_state: str,
    event_types: list[str] | None,
    heat_level: int,
) -> dict[str, Any]:
    return {
        "race_state": str(race_state),
        "event_types": [str(item) for item in (event_types or [])],
        "heat_level": int(heat_level),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_race_heat_resolution_packet(
        race_state=str(payload.get("race_state") or ""),
        event_types=list(payload.get("event_types") or []),
        heat_level=int(payload.get("heat_level") or 0),
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
        "receipt_id": "race-heat-resolution-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built race-heat resolution packet.",
        "refs": [],
        "data": {
            "race_state": value.get("race_state", ""),
            "heat_level": value.get("heat_level", 0),
            "event_type_count": len(value.get("event_types", [])),
        },
    }]
