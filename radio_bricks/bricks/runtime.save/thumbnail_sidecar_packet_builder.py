from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.thumbnail_sidecar_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🖇️",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.thumbnail_sidecar_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "thumbnail", "sidecar", "path", "png"],
    "description": "Package the thumbnail sidecar artifact path and render sizing for a descriptor-backed visual snapshot.",
}


def build_thumbnail_sidecar_packet(
    descriptor_path: str,
    thumbnail_path: str,
    tick: int,
    size: list[int] | tuple[int, int] | None,
    media_time: float,
) -> dict[str, Any]:
    return {
        "descriptor_path": str(descriptor_path),
        "thumbnail_path": str(thumbnail_path),
        "tick": int(tick),
        "size": [int(item) for item in (size or [])],
        "media_time": float(media_time),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_thumbnail_sidecar_packet(
        descriptor_path=str(payload.get("descriptor_path") or ""),
        thumbnail_path=str(payload.get("thumbnail_path") or ""),
        tick=int(payload.get("tick") or 0),
        size=payload.get("size"),
        media_time=float(payload.get("media_time") or 0.0),
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
        "receipt_id": "thumbnail-sidecar-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built thumbnail sidecar packet.",
        "refs": [],
        "data": {
            "thumbnail_path": value.get("thumbnail_path", ""),
            "tick": value.get("tick", 0),
        },
    }]
