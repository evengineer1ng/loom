from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.mission_event_detector_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🛰️",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.mission_event_detector_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "mission", "event", "detector"],
    "description": "Package mission-event detection over sequential telemetry snapshots for milestones like launch, staging, orbit, reentry, landing, or anomalies.",
}


def build_mission_event_detector_packet(
    previous_snapshot: dict[str, Any] | None,
    current_snapshot: dict[str, Any] | None,
    detected_events: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "previous_snapshot": dict(previous_snapshot or {}),
        "current_snapshot": dict(current_snapshot or {}),
        "detected_events": [dict(item) for item in (detected_events or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_mission_event_detector_packet(
        previous_snapshot=dict(payload.get("previous_snapshot") or {}),
        current_snapshot=dict(payload.get("current_snapshot") or {}),
        detected_events=list(payload.get("detected_events") or []),
    )
    output_packet = {
        "packet_type": "runtime.decision_response.v1",
        "packet_version": "runtime.decision_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "mission-event-detector-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built mission-event detector packet.",
        "refs": [],
        "data": {
            "detected_event_count": len(value.get("detected_events", [])),
        },
    }]
