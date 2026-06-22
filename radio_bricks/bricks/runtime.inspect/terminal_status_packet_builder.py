from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.terminal_status_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🖥️",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.terminal_status_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "terminal", "status", "display"],
    "description": "Package terminal display state with control mode, camera preview, render cadence, and recent event capacity.",
}


def build_terminal_status_packet(
    control_mode: bool,
    camera_preview: bool,
    render_interval: float,
    recent_event_capacity: int,
) -> dict[str, Any]:
    return {
        "control_mode": bool(control_mode),
        "camera_preview": bool(camera_preview),
        "render_interval": float(render_interval),
        "recent_event_capacity": int(recent_event_capacity),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_terminal_status_packet(
        control_mode=bool(payload.get("control_mode")),
        camera_preview=bool(payload.get("camera_preview")),
        render_interval=float(payload.get("render_interval") or 0.0),
        recent_event_capacity=int(payload.get("recent_event_capacity") or 0),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "terminal-status-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built terminal-status packet.",
        "refs": [],
        "data": {
            "control_mode": value.get("control_mode", False),
            "camera_preview": value.get("camera_preview", False),
            "render_interval": value.get("render_interval", 0.0),
        },
    }]
