from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.truth_mode_selection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎚️",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.truth_mode_selection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "truth", "mode", "selection"],
    "description": "Package the choice between static compiler truth and live engine truth, including mode-specific headline shaping and query metadata.",
}


def build_truth_mode_selection_packet(
    mode: str,
    used_live_engine: bool,
    query_driven: bool,
    headline: str,
    from_tick: int,
    to_tick: int,
    ticks_advanced: int,
    query_metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "mode": str(mode),
        "used_live_engine": bool(used_live_engine),
        "query_driven": bool(query_driven),
        "headline": str(headline),
        "from_tick": int(from_tick),
        "to_tick": int(to_tick),
        "ticks_advanced": int(ticks_advanced),
        "query_metadata": dict(query_metadata or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_truth_mode_selection_packet(
        mode=str(payload.get("mode") or ""),
        used_live_engine=bool(payload.get("used_live_engine")),
        query_driven=bool(payload.get("query_driven")),
        headline=str(payload.get("headline") or ""),
        from_tick=int(payload.get("from_tick") or 0),
        to_tick=int(payload.get("to_tick") or 0),
        ticks_advanced=int(payload.get("ticks_advanced") or 0),
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
        "receipt_id": "truth-mode-selection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built truth-mode selection packet.",
        "refs": [],
        "data": {
            "mode": value.get("mode", ""),
            "used_live_engine": value.get("used_live_engine", False),
            "ticks_advanced": value.get("ticks_advanced", 0),
        },
    }]
