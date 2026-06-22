from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.arc_memory_packet_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.arc_memory_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "memory", "arc"],
    "description": "Build a persistent arc-memory packet for themes, open loops, momentum, and recent pain points.",
}


def build_arc_memory_packet(state: dict[str, Any] | None) -> dict[str, Any]:
    current = dict(state or {})
    return {
        "themes": list(current.get("themes") or []),
        "open_loops": list(current.get("open_loops") or []),
        "last_formula_z_top3": list(current.get("last_formula_z_top3") or []),
        "last_formula_z_leader": str(current.get("last_formula_z_leader") or ""),
        "last_formula_z_news_tick": int(current.get("last_formula_z_news_tick") or 0),
        "recent_pain_points": list(current.get("recent_pain_points") or []),
        "momentum": str(current.get("momentum") or "unknown"),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = build_arc_memory_packet(dict(input_packet.get("payload") or {}))
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
        "receipt_id": "arc-memory-packet",
        "brick_id": CONCEPT["id"],
        "kind": "state",
        "label": "Built arc memory packet.",
        "refs": [],
        "data": {"themes": len(value.get("themes", [])), "open_loops": len(value.get("open_loops", []))},
    }]
