from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.influence.prediction_feedback_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⚖️",
    "deterministic": True,
    "inputs": ["world.influence_request.v1"],
    "outputs": ["world.influence_response.v1"],
    "requires": [],
    "provides": ["world.prediction_feedback_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "influence", "prediction", "legitimacy", "feedback"],
    "description": "Package the institutional legitimacy and macro-pressure adjustment that follows prediction hits and misses.",
}


def build_prediction_feedback_packet(
    outcome: str,
    legitimacy_delta: float,
    affected_institutions: list[dict[str, Any]] | None,
    institutional_pressure_before: float,
    institutional_pressure_after: float,
) -> dict[str, Any]:
    return {
        "outcome": str(outcome),
        "legitimacy_delta": float(legitimacy_delta),
        "affected_institutions": [dict(item) for item in (affected_institutions or [])],
        "institutional_pressure_before": float(institutional_pressure_before),
        "institutional_pressure_after": float(institutional_pressure_after),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_prediction_feedback_packet(
        outcome=str(payload.get("outcome") or ""),
        legitimacy_delta=float(payload.get("legitimacy_delta") or 0.0),
        affected_institutions=list(payload.get("affected_institutions") or []),
        institutional_pressure_before=float(payload.get("institutional_pressure_before") or 0.0),
        institutional_pressure_after=float(payload.get("institutional_pressure_after") or 0.0),
    )
    output_packet = {
        "packet_type": "world.influence_response.v1",
        "packet_version": "world.influence_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "prediction-feedback-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built prediction-feedback packet.",
        "refs": [],
        "data": {
            "outcome": value.get("outcome", ""),
            "legitimacy_delta": value.get("legitimacy_delta", 0.0),
            "institution_count": len(value.get("affected_institutions", [])),
        },
    }]
