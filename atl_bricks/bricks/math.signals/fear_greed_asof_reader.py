from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.fear_greed_asof_reader",
    "kind": "calculator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.fear_greed_asof_value"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "fear-greed", "asof"],
    "description": "Read a deterministic fear-and-greed value as-of a requested day, defaulting to neutral when unavailable.",
}


def fear_greed_asof_value(series: list[list[Any]] | list[tuple[Any, Any]] | None, day: str, default: int = 50) -> int:
    chosen = int(default)
    for pair in list(series or []):
        if len(pair) != 2:
            continue
        pair_day, pair_value = pair[0], pair[1]
        if str(pair_day) <= str(day):
            chosen = int(pair_value)
        else:
            break
    return chosen


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {"value": fear_greed_asof_value(payload.get("series"), str(payload.get("day") or ""), int(payload.get("default") or 50))}
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "fear-greed-asof",
        "brick_id": CONCEPT["id"],
        "kind": "calculation",
        "label": "Resolved fear-and-greed as-of value.",
        "refs": [],
        "data": {"value": value.get("value", 50)},
    }]
