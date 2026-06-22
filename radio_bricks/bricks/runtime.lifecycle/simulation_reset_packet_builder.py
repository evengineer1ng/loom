from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.lifecycle.simulation_reset_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "♻️",
    "deterministic": True,
    "inputs": ["runtime.lifecycle_request.v1"],
    "outputs": ["runtime.lifecycle_response.v1"],
    "requires": [],
    "provides": ["runtime.simulation_reset_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "lifecycle", "reset", "simulation", "island"],
    "description": "Package simulation reset output with profile deletion state, requested seed, and post-reset island initialization data.",
}


def build_simulation_reset_packet(
    profile_deleted: bool | None,
    new_seed: int,
    new_island: dict[str, Any] | None,
    events: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "profile_deleted": profile_deleted if profile_deleted is None else bool(profile_deleted),
        "new_seed": int(new_seed),
        "new_island": dict(new_island or {}) if new_island is not None else None,
        "events": [dict(item) for item in (events or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_simulation_reset_packet(
        profile_deleted=payload.get("profile_deleted"),
        new_seed=int(payload.get("new_seed") or 0),
        new_island=payload.get("new_island"),
        events=list(payload.get("events") or []),
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
        "receipt_id": "simulation-reset-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built simulation-reset packet.",
        "refs": [],
        "data": {"new_seed": value.get("new_seed", 0), "profile_deleted": value.get("profile_deleted", None)},
    }]
