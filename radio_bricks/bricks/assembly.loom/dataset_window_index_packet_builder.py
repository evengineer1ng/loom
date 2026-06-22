from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.dataset_window_index_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪟",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.dataset_window_index_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "dataset", "window", "index"],
    "description": "Package dataset window-index configuration with window length, stride, future offset, mask probability, and stream dimension.",
}


def build_dataset_window_index_packet(
    window: int,
    stride: int,
    future_offset: int,
    mask_prob: float,
    stream_dim: int,
) -> dict[str, Any]:
    return {
        "window": int(window),
        "stride": int(stride),
        "future_offset": int(future_offset),
        "mask_prob": float(mask_prob),
        "stream_dim": int(stream_dim),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_dataset_window_index_packet(
        window=int(payload.get("window") or 0),
        stride=int(payload.get("stride") or 0),
        future_offset=int(payload.get("future_offset") or 0),
        mask_prob=float(payload.get("mask_prob") or 0.0),
        stream_dim=int(payload.get("stream_dim") or 0),
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
        "receipt_id": "dataset-window-index-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built dataset-window index packet.",
        "refs": [],
        "data": {
            "window": value.get("window", 0),
            "stride": value.get("stride", 0),
            "stream_dim": value.get("stream_dim", 0),
        },
    }]
