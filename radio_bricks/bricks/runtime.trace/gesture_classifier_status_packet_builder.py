from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.gesture_classifier_status_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📡",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.gesture_classifier_status_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "classifier", "status", "diagnostics"],
    "description": "Package live classifier runtime status including motion gate, buffer fill, raw probabilities, and spike ratios.",
}


def build_gesture_classifier_status_packet(
    status: str,
    buffered_frames: int,
    motion: float,
    probabilities: dict[str, float] | None,
    spikes: dict[str, float] | None,
) -> dict[str, Any]:
    return {
        "status": str(status),
        "buffered_frames": int(buffered_frames),
        "motion": float(motion),
        "probabilities": {str(key): float(value) for key, value in (probabilities or {}).items()},
        "spikes": {str(key): float(value) for key, value in (spikes or {}).items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_gesture_classifier_status_packet(
        status=str(payload.get("status") or ""),
        buffered_frames=int(payload.get("buffered_frames") or 0),
        motion=float(payload.get("motion") or 0.0),
        probabilities=dict(payload.get("probabilities") or {}),
        spikes=dict(payload.get("spikes") or {}),
    )
    output_packet = {
        "packet_type": "runtime.trace_response.v1",
        "packet_version": "runtime.trace_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "gesture-classifier-status-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built gesture-classifier status packet.",
        "refs": [],
        "data": {
            "status": value.get("status", ""),
            "buffered_frames": value.get("buffered_frames", 0),
            "probability_count": len(value.get("probabilities", {})),
        },
    }]
