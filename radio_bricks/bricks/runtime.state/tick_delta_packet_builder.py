from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.tick_delta_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⏱️",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.tick_delta_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "tick", "delta", "heat", "headline"],
    "description": "Package a single advance-step delta with events, predictions, heat, and headline.",
}


def build_tick_delta_packet(
    from_tick: int,
    to_tick: int,
    events: list[dict[str, Any]] | None,
    predictions: list[dict[str, Any]] | None,
    heat: float,
    headline: str,
) -> dict[str, Any]:
    return {
        "from_tick": int(from_tick),
        "to_tick": int(to_tick),
        "ticks_advanced": int(to_tick) - int(from_tick),
        "events": [dict(item) for item in (events or [])],
        "predictions": [dict(item) for item in (predictions or [])],
        "heat": float(heat),
        "headline": str(headline),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_tick_delta_packet(
        from_tick=int(payload.get("from_tick") or 0),
        to_tick=int(payload.get("to_tick") or 0),
        events=list(payload.get("events") or []),
        predictions=list(payload.get("predictions") or []),
        heat=float(payload.get("heat") or 0.0),
        headline=str(payload.get("headline") or ""),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "tick-delta-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built tick delta packet.",
        "refs": [],
        "data": {
            "from_tick": value.get("from_tick", 0),
            "to_tick": value.get("to_tick", 0),
            "ticks_advanced": value.get("ticks_advanced", 0),
        },
    }]
