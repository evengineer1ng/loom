from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.motion_dataset_schema_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📚",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.motion_dataset_schema_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "dataset", "schema", "features"],
    "description": "Package the dual-stream motion dataset schema with canonical feature order, confidence ownership, stream dimension, and windowing defaults.",
}


def build_motion_dataset_schema_packet(
    features: list[str] | None,
    confidence_features: list[str] | None,
    stream_dim: int,
    window: int,
    stride: int,
    future_offset: int,
    mask_prob: float,
) -> dict[str, Any]:
    return {
        "features": [str(item) for item in (features or [])],
        "confidence_features": [str(item) for item in (confidence_features or [])],
        "stream_dim": int(stream_dim),
        "window": int(window),
        "stride": int(stride),
        "future_offset": int(future_offset),
        "mask_prob": float(mask_prob),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_motion_dataset_schema_packet(
        features=list(payload.get("features") or []),
        confidence_features=list(payload.get("confidence_features") or []),
        stream_dim=int(payload.get("stream_dim") or 0),
        window=int(payload.get("window") or 0),
        stride=int(payload.get("stride") or 0),
        future_offset=int(payload.get("future_offset") or 0),
        mask_prob=float(payload.get("mask_prob") or 0.0),
    )
    output_packet = {
        "packet_type": "assembly.loom_response.v1",
        "packet_version": "assembly.loom_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "motion-dataset-schema-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built motion-dataset schema packet.",
        "refs": [],
        "data": {
            "feature_count": len(value.get("features", [])),
            "stream_dim": value.get("stream_dim", 0),
            "window": value.get("window", 0),
        },
    }]
