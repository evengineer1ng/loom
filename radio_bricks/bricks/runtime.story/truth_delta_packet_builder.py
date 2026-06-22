from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.truth_delta_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌡️",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.truth_delta_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "truth", "delta", "absence"],
    "description": "Package a ForkUniverse truth delta spanning ticks with new events, thread deltas, prediction settlements, headline, and heat.",
}


def build_truth_delta_packet(
    universe_id: str,
    from_tick: int,
    to_tick: int,
    headline: str,
    heat: float,
    new_events: list[dict[str, Any]] | None,
    thread_deltas: list[dict[str, Any]] | None,
    opened_threads: list[dict[str, Any]] | None,
    resolved_threads: list[dict[str, Any]] | None,
    settled_predictions: list[dict[str, Any]] | None,
    opened_predictions: list[dict[str, Any]] | None,
    prediction_scorecard: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "universe_id": universe_id,
        "from_tick": int(from_tick),
        "to_tick": int(to_tick),
        "headline": headline,
        "heat": float(heat),
        "new_events": [dict(item) for item in (new_events or [])],
        "thread_deltas": [dict(item) for item in (thread_deltas or [])],
        "opened_threads": [dict(item) for item in (opened_threads or [])],
        "resolved_threads": [dict(item) for item in (resolved_threads or [])],
        "settled_predictions": [dict(item) for item in (settled_predictions or [])],
        "opened_predictions": [dict(item) for item in (opened_predictions or [])],
        "prediction_scorecard": dict(prediction_scorecard or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_truth_delta_packet(
        universe_id=str(payload.get("universe_id") or ""),
        from_tick=int(payload.get("from_tick") or 0),
        to_tick=int(payload.get("to_tick") or 0),
        headline=str(payload.get("headline") or ""),
        heat=float(payload.get("heat") or 0.0),
        new_events=list(payload.get("new_events") or []),
        thread_deltas=list(payload.get("thread_deltas") or []),
        opened_threads=list(payload.get("opened_threads") or []),
        resolved_threads=list(payload.get("resolved_threads") or []),
        settled_predictions=list(payload.get("settled_predictions") or []),
        opened_predictions=list(payload.get("opened_predictions") or []),
        prediction_scorecard=dict(payload.get("prediction_scorecard") or {}),
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
        "receipt_id": "truth-delta-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built truth-delta packet.",
        "refs": [],
        "data": {"from_tick": value.get("from_tick", 0), "to_tick": value.get("to_tick", 0)},
    }]
