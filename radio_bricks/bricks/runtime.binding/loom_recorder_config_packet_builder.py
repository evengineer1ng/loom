from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.loom_recorder_config_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎚️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.loom_recorder_config_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "loom", "recorder", "config"],
    "description": "Package Loom recorder configuration with source choice, back window, duration, tick interval, and output tape paths.",
}


def build_loom_recorder_config_packet(
    source: str,
    back_seconds: int,
    duration_seconds: int,
    tick_seconds: int,
    out_ndjson: str,
    out_json: str,
) -> dict[str, Any]:
    return {
        "source": str(source),
        "back_seconds": int(back_seconds),
        "duration_seconds": int(duration_seconds),
        "tick_seconds": int(tick_seconds),
        "out_ndjson": str(out_ndjson),
        "out_json": str(out_json),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_loom_recorder_config_packet(
        source=str(payload.get("source") or ""),
        back_seconds=int(payload.get("back_seconds") or 0),
        duration_seconds=int(payload.get("duration_seconds") or 0),
        tick_seconds=int(payload.get("tick_seconds") or 0),
        out_ndjson=str(payload.get("out_ndjson") or ""),
        out_json=str(payload.get("out_json") or ""),
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
        "receipt_id": "loom-recorder-config-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Loom recorder-config packet.",
        "refs": [],
        "data": {
            "source": value.get("source", ""),
            "duration_seconds": value.get("duration_seconds", 0),
            "tick_seconds": value.get("tick_seconds", 0),
        },
    }]
