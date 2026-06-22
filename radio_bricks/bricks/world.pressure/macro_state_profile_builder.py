from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.pressure.macro_state_profile_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌐",
    "deterministic": True,
    "inputs": ["world.pressure_request.v1"],
    "outputs": ["world.pressure_response.v1"],
    "requires": [],
    "provides": ["world.macro_state_profile_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "pressure", "forkuniverse", "macro", "profile"],
    "description": "Package concept-derived macro pressure rows with baseline, normalization bias, and drift rate per concept domain.",
}


def build_macro_state_profile_packet(rows: list[dict[str, Any]] | None) -> dict[str, Any]:
    return {"rows": [dict(item) for item in (rows or [])], "count": len(rows or [])}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_macro_state_profile_packet(rows=list(payload.get("rows") or []))
    output_packet = {
        "packet_type": "world.pressure_response.v1",
        "packet_version": "world.pressure_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "macro-state-profile-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built macro-state profile packet.",
        "refs": [],
        "data": {"count": value.get("count", 0)},
    }]
