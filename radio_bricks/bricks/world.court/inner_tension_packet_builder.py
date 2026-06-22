from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.court.inner_tension_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "😰",
    "deterministic": True,
    "inputs": ["world.court_request.v1"],
    "outputs": ["world.court_response.v1"],
    "requires": [],
    "provides": ["world.inner_tension_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "court", "oracle", "tension", "inner-state"],
    "description": "Package oracle inner tension with global tension proxy, crisis count, silence pressure, existential pressure, and final damped tension.",
}


def build_inner_tension_packet(
    global_tension: float,
    crisis_count: int,
    consecutive_silence_ticks: int,
    existential_pressure: float,
    sleeping_dampened: bool,
    final_tension: float,
) -> dict[str, Any]:
    return {
        "global_tension": float(global_tension),
        "crisis_count": int(crisis_count),
        "consecutive_silence_ticks": int(consecutive_silence_ticks),
        "existential_pressure": float(existential_pressure),
        "sleeping_dampened": bool(sleeping_dampened),
        "final_tension": float(final_tension),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_inner_tension_packet(
        global_tension=float(payload.get("global_tension") or 0.0),
        crisis_count=int(payload.get("crisis_count") or 0),
        consecutive_silence_ticks=int(payload.get("consecutive_silence_ticks") or 0),
        existential_pressure=float(payload.get("existential_pressure") or 0.0),
        sleeping_dampened=bool(payload.get("sleeping_dampened")),
        final_tension=float(payload.get("final_tension") or 0.0),
    )
    output_packet = {
        "packet_type": "world.court_response.v1",
        "packet_version": "world.court_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "inner-tension-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built inner-tension packet.",
        "refs": [],
        "data": {
            "crisis_count": value.get("crisis_count", 0),
            "sleeping_dampened": value.get("sleeping_dampened", False),
            "final_tension": value.get("final_tension", 0.0),
        },
    }]
