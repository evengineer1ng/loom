from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "progression.outcome.outcome_band_classifier",
    "kind": "classifier",
    "version": "0.1.0",
    "emoji": "🎯",
    "deterministic": True,
    "inputs": ["progression.outcome_request.v1"],
    "outputs": ["progression.outcome_response.v1"],
    "requires": [],
    "provides": ["progression.outcome_band_classification"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["progression", "outcome", "band", "quadrant", "classifier"],
    "description": "Package the Neikos outcome-band composition from island quadrant and personal quadrant into a single band id.",
}


def classify_outcome_band(island_quadrant: int, personal_quadrant: int) -> dict[str, Any]:
    band_id = int(island_quadrant) * 10 + int(personal_quadrant)
    return {
        "island_quadrant": int(island_quadrant),
        "personal_quadrant": int(personal_quadrant),
        "band_id": band_id,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = classify_outcome_band(
        island_quadrant=int(payload.get("island_quadrant") or 0),
        personal_quadrant=int(payload.get("personal_quadrant") or 0),
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
        "receipt_id": "outcome-band-classification",
        "brick_id": CONCEPT["id"],
        "kind": "classify",
        "label": "Classified outcome band.",
        "refs": [],
        "data": {"band_id": value.get("band_id", 0)},
    }]
