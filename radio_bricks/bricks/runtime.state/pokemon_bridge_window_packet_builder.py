from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.pokemon_bridge_window_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪟",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.pokemon_bridge_window_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "pokemon", "bridge", "window"],
    "description": "Package Citra window bridge state with hwnd, title, class, bounds, width, and height.",
}


def build_pokemon_bridge_window_packet(
    hwnd: int,
    title: str,
    class_name: str,
    left: int,
    top: int,
    right: int,
    bottom: int,
    width: int,
    height: int,
) -> dict[str, Any]:
    return {
        "hwnd": int(hwnd),
        "title": str(title),
        "class_name": str(class_name),
        "left": int(left),
        "top": int(top),
        "right": int(right),
        "bottom": int(bottom),
        "width": int(width),
        "height": int(height),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_pokemon_bridge_window_packet(
        hwnd=int(payload.get("hwnd") or 0),
        title=str(payload.get("title") or ""),
        class_name=str(payload.get("class_name") or ""),
        left=int(payload.get("left") or 0),
        top=int(payload.get("top") or 0),
        right=int(payload.get("right") or 0),
        bottom=int(payload.get("bottom") or 0),
        width=int(payload.get("width") or 0),
        height=int(payload.get("height") or 0),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "pokemon-bridge-window-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Pokemon bridge window packet.",
        "refs": [],
        "data": {
            "title": value.get("title", ""),
            "width": value.get("width", 0),
            "height": value.get("height", 0),
        },
    }]
