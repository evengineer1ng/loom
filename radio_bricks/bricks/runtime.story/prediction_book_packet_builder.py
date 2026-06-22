from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.prediction_book_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔮",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.prediction_book_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "prediction", "book", "calibration"],
    "description": "Package the ForkUniverse prediction book with predictions, settled hits and misses, and calibration score.",
}


def build_prediction_book_packet(
    predictions: list[dict[str, Any]] | None,
    settled_hits: int,
    settled_misses: int,
    calibration_score: float,
) -> dict[str, Any]:
    return {
        "predictions": [dict(item) for item in (predictions or [])],
        "settled_hits": int(settled_hits),
        "settled_misses": int(settled_misses),
        "calibration_score": float(calibration_score),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_prediction_book_packet(
        predictions=list(payload.get("predictions") or []),
        settled_hits=int(payload.get("settled_hits") or 0),
        settled_misses=int(payload.get("settled_misses") or 0),
        calibration_score=float(payload.get("calibration_score") or 0.0),
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
        "receipt_id": "prediction-book-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built prediction-book packet.",
        "refs": [],
        "data": {"prediction_count": len(value.get("predictions", [])), "calibration_score": value.get("calibration_score", 0.0)},
    }]
