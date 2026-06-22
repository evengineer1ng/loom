from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.approval_training_temporal_window_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🕰️",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.approval_training_temporal_window_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "approval", "temporal", "window"],
    "description": "Package approval-training temporal windows with offsets, per-candidate cov/mot/aggregate history, and decision timing.",
}


def build_approval_training_temporal_window_packet(
    window_ms: int,
    peak_time_offset_ms: int,
    decision_time_offset_ms: int,
    samples: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    normalized_samples = []
    for sample in samples or []:
        normalized_samples.append({
            "t_offset_ms": int(sample.get("t_offset_ms") or 0),
            "predicted_action": str(sample.get("predicted_action") or ""),
            "cov": float(sample.get("cov") or 0.0),
            "mot": float(sample.get("mot") or 0.0),
            "aggregate": float(sample.get("aggregate") or 0.0),
            "dtw": float(sample.get("dtw") or 0.0),
        })
    return {
        "window_ms": int(window_ms),
        "peak_time_offset_ms": int(peak_time_offset_ms),
        "decision_time_offset_ms": int(decision_time_offset_ms),
        "samples": normalized_samples,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_approval_training_temporal_window_packet(
        window_ms=int(payload.get("window_ms") or 0),
        peak_time_offset_ms=int(payload.get("peak_time_offset_ms") or 0),
        decision_time_offset_ms=int(payload.get("decision_time_offset_ms") or 0),
        samples=list(payload.get("samples") or []),
    )
    output_packet = {
        "packet_type": "runtime.save_response.v1",
        "packet_version": "runtime.save_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "approval-training-temporal-window-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built approval-training temporal-window packet.",
        "refs": [],
        "data": {
            "window_ms": value.get("window_ms", 0),
            "sample_count": len(value.get("samples", [])),
        },
    }]
