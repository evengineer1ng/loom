from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.race.race_event_batch_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏁",
    "deterministic": True,
    "inputs": ["runtime.race_request.v1"],
    "outputs": ["runtime.race_response.v1"],
    "requires": [],
    "provides": ["runtime.race_event_batch_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "race", "events", "batch", "heat"],
    "description": "Package prepared race-event batches with stale filtering, finish-event preservation, priority sorting, and per-tick cap application.",
}


def build_race_event_batch_packet(
    race_state: str,
    raw_events: list[dict[str, Any]] | None,
    prepared_events: list[dict[str, Any]] | None,
    max_age_sec: float,
    max_events_per_tick: int,
) -> dict[str, Any]:
    return {
        "race_state": str(race_state),
        "raw_events": [dict(item) for item in (raw_events or [])],
        "prepared_events": [dict(item) for item in (prepared_events or [])],
        "max_age_sec": float(max_age_sec),
        "max_events_per_tick": int(max_events_per_tick),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_race_event_batch_packet(
        race_state=str(payload.get("race_state") or ""),
        raw_events=list(payload.get("raw_events") or []),
        prepared_events=list(payload.get("prepared_events") or []),
        max_age_sec=float(payload.get("max_age_sec") or 0.0),
        max_events_per_tick=int(payload.get("max_events_per_tick") or 0),
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
        "receipt_id": "race-event-batch-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built race-event batch packet.",
        "refs": [],
        "data": {
            "race_state": value.get("race_state", ""),
            "prepared_count": len(value.get("prepared_events", [])),
            "max_events_per_tick": value.get("max_events_per_tick", 0),
        },
    }]
