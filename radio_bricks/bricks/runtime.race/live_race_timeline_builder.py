from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.race.live_race_timeline_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.race_request.v1"],
    "outputs": ["runtime.race_response.v1"],
    "requires": [],
    "provides": ["runtime.live_race_timeline_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "race", "timeline", "pbp"],
    "description": "Build a live race playback timeline from lap state, standings snapshots, and streamed events.",
}


def build_live_race_timeline_packet(
    current_lap: int,
    total_laps: int,
    live_standings: list[dict[str, Any]] | None,
    live_events: list[dict[str, Any]] | None,
    race_paused: bool = False,
) -> dict[str, Any]:
    standings = [dict(item) for item in (live_standings or [])]
    events = [dict(item) for item in (live_events or [])]
    progress = min(1.0, (int(current_lap) / int(total_laps))) if int(total_laps) > 0 else 0.0
    return {
        "current_lap": int(current_lap),
        "total_laps": int(total_laps),
        "progress": progress,
        "status": "paused" if race_paused else "live",
        "live_standings": standings,
        "event_feed": events[-15:],
        "latest_event": events[-1] if events else None,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_live_race_timeline_packet(
        current_lap=int(payload.get("current_lap") or 0),
        total_laps=int(payload.get("total_laps") or 0),
        live_standings=list(payload.get("live_standings") or []),
        live_events=list(payload.get("live_events") or []),
        race_paused=bool(payload.get("race_paused", False)),
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
        "receipt_id": "live-race-timeline-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built live race timeline packet.",
        "refs": [],
        "data": {"current_lap": value.get("current_lap", 0), "event_count": len(value.get("event_feed", []))},
    }]
