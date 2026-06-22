from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "visual.capture.capture_source_plan_builder",
    "kind": "planner",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["visual.capture_request.v1"],
    "outputs": ["visual.capture_response.v1"],
    "requires": [],
    "provides": ["visual.capture_source_plan"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["visual", "capture", "source", "plan"],
    "description": "Build a capture plan from visual-reader source type, path/window target, interval, and reaction mode.",
}


def build_capture_source_plan(config: dict[str, Any] | None) -> dict[str, Any]:
    cfg = dict(config or {})
    source_type = str(cfg.get("source_type") or "screen")
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "source_type": source_type,
        "source_path": str(cfg.get("source_path") or ""),
        "source_window": str(cfg.get("source_window") or ""),
        "capture_interval": float(cfg.get("capture_interval") or 5),
        "talk_over_video": bool(cfg.get("talk_over_video", False)),
        "reaction_frequency": float(cfg.get("reaction_frequency") or 30),
        "plan_kind": {
            "screen": "screen_capture",
            "window": "window_capture",
            "video_file": "video_frame_capture",
        }.get(source_type, "screen_capture"),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = build_capture_source_plan(dict(input_packet.get("payload") or {}))
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
        "receipt_id": "capture-source-plan",
        "brick_id": CONCEPT["id"],
        "kind": "plan",
        "label": "Built capture source plan.",
        "refs": [],
        "data": {"plan_kind": value.get("plan_kind", ""), "enabled": value.get("enabled", False)},
    }]
