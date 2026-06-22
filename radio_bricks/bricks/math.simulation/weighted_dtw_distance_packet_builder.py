from __future__ import annotations

import math
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.simulation.weighted_dtw_distance_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📏",
    "deterministic": True,
    "inputs": ["math.distance_request.v1"],
    "outputs": ["math.distance_response.v1"],
    "requires": [],
    "provides": ["math.weighted_dtw_distance_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "simulation", "dtw", "distance", "sequence"],
    "description": "Compute a normalized weighted DTW distance packet across two same-dimensional feature sequences.",
}


def build_weighted_dtw_distance_packet(
    sequence_a: list[list[float]],
    sequence_b: list[list[float]],
    weights: list[float] | None,
) -> dict[str, Any]:
    return {
        "distance": dtw_distance_weighted(sequence_a, sequence_b, weights=weights),
        "sequence_a_length": len(sequence_a),
        "sequence_b_length": len(sequence_b),
        "weight_count": len(weights or []),
    }


def dtw_distance_weighted(
    sequence_a: list[list[float]],
    sequence_b: list[list[float]],
    *,
    weights: list[float] | None = None,
) -> float:
    if not sequence_a or not sequence_b:
        return math.inf

    previous = [math.inf] * (len(sequence_b) + 1)
    previous[0] = 0.0
    for row_a in sequence_a:
        current = [math.inf] * (len(sequence_b) + 1)
        for index, row_b in enumerate(sequence_b, start=1):
            cost = row_distance(row_a, row_b, weights=weights)
            current[index] = cost + min(previous[index], current[index - 1], previous[index - 1])
        previous = current
    return previous[-1] / max(len(sequence_a) + len(sequence_b), 1)


def row_distance(row_a: list[float], row_b: list[float], *, weights: list[float] | None = None) -> float:
    dims = min(len(row_a), len(row_b))
    if dims == 0:
        return 0.0
    if not weights:
        return math.sqrt(sum((row_a[index] - row_b[index]) ** 2 for index in range(dims)) / dims)
    weighted_sum = 0.0
    total_weight = 0.0
    for index in range(dims):
        weight = max(float(weights[index]), 1e-6) if index < len(weights) else 1.0
        weighted_sum += weight * ((row_a[index] - row_b[index]) ** 2)
        total_weight += weight
    return math.sqrt(weighted_sum / max(total_weight, 1e-6))


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_weighted_dtw_distance_packet(
        sequence_a=list(payload.get("sequence_a") or []),
        sequence_b=list(payload.get("sequence_b") or []),
        weights=[float(item) for item in (payload.get("weights") or [])] or None,
    )
    output_packet = {
        "packet_type": "math.distance_response.v1",
        "packet_version": "math.distance_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "weighted-dtw-distance",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built weighted DTW distance packet.",
        "refs": [],
        "data": {
            "distance": value.get("distance"),
            "sequence_a_length": value.get("sequence_a_length", 0),
            "sequence_b_length": value.get("sequence_b_length", 0),
        },
    }]
