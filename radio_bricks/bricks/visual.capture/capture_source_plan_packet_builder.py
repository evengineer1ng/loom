from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "visual.capture.capture_source_plan_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📸",
    "deterministic": True,
    "inputs": ["visual.capture_request.v1"],
    "outputs": ["visual.capture_response.v1"],
    "requires": [],
    "provides": ["visual.capture_source_plan_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["visual", "capture", "source", "plan", "frame"],
    "description": "Package capture planning across screen, window, and video-file modes with source identifiers, capture interval, and frame-advance strategy.",
}


def build_capture_source_plan_packet(
    source_type: str,
    source_path: str,
    source_window: str,
    capture_interval: float,
    video_frame_index: int,
    next_frame_step: int,
) -> dict[str, Any]:
    return {
        "source_type": str(source_type),
        "source_path": str(source_path),
        "source_window": str(source_window),
        "capture_interval": float(capture_interval),
        "video_frame_index": int(video_frame_index),
        "next_frame_step": int(next_frame_step),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_capture_source_plan_packet(
        source_type=str(payload.get("source_type") or ""),
        source_path=str(payload.get("source_path") or ""),
        source_window=str(payload.get("source_window") or ""),
        capture_interval=float(payload.get("capture_interval") or 0.0),
        video_frame_index=int(payload.get("video_frame_index") or 0),
        next_frame_step=int(payload.get("next_frame_step") or 0),
    )
    output_packet = {
        "packet_type": "visual.capture_response.v1",
        "packet_version": "visual.capture_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "capture-source-plan-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built capture-source plan packet.",
        "refs": [],
        "data": {
            "source_type": value.get("source_type", ""),
            "capture_interval": value.get("capture_interval", 0.0),
            "next_frame_step": value.get("next_frame_step", 0),
        },
    }]
