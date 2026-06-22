from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "registry.station.voice_assignment_reader",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["registry.station_request.v1"],
    "outputs": ["registry.station_response.v1"],
    "requires": [],
    "provides": ["registry.station_voice_assignments"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["registry", "station", "voice"],
    "description": "Read station voice assignments into role-to-asset mappings and provider hints.",
}


def read_voice_assignments(manifest: dict[str, Any] | None) -> dict[str, Any]:
    data = dict(manifest or {})
    return {
        "provider_hint": dict(dict(data.get("audio") or {})).get("piper_bin") or "",
        "voices": {str(name): str(path) for name, path in dict(data.get("voices") or {}).items()},
        "voice_count": len(dict(data.get("voices") or {})),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = read_voice_assignments(dict(input_packet.get("payload") or {}))
    output_packet = {
        "packet_type": "registry.station_response.v1",
        "packet_version": "registry.station_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "voice-assignment-reader",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Read voice assignments.",
        "refs": [],
        "data": {"voice_count": value.get("voice_count", 0)},
    }]
