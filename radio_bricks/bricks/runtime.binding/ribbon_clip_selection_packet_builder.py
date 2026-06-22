from __future__ import annotations

import os
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.ribbon_clip_selection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎬",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.ribbon_clip_selection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "ribbon", "clip", "media", "selection"],
    "description": "Resolve the deterministic ribbon media path for a station category and clip phase like entry, loop, or exit.",
}


def build_ribbon_clip_selection_packet(
    media_root: str,
    category: str,
    kind: str,
) -> dict[str, Any]:
    ribbon_root = os.path.join(str(media_root), "ribbon")
    clip_path = os.path.join(ribbon_root, str(category), f"{str(kind)}.ogv")
    return {
        "media_root": str(media_root),
        "category": str(category),
        "kind": str(kind),
        "clip_path": clip_path,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_ribbon_clip_selection_packet(
        media_root=str(payload.get("media_root") or ""),
        category=str(payload.get("category") or ""),
        kind=str(payload.get("kind") or ""),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "ribbon-clip-selection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ribbon clip-selection packet.",
        "refs": [],
        "data": {
            "category": value.get("category", ""),
            "kind": value.get("kind", ""),
        },
    }]
