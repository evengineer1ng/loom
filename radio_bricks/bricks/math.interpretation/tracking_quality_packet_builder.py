from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.tracking_quality_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🩺",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.tracking_quality_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "tracking", "quality", "confidence"],
    "description": "Package landmark tracking quality with torso, hands, legs, score, and the reason explaining degradation.",
}


def build_tracking_quality_packet(
    timestamp: float,
    score: float,
    torso_confidence: float,
    hands_confidence: float,
    legs_confidence: float,
    reason: str,
) -> dict[str, Any]:
    return {
        "timestamp": float(timestamp),
        "score": float(score),
        "torso_confidence": float(torso_confidence),
        "hands_confidence": float(hands_confidence),
        "legs_confidence": float(legs_confidence),
        "reason": str(reason),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_tracking_quality_packet(
        timestamp=float(payload.get("timestamp") or 0.0),
        score=float(payload.get("score") or 0.0),
        torso_confidence=float(payload.get("torso_confidence") or 0.0),
        hands_confidence=float(payload.get("hands_confidence") or 0.0),
        legs_confidence=float(payload.get("legs_confidence") or 0.0),
        reason=str(payload.get("reason") or ""),
    )
    output_packet = {
        "packet_type": "math.interpretation_response.v1",
        "packet_version": "math.interpretation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "tracking-quality-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built tracking-quality packet.",
        "refs": [],
        "data": {
            "score": value.get("score", 0.0),
            "reason": value.get("reason", ""),
        },
    }]
