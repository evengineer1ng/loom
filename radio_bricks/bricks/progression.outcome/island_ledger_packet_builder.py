from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "progression.outcome.island_ledger_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📊",
    "deterministic": True,
    "inputs": ["progression.outcome_request.v1"],
    "outputs": ["progression.outcome_response.v1"],
    "requires": [],
    "provides": ["progression.island_ledger_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["progression", "outcome", "ledger", "indices", "normalization"],
    "description": "Package the Neikos island ledger with raw axes, normalized values, and derived stability, civilization, and tension indices.",
}


def build_island_ledger_packet(
    raw: dict[str, float] | None,
    normalized: dict[str, float] | None,
    stability_index: float,
    civilization_index: float,
    tension_index: float,
) -> dict[str, Any]:
    return {
        "raw": {str(key): float(value) for key, value in (raw or {}).items()},
        "normalized": {str(key): float(value) for key, value in (normalized or {}).items()},
        "stability_index": float(stability_index),
        "civilization_index": float(civilization_index),
        "tension_index": float(tension_index),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_island_ledger_packet(
        raw=dict(payload.get("raw") or {}),
        normalized=dict(payload.get("normalized") or {}),
        stability_index=float(payload.get("stability_index") or 0.0),
        civilization_index=float(payload.get("civilization_index") or 0.0),
        tension_index=float(payload.get("tension_index") or 0.0),
    )
    output_packet = {
        "packet_type": "progression.outcome_response.v1",
        "packet_version": "progression.outcome_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "island-ledger-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built island-ledger packet.",
        "refs": [],
        "data": {"stability_index": value.get("stability_index", 0.0), "tension_index": value.get("tension_index", 0.0)},
    }]
