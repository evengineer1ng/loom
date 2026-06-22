from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.lifecycle.expedition_completion_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏁",
    "deterministic": True,
    "inputs": ["runtime.lifecycle_request.v1"],
    "outputs": ["runtime.lifecycle_response.v1"],
    "requires": [],
    "provides": ["runtime.expedition_completion_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "lifecycle", "expedition", "completion", "transition"],
    "description": "Package expedition completion output with finished-run state, behavioral axis, profile path, next seed, and optional new-island initialization data.",
}


def build_expedition_completion_packet(
    completed_seed: int,
    ticks_played: int,
    final_tier: str,
    behavioral_axis: str,
    profile_path: str,
    next_seed: int,
    events: list[dict[str, Any]] | None,
    new_island: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "completed_seed": int(completed_seed),
        "ticks_played": int(ticks_played),
        "final_tier": final_tier,
        "behavioral_axis": behavioral_axis,
        "profile_path": profile_path,
        "next_seed": int(next_seed),
        "events": [dict(item) for item in (events or [])],
        "new_island": dict(new_island or {}) if new_island is not None else None,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_expedition_completion_packet(
        completed_seed=int(payload.get("completed_seed") or 0),
        ticks_played=int(payload.get("ticks_played") or 0),
        final_tier=str(payload.get("final_tier") or ""),
        behavioral_axis=str(payload.get("behavioral_axis") or ""),
        profile_path=str(payload.get("profile_path") or ""),
        next_seed=int(payload.get("next_seed") or 0),
        events=list(payload.get("events") or []),
        new_island=payload.get("new_island"),
    )
    output_packet = {
        "packet_type": "runtime.lifecycle_response.v1",
        "packet_version": "runtime.lifecycle_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "expedition-completion-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built expedition-completion packet.",
        "refs": [],
        "data": {"completed_seed": value.get("completed_seed", 0), "next_seed": value.get("next_seed", 0)},
    }]
