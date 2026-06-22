from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.forkuniverse_query_request_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📻",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.forkuniverse_query_request_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "forkuniverse", "query", "request"],
    "description": "Package a ForkUniverse truth query request with observation mode, since policy, event caps, and inclusion flags.",
}


def build_forkuniverse_query_request_packet(
    universe_id: str,
    mode: str,
    since: str,
    since_timestamp: str | None,
    max_events: int,
    heat_threshold: float,
    include_threads: bool,
    include_resolved_predictions: bool,
    include_new_predictions: bool,
    now_timestamp: str | None,
) -> dict[str, Any]:
    packet = {
        "universe_id": universe_id,
        "mode": mode,
        "since": since,
        "max_events": int(max_events),
        "heat_threshold": float(heat_threshold),
        "include_threads": bool(include_threads),
        "include_resolved_predictions": bool(include_resolved_predictions),
        "include_new_predictions": bool(include_new_predictions),
    }
    if since_timestamp:
        packet["since_timestamp"] = since_timestamp
    if now_timestamp:
        packet["now_timestamp"] = now_timestamp
    return packet


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_query_request_packet(
        universe_id=str(payload.get("universe_id") or ""),
        mode=str(payload.get("mode") or ""),
        since=str(payload.get("since") or ""),
        since_timestamp=payload.get("since_timestamp"),
        max_events=int(payload.get("max_events") or 0),
        heat_threshold=float(payload.get("heat_threshold") or 0.0),
        include_threads=bool(payload.get("include_threads")),
        include_resolved_predictions=bool(payload.get("include_resolved_predictions")),
        include_new_predictions=bool(payload.get("include_new_predictions")),
        now_timestamp=payload.get("now_timestamp"),
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
        "receipt_id": "forkuniverse-query-request-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse query-request packet.",
        "refs": [],
        "data": {"mode": value.get("mode", ""), "max_events": value.get("max_events", 0)},
    }]
