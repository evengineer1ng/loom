from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "progression.outcome.narrative_role_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎭",
    "deterministic": True,
    "inputs": ["progression.outcome_request.v1"],
    "outputs": ["progression.outcome_response.v1"],
    "requires": [],
    "provides": ["progression.narrative_role_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["progression", "outcome", "role", "narrative", "label"],
    "description": "Package the canonical narrative role label for a Neikos outcome band.",
}


def build_narrative_role_packet(band_id: int, role_label: str) -> dict[str, Any]:
    return {"band_id": int(band_id), "role_label": role_label}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_narrative_role_packet(
        band_id=int(payload.get("band_id") or 0),
        role_label=str(payload.get("role_label") or ""),
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
        "receipt_id": "narrative-role-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built narrative role packet.",
        "refs": [],
        "data": {"band_id": value.get("band_id", 0), "role_label": value.get("role_label", "")},
    }]
