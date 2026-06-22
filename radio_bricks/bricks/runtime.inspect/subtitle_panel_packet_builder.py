from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.subtitle_panel_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "💬",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.subtitle_panel_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "subtitle", "panel", "bookmark", "console"],
    "description": "Package Bookmark's subtitle panel as a reusable readout surface with text, wrapping posture, wave toggle, and panel theme.",
}


def build_subtitle_panel_packet(
    text: str,
    max_chars: int,
    wave_enabled: bool,
    panel_theme: dict[str, Any] | None,
    text_color: str,
) -> dict[str, Any]:
    return {
        "text": str(text),
        "max_chars": int(max_chars),
        "wave_enabled": bool(wave_enabled),
        "panel_theme": dict(panel_theme or {}),
        "text_color": str(text_color),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_subtitle_panel_packet(
        text=str(payload.get("text") or ""),
        max_chars=int(payload.get("max_chars") or 0),
        wave_enabled=bool(payload.get("wave_enabled")),
        panel_theme=dict(payload.get("panel_theme") or {}),
        text_color=str(payload.get("text_color") or ""),
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
        "receipt_id": "subtitle-panel-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built subtitle panel packet.",
        "refs": [],
        "data": {
            "max_chars": value.get("max_chars", 0),
            "wave_enabled": value.get("wave_enabled", False),
        },
    }]
