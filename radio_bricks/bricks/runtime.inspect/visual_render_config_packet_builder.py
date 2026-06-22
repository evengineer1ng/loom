from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.visual_render_config_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎨",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.visual_render_config_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "visual", "render", "theme", "media"],
    "description": "Package the resolved visual render config that chooses builtin theme versus media-backed base imagery.",
}


def build_visual_render_config_packet(
    mode: str,
    theme: str,
    path: str,
    base_label: str | None,
) -> dict[str, Any]:
    return {
        "mode": str(mode),
        "theme": str(theme),
        "path": str(path),
        "base_label": str(base_label or ""),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_visual_render_config_packet(
        mode=str(payload.get("mode") or ""),
        theme=str(payload.get("theme") or ""),
        path=str(payload.get("path") or ""),
        base_label=payload.get("base_label"),
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
        "receipt_id": "visual-render-config-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built visual render config packet.",
        "refs": [],
        "data": {
            "mode": value.get("mode", ""),
            "theme": value.get("theme", ""),
        },
    }]
