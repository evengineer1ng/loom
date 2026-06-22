from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.prediction_resolution_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔮",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.prediction_resolution_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "prediction", "calibration", "resolution"],
    "description": "Package prediction settlement with confidence drift, truth scoring, calibration error, and final hit-or-miss disposition.",
}


def build_prediction_resolution_packet(
    tick: int,
    prediction_id: str,
    thread_id: str,
    confidence_before: float,
    confidence_after: float,
    outcome: str,
    truth_value: float,
    calibration_error: float,
    emitted_event: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "prediction_id": str(prediction_id),
        "thread_id": str(thread_id),
        "confidence_before": float(confidence_before),
        "confidence_after": float(confidence_after),
        "outcome": str(outcome),
        "truth_value": float(truth_value),
        "calibration_error": float(calibration_error),
        "emitted_event": dict(emitted_event or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_prediction_resolution_packet(
        tick=int(payload.get("tick") or 0),
        prediction_id=str(payload.get("prediction_id") or ""),
        thread_id=str(payload.get("thread_id") or ""),
        confidence_before=float(payload.get("confidence_before") or 0.0),
        confidence_after=float(payload.get("confidence_after") or 0.0),
        outcome=str(payload.get("outcome") or ""),
        truth_value=float(payload.get("truth_value") or 0.0),
        calibration_error=float(payload.get("calibration_error") or 0.0),
        emitted_event=dict(payload.get("emitted_event") or {}),
    )
    output_packet = {
        "packet_type": "runtime.story_response.v1",
        "packet_version": "runtime.story_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "prediction-resolution-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built prediction-resolution packet.",
        "refs": [],
        "data": {
            "prediction_id": value.get("prediction_id", ""),
            "outcome": value.get("outcome", ""),
            "calibration_error": value.get("calibration_error", 0.0),
        },
    }]
