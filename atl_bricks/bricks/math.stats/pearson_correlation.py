from __future__ import annotations

import math
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.stats.pearson_correlation",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.pearson"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "stats", "correlation"],
    "description": "Compute Pearson correlation for two numeric series.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if not isinstance(payload.get("xs"), list) or not isinstance(payload.get("ys"), list):
        return [{"code": "missing_series", "message": "payload.xs and payload.ys must be lists."}]
    if len(payload.get("xs", [])) != len(payload.get("ys", [])):
        return [{"code": "length_mismatch", "message": "payload.xs and payload.ys must have equal length."}]
    return []


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3:
        return None
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return None
    return round(num / (dx * dy), 2)


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    xs = [float(x) for x in input_packet["payload"].get("xs", [])]
    ys = [float(y) for y in input_packet["payload"].get("ys", [])]
    result = pearson(xs, ys)
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"pearson": result, "count": len(xs)},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "pearson-computed",
        "brick_id": CONCEPT["id"],
        "kind": "analytics",
        "label": "Computed Pearson correlation.",
        "refs": [],
        "data": output_packet["payload"],
    }]
