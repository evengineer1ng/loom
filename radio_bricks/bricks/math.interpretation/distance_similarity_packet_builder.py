from __future__ import annotations

import math
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.distance_similarity_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📉",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.distance_similarity_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "distance", "similarity", "scale"],
    "description": "Translate a distance score into an exponential similarity packet with explicit scale handling.",
}


def build_distance_similarity_packet(distance: float, scale: float) -> dict[str, Any]:
    if math.isinf(distance):
        similarity = 0.0
    else:
        similarity = math.exp(-float(distance) / max(float(scale), 1e-6))
    return {
        "distance": float(distance),
        "scale": float(scale),
        "similarity": float(similarity),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_distance_similarity_packet(
        distance=float(payload.get("distance") or 0.0),
        scale=float(payload.get("scale") or 0.0),
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
        "receipt_id": "distance-similarity-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built distance-to-similarity packet.",
        "refs": [],
        "data": {
            "distance": value.get("distance", 0.0),
            "similarity": value.get("similarity", 0.0),
        },
    }]
