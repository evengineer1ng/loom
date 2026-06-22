from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.media_resolution_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗺️",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.media_resolution_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "media", "resolution", "thumbnail", "path"],
    "description": "Package how a visual asset reference resolved against descriptor, absolute, or working-directory paths.",
}


def build_media_resolution_packet(
    ref: str,
    resolved_path: str,
    resolution_source: str,
    exists: bool,
) -> dict[str, Any]:
    return {
        "ref": str(ref),
        "resolved_path": str(resolved_path),
        "resolution_source": str(resolution_source),
        "exists": bool(exists),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_media_resolution_packet(
        ref=str(payload.get("ref") or ""),
        resolved_path=str(payload.get("resolved_path") or ""),
        resolution_source=str(payload.get("resolution_source") or ""),
        exists=bool(payload.get("exists")),
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
        "receipt_id": "media-resolution-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built media resolution packet.",
        "refs": [],
        "data": {
            "ref": value.get("ref", ""),
            "resolution_source": value.get("resolution_source", ""),
            "exists": value.get("exists", False),
        },
    }]
