from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "progression.outcome.personal_quadrant_classifier",
    "kind": "classifier",
    "version": "0.1.0",
    "emoji": "👤",
    "deterministic": True,
    "inputs": ["progression.outcome_request.v1"],
    "outputs": ["progression.outcome_response.v1"],
    "requires": [],
    "provides": ["progression.personal_quadrant_classification"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["progression", "outcome", "personal", "quadrant", "risk"],
    "description": "Classify the personal outcome quadrant from dominant trajectory axis and risk-appetite split.",
}


def classify_personal_quadrant(
    competitive_focus: float,
    exploration_depth: float,
    research_investment: float,
    breeding_intensity: float,
    anomaly_exposure: float,
    risk_appetite: float,
) -> dict[str, Any]:
    scores = [competitive_focus, exploration_depth, research_investment, breeding_intensity, anomaly_exposure]
    max_score = max(scores)
    max_idx = scores.index(max_score)
    quadrant_map = {0: [0, 7], 1: [2, 4], 2: [1, 3], 3: [3, 8], 4: [5, 9]}
    options = quadrant_map.get(max_idx, [0, 5])
    quadrant = options[1] if risk_appetite > 50 else options[0]
    return {"dominant_axis_index": max_idx, "quadrant": quadrant, "risk_appetite": float(risk_appetite)}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = classify_personal_quadrant(
        competitive_focus=float(payload.get("competitive_focus") or 0.0),
        exploration_depth=float(payload.get("exploration_depth") or 0.0),
        research_investment=float(payload.get("research_investment") or 0.0),
        breeding_intensity=float(payload.get("breeding_intensity") or 0.0),
        anomaly_exposure=float(payload.get("anomaly_exposure") or 0.0),
        risk_appetite=float(payload.get("risk_appetite") or 0.0),
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
        "receipt_id": "personal-quadrant-classification",
        "brick_id": CONCEPT["id"],
        "kind": "classify",
        "label": "Classified personal quadrant.",
        "refs": [],
        "data": {"quadrant": value.get("quadrant", 0)},
    }]
