from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.soundtrack_bed_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎵",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.soundtrack_bed_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "soundtrack", "audio", "loom", "media"],
    "description": "Package the optional Loom soundtrack bed with media path, looping intent, and fade timing.",
}


def build_soundtrack_bed_packet(
    path: str,
    loop: bool,
    fade_sec: float,
    volume: float | None,
) -> dict[str, Any]:
    return {
        "path": str(path),
        "loop": bool(loop),
        "fade_sec": float(fade_sec),
        "volume": volume,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_soundtrack_bed_packet(
        path=str(payload.get("path") or ""),
        loop=bool(payload.get("loop", True)),
        fade_sec=float(payload.get("fade_sec") or 0.0),
        volume=payload.get("volume"),
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
        "receipt_id": "soundtrack-bed-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built soundtrack bed packet.",
        "refs": [],
        "data": {
            "path": value.get("path", ""),
            "fade_sec": value.get("fade_sec", 0.0),
        },
    }]
