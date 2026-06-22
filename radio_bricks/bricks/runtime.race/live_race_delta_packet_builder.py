from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.race.live_race_delta_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏎️",
    "deterministic": True,
    "inputs": ["runtime.race_request.v1"],
    "outputs": ["runtime.race_response.v1"],
    "requires": [],
    "provides": ["runtime.live_race_delta_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "race", "live", "delta", "telemetry"],
    "description": "Package synthesized live race deltas from standings and telemetry snapshots such as incidents, position shifts, gap changes, speed spikes, or sector changes.",
}


def build_live_race_delta_packet(
    race_state: str,
    previous_snapshot: dict[str, Any] | None,
    current_snapshot: dict[str, Any] | None,
    synthesized_events: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "race_state": str(race_state),
        "previous_snapshot": dict(previous_snapshot or {}),
        "current_snapshot": dict(current_snapshot or {}),
        "synthesized_events": [dict(item) for item in (synthesized_events or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_live_race_delta_packet(
        race_state=str(payload.get("race_state") or ""),
        previous_snapshot=dict(payload.get("previous_snapshot") or {}),
        current_snapshot=dict(payload.get("current_snapshot") or {}),
        synthesized_events=list(payload.get("synthesized_events") or []),
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
        "receipt_id": "live-race-delta-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built live-race delta packet.",
        "refs": [],
        "data": {
            "race_state": value.get("race_state", ""),
            "event_count": len(value.get("synthesized_events", [])),
        },
    }]
