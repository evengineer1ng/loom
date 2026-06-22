from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "music.flow.break_schedule_builder",
    "kind": "planner",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["music.flow_request.v1"],
    "outputs": ["music.flow_response.v1"],
    "requires": [],
    "provides": ["music.flow_break_schedule"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["music", "flow", "break", "schedule"],
    "description": "Build song-flow and talk-break schedule bounds from Flows configuration.",
}


def build_break_schedule(config: dict[str, Any] | None) -> dict[str, Any]:
    cfg = dict(config or {})
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "reaction_frequency": float(cfg.get("reaction_frequency") or 0.2),
        "min_reaction_gap_sec": float(cfg.get("min_reaction_gap_sec") or 20),
        "flow_songs_min": int(cfg.get("flow_songs_min") or 1),
        "flow_songs_max": int(cfg.get("flow_songs_max") or 3),
        "flow_songs_random": bool(cfg.get("flow_songs_random", True)),
        "talk_segments_min": int(cfg.get("talk_segments_min") or 2),
        "talk_segments_max": int(cfg.get("talk_segments_max") or 5),
        "talk_segments_random": bool(cfg.get("talk_segments_random", True)),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = build_break_schedule(dict(input_packet.get("payload") or {}))
    output_packet = {
        "packet_type": "music.flow_response.v1",
        "packet_version": "music.flow_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "break-schedule-builder",
        "brick_id": CONCEPT["id"],
        "kind": "plan",
        "label": "Built flow break schedule.",
        "refs": [],
        "data": {"enabled": value.get("enabled", False), "flow_span": [value.get("flow_songs_min", 0), value.get("flow_songs_max", 0)]},
    }]
