from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.race.race_result_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.race_request.v1"],
    "outputs": ["runtime.race_response.v1"],
    "requires": [],
    "provides": ["runtime.race_result_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "race", "result", "packet"],
    "description": "Package race results, event timelines, and telemetry into a single portable race read model.",
}


def build_race_result_packet(race_result: dict[str, Any] | None) -> dict[str, Any]:
    race = dict(race_result or {})
    laps = list(race.get("laps") or [])
    events = list(race.get("race_events") or race.get("events") or [])
    total_laps = len({int(lap.get("lap_number") or 0) for lap in laps}) if laps else 0
    return {
        "race_id": str(race.get("race_id") or ""),
        "league_id": str(race.get("league_id") or ""),
        "league_name": str(race.get("league_name") or ""),
        "track_id": str(race.get("track_id") or ""),
        "track_name": str(race.get("track_name") or ""),
        "season": int(race.get("season") or 0),
        "round_number": int(race.get("round_number") or race.get("round") or 0),
        "final_positions": list(race.get("final_positions") or []),
        "fastest_lap": race.get("fastest_lap"),
        "telemetry": dict(race.get("telemetry") or {}),
        "events": events,
        "total_laps": total_laps,
        "event_count": len(events),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_race_result_packet(dict(payload.get("race_result") or {}))
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
        "receipt_id": "race-result-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built race result packet.",
        "refs": [],
        "data": {"event_count": value.get("event_count", 0), "total_laps": value.get("total_laps", 0)},
    }]
