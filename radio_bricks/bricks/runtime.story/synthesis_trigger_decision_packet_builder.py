from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.synthesis_trigger_decision_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎬",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.synthesis_trigger_decision_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "synthesis", "trigger", "decision"],
    "description": "Package a story-synthesis trigger decision with threshold math, signal score, priority-event presence, and low-signal force outcome.",
}


def build_synthesis_trigger_decision_packet(
    should_write: bool,
    has_priority_event: bool,
    effective_threshold: int,
    signal_score: float,
    signal_count: int,
    distinct_signal_types: int,
    low_signal_force: bool,
) -> dict[str, Any]:
    return {
        "should_write": bool(should_write),
        "has_priority_event": bool(has_priority_event),
        "effective_threshold": int(effective_threshold),
        "signal_score": float(signal_score),
        "signal_count": int(signal_count),
        "distinct_signal_types": int(distinct_signal_types),
        "low_signal_force": bool(low_signal_force),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_synthesis_trigger_decision_packet(
        should_write=bool(payload.get("should_write")),
        has_priority_event=bool(payload.get("has_priority_event")),
        effective_threshold=int(payload.get("effective_threshold") or 0),
        signal_score=float(payload.get("signal_score") or 0.0),
        signal_count=int(payload.get("signal_count") or 0),
        distinct_signal_types=int(payload.get("distinct_signal_types") or 0),
        low_signal_force=bool(payload.get("low_signal_force")),
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
        "receipt_id": "synthesis-trigger-decision-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built synthesis trigger-decision packet.",
        "refs": [],
        "data": {
            "should_write": value.get("should_write", False),
            "signal_score": value.get("signal_score", 0.0),
            "effective_threshold": value.get("effective_threshold", 0),
        },
    }]
