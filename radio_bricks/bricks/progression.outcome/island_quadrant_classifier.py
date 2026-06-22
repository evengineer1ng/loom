from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "progression.outcome.island_quadrant_classifier",
    "kind": "classifier",
    "version": "0.1.0",
    "emoji": "🧱",
    "deterministic": True,
    "inputs": ["progression.outcome_request.v1"],
    "outputs": ["progression.outcome_response.v1"],
    "requires": [],
    "provides": ["progression.island_quadrant_classification"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["progression", "outcome", "island", "quadrant", "classifier"],
    "description": "Classify the island-state quadrant from normalized ledger axes and stability pressure.",
}


def classify_island_quadrant(scores: dict[str, float] | None) -> dict[str, Any]:
    score_map = {str(key): float(value) for key, value in (scores or {}).items()}
    winner = max(score_map.items(), key=lambda item: item[1])[0] if score_map else ""
    return {"scores": score_map, "winning_quadrant": winner}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = classify_island_quadrant(dict((input_packet.get("payload") or {}).get("scores") or {}))
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
        "receipt_id": "island-quadrant-classification",
        "brick_id": CONCEPT["id"],
        "kind": "classify",
        "label": "Classified island quadrant.",
        "refs": [],
        "data": {"winning_quadrant": value.get("winning_quadrant", "")},
    }]
