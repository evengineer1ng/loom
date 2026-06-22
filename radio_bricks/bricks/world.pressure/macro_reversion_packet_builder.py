from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.pressure.macro_reversion_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧲",
    "deterministic": True,
    "inputs": ["world.pressure_request.v1"],
    "outputs": ["world.pressure_response.v1"],
    "requires": [],
    "provides": ["world.macro_reversion_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "pressure", "macro", "reversion", "drift"],
    "description": "Package macro-axis reversion toward baseline plus normalization bias, including applied drift-rate contribution and clamped output values.",
}


def build_macro_reversion_packet(
    tick: int,
    reversion_rate: float,
    axis_rows: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "reversion_rate": float(reversion_rate),
        "axis_rows": [dict(item) for item in (axis_rows or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_macro_reversion_packet(
        tick=int(payload.get("tick") or 0),
        reversion_rate=float(payload.get("reversion_rate") or 0.0),
        axis_rows=list(payload.get("axis_rows") or []),
    )
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
        "receipt_id": "macro-reversion-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built macro-reversion packet.",
        "refs": [],
        "data": {
            "reversion_rate": value.get("reversion_rate", 0.0),
            "axis_count": len(value.get("axis_rows", [])),
        },
    }]
