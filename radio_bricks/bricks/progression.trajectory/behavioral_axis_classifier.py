from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "progression.trajectory.behavioral_axis_classifier",
    "kind": "classifier",
    "version": "0.1.0",
    "emoji": "🧠",
    "deterministic": True,
    "inputs": ["progression.trajectory_request.v1"],
    "outputs": ["progression.trajectory_response.v1"],
    "requires": [],
    "provides": ["progression.behavioral_axis_classification"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["progression", "trajectory", "behavior", "axis", "classifier"],
    "description": "Classify the Neikos behavioral axis from competitive, curious, stabilizing, and exploitative score blends.",
}


def classify_behavioral_axis(
    competitive_focus: float,
    exploration_depth: float,
    research_investment: float,
    breeding_intensity: float,
    anomaly_exposure: float,
    risk_appetite: float,
) -> dict[str, Any]:
    dominant_score = competitive_focus * 0.5 + risk_appetite * 0.3 - exploration_depth * 0.1
    curious_score = exploration_depth * 0.45 + anomaly_exposure * 0.45 - competitive_focus * 0.1
    stabilizing_score = research_investment * 0.4 + breeding_intensity * 0.3 - anomaly_exposure * 0.2 + (100.0 - risk_appetite) * 0.1
    exploitative_score = breeding_intensity * 0.4 + competitive_focus * 0.3 - exploration_depth * 0.1 - research_investment * 0.1
    scores = {
        "DOMINANT": float(dominant_score),
        "CURIOUS": float(curious_score),
        "STABILIZING": float(stabilizing_score),
        "EXPLOITATIVE": float(exploitative_score),
    }
    axis = max(scores.items(), key=lambda item: item[1])[0]
    return {"behavioral_axis": axis, "scores": scores}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = classify_behavioral_axis(
        competitive_focus=float(payload.get("competitive_focus") or 0.0),
        exploration_depth=float(payload.get("exploration_depth") or 0.0),
        research_investment=float(payload.get("research_investment") or 0.0),
        breeding_intensity=float(payload.get("breeding_intensity") or 0.0),
        anomaly_exposure=float(payload.get("anomaly_exposure") or 0.0),
        risk_appetite=float(payload.get("risk_appetite") or 0.0),
    )
    output_packet = {
        "packet_type": "progression.trajectory_response.v1",
        "packet_version": "progression.trajectory_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "behavioral-axis-classification",
        "brick_id": CONCEPT["id"],
        "kind": "classify",
        "label": "Classified behavioral axis.",
        "refs": [],
        "data": {"behavioral_axis": value.get("behavioral_axis", "")},
    }]
