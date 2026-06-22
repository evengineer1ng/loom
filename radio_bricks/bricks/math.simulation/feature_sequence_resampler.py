from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.simulation.feature_sequence_resampler",
    "kind": "transform",
    "version": "0.1.0",
    "emoji": "🪜",
    "deterministic": True,
    "inputs": ["math.sequence_request.v1"],
    "outputs": ["math.sequence_response.v1"],
    "requires": [],
    "provides": ["math.feature_sequence_resampled"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "simulation", "sequence", "resample", "interpolation"],
    "description": "Resample ordered feature-frame values into a fixed-length sequence by linear interpolation over the original timeline.",
}


def resample_feature_sequence(
    feature_frames: list[dict[str, float]],
    feature_names: list[str],
    *,
    length: int,
) -> list[list[float]]:
    rows = [
        [float(frame.get(name, 0.0) or 0.0) for name in feature_names]
        for frame in feature_frames
    ]
    if not rows:
        return []
    if length <= 1 or len(rows) == 1:
        return [list(rows[0]) for _ in range(max(length, 1))]

    output: list[list[float]] = []
    source_max = len(rows) - 1
    target_max = length - 1
    for index in range(length):
        position = index * source_max / target_max
        left = int(position)
        right = min(left + 1, source_max)
        fraction = position - left
        output.append([
            rows[left][dim] + (rows[right][dim] - rows[left][dim]) * fraction
            for dim in range(len(feature_names))
        ])
    return output


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {
        "feature_names": [str(item) for item in (payload.get("feature_names") or [])],
        "length": int(payload.get("length") or 0),
        "sequence": resample_feature_sequence(
            feature_frames=list(payload.get("feature_frames") or []),
            feature_names=[str(item) for item in (payload.get("feature_names") or [])],
            length=int(payload.get("length") or 0),
        ),
    }
    output_packet = {
        "packet_type": "math.sequence_response.v1",
        "packet_version": "math.sequence_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "feature-sequence-resampled",
        "brick_id": CONCEPT["id"],
        "kind": "transform",
        "label": "Resampled feature sequence to fixed length.",
        "refs": [],
        "data": {
            "length": value.get("length", 0),
            "feature_count": len(value.get("feature_names", [])),
        },
    }]
