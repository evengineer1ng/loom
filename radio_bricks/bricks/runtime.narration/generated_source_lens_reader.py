from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.generated_source_lens_reader",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.generated_source_lens"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "generated", "lens"],
    "description": "Read a generated meta-plugin spec into source lenses, source field mappings, tone, and voice defaults.",
}


def read_generated_source_lenses(spec: dict[str, Any] | None) -> dict[str, Any]:
    data = dict(spec or {})
    sources = {}
    for name, raw in dict(data.get("sources") or {}).items():
        row = dict(raw or {})
        sources[str(name)] = {
            "label": row.get("label") or str(name),
            "lens": row.get("lens") or f"an update from {name}",
            "headline": row.get("headline") or "{title}",
            "fields": dict(row.get("fields") or {}),
            "min_priority": float(row.get("min_priority") or 0.0),
            "heat": dict(row.get("heat") or {}),
        }
    return {
        "station": data.get("station") or "Station",
        "tone": data.get("tone") or "",
        "voices": list(data.get("voices") or ["host"]),
        "sources": sources,
        "broadcast_grammar": dict(data.get("broadcast_grammar") or {}),
        "signal_heat": dict(data.get("signal_heat") or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = read_generated_source_lenses(dict(input_packet.get("payload") or {}))
    output_packet = {
        "packet_type": "runtime.narration_response.v1",
        "packet_version": "runtime.narration_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "generated-source-lens-reader",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Read generated source lens spec.",
        "refs": [],
        "data": {"sources": len(value.get("sources", {})), "voices": len(value.get("voices", []))},
    }]
