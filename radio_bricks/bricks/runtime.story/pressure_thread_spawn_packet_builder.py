from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.pressure_thread_spawn_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌋",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.pressure_thread_spawn_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "pressure", "thread", "spawn"],
    "description": "Package ambient pressure-driven thread spawning with thresholds, chance gates, active-thread budget, chosen domain, and participant picks.",
}


def build_pressure_thread_spawn_packet(
    tick: int,
    axis_id: str,
    threshold: float,
    spawn_chance: float,
    active_thread_budget: int,
    active_thread_count: int,
    domain: str,
    participant_ids: list[str] | None,
    spawned_thread: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "axis_id": str(axis_id),
        "threshold": float(threshold),
        "spawn_chance": float(spawn_chance),
        "active_thread_budget": int(active_thread_budget),
        "active_thread_count": int(active_thread_count),
        "domain": str(domain),
        "participant_ids": [str(item) for item in (participant_ids or [])],
        "spawned_thread": dict(spawned_thread or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_pressure_thread_spawn_packet(
        tick=int(payload.get("tick") or 0),
        axis_id=str(payload.get("axis_id") or ""),
        threshold=float(payload.get("threshold") or 0.0),
        spawn_chance=float(payload.get("spawn_chance") or 0.0),
        active_thread_budget=int(payload.get("active_thread_budget") or 0),
        active_thread_count=int(payload.get("active_thread_count") or 0),
        domain=str(payload.get("domain") or ""),
        participant_ids=list(payload.get("participant_ids") or []),
        spawned_thread=dict(payload.get("spawned_thread") or {}),
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
        "receipt_id": "pressure-thread-spawn-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built pressure-thread-spawn packet.",
        "refs": [],
        "data": {
            "axis_id": value.get("axis_id", ""),
            "domain": value.get("domain", ""),
            "spawned": bool(value.get("spawned_thread")),
        },
    }]
