from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.forkuniverse_truth_result_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🛰️",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.forkuniverse_truth_result_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "forkuniverse", "truth", "result"],
    "description": "Package a ForkUniverse truth computation result with universe time, elapsed sim time, headline, events, threads, predictions, heat, and query metadata.",
}


def build_forkuniverse_truth_result_packet(
    universe_id: str,
    mode: str,
    universe_time: str,
    elapsed_sim_time: str,
    headline: str,
    events: list[dict[str, Any]] | None,
    threads: list[dict[str, Any]] | None,
    resolved_predictions: list[dict[str, Any]] | None,
    new_predictions: list[dict[str, Any]] | None,
    heat: float,
    query_metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "universe_id": universe_id,
        "mode": mode,
        "universe_time": universe_time,
        "elapsed_sim_time": elapsed_sim_time,
        "headline": headline,
        "events": [dict(item) for item in (events or [])],
        "threads": [dict(item) for item in (threads or [])],
        "resolved_predictions": [dict(item) for item in (resolved_predictions or [])],
        "new_predictions": [dict(item) for item in (new_predictions or [])],
        "heat": float(heat),
        "query_metadata": dict(query_metadata or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_truth_result_packet(
        universe_id=str(payload.get("universe_id") or ""),
        mode=str(payload.get("mode") or ""),
        universe_time=str(payload.get("universe_time") or ""),
        elapsed_sim_time=str(payload.get("elapsed_sim_time") or ""),
        headline=str(payload.get("headline") or ""),
        events=list(payload.get("events") or []),
        threads=list(payload.get("threads") or []),
        resolved_predictions=list(payload.get("resolved_predictions") or []),
        new_predictions=list(payload.get("new_predictions") or []),
        heat=float(payload.get("heat") or 0.0),
        query_metadata=dict(payload.get("query_metadata") or {}),
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
        "receipt_id": "forkuniverse-truth-result-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse truth-result packet.",
        "refs": [],
        "data": {"headline": value.get("headline", ""), "heat": value.get("heat", 0.0)},
    }]
