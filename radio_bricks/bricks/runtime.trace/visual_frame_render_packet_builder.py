from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.visual_frame_render_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🖼️",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.visual_frame_render_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "visual", "frame", "snapshot", "render"],
    "description": "Package a rendered visual-frame trace with tick, size, base source, snapshot stats, and media time.",
}


def build_visual_frame_render_packet(
    tick: int,
    size: list[int] | tuple[int, int] | None,
    phase: float,
    media_time: float,
    base: str,
    snapshot_tick: int,
    entries: int,
    zoom: float,
    haze: float,
    bloom: float,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "size": [int(item) for item in (size or [])],
        "phase": float(phase),
        "media_time": float(media_time),
        "base": str(base),
        "snapshot_tick": int(snapshot_tick),
        "entries": int(entries),
        "zoom": float(zoom),
        "haze": float(haze),
        "bloom": float(bloom),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_visual_frame_render_packet(
        tick=int(payload.get("tick") or 0),
        size=payload.get("size"),
        phase=float(payload.get("phase") or 0.0),
        media_time=float(payload.get("media_time") or 0.0),
        base=str(payload.get("base") or ""),
        snapshot_tick=int(payload.get("snapshot_tick") or 0),
        entries=int(payload.get("entries") or 0),
        zoom=float(payload.get("zoom") or 0.0),
        haze=float(payload.get("haze") or 0.0),
        bloom=float(payload.get("bloom") or 0.0),
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
        "receipt_id": "visual-frame-render-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built visual frame render packet.",
        "refs": [],
        "data": {
            "tick": value.get("tick", 0),
            "base": value.get("base", ""),
            "entries": value.get("entries", 0),
        },
    }]
