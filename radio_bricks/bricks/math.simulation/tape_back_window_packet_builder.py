from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.simulation.tape_back_window_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪟",
    "deterministic": True,
    "inputs": ["math.simulation_request.v1"],
    "outputs": ["math.simulation_response.v1"],
    "requires": [],
    "provides": ["math.tape_back_window_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "simulation", "tape", "window", "loom"],
    "description": "Package a back-window filtered tape slice with requested seconds and retained row count.",
}


def build_tape_back_window_packet(back_seconds: int, rows: list[dict[str, Any]] | None) -> dict[str, Any]:
    return {
        "back_seconds": int(back_seconds),
        "rows": [dict(item) for item in (rows or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_tape_back_window_packet(
        back_seconds=int(payload.get("back_seconds") or 0),
        rows=list(payload.get("rows") or []),
    )
    output_packet = {
        "packet_type": "math.simulation_response.v1",
        "packet_version": "math.simulation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "tape-back-window-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built tape back-window packet.",
        "refs": [],
        "data": {
            "back_seconds": value.get("back_seconds", 0),
            "row_count": len(value.get("rows", [])),
        },
    }]
