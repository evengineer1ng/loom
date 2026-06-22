from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "progression.outcome.outcome_view_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔭",
    "deterministic": True,
    "inputs": ["progression.outcome_request.v1"],
    "outputs": ["progression.outcome_response.v1"],
    "requires": [],
    "provides": ["progression.outcome_view_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["progression", "outcome", "view", "description", "narrative"],
    "description": "Package the described outcome-band surface returned to callers as a portable narrative outcome view.",
}


def build_outcome_view_packet(
    outcome: dict[str, Any] | None,
) -> dict[str, Any]:
    return dict(outcome or {})


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_outcome_view_packet(
        outcome=dict(payload.get("outcome") or {}),
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
        "receipt_id": "outcome-view-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built outcome-view packet.",
        "refs": [],
        "data": {"field_count": len(value)},
    }]
