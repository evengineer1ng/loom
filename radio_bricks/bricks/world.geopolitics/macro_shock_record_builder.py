from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.geopolitics.macro_shock_record_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⚡",
    "deterministic": True,
    "inputs": ["world.geopolitics_request.v1"],
    "outputs": ["world.geopolitics_response.v1"],
    "requires": [],
    "provides": ["world.macro_shock_record"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "geopolitics", "shock", "record", "deep_field"],
    "description": "Build a Deep Field macro-shock record packet with type, tick, magnitude, and civ identity.",
}


def build_macro_shock_record(shock_type: str, tick: int, magnitude: float, civ_id: str) -> dict[str, Any]:
    return {
        "shock_type": shock_type,
        "tick": int(tick),
        "magnitude": float(magnitude),
        "civ_id": civ_id,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_macro_shock_record(
        shock_type=str(payload.get("shock_type") or ""),
        tick=int(payload.get("tick") or 0),
        magnitude=float(payload.get("magnitude") or 0.0),
        civ_id=str(payload.get("civ_id") or ""),
    )
    output_packet = {
        "packet_type": "world.geopolitics_response.v1",
        "packet_version": "world.geopolitics_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "macro-shock-record",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built macro-shock record.",
        "refs": [],
        "data": {"shock_type": value.get("shock_type", ""), "civ_id": value.get("civ_id", "")},
    }]
