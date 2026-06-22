from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.stats.mean_value",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.mean"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "stats", "mean"],
    "description": "Compute the arithmetic mean of a numeric series.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    if not isinstance(input_packet.get("payload", {}).get("values"), list):
        return [{"code": "missing_values", "message": "payload.values must be a list."}]
    return []


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    values = [float(x) for x in input_packet["payload"].get("values", [])]
    result = mean(values)
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"mean": result, "count": len(values)},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "mean-computed",
        "brick_id": CONCEPT["id"],
        "kind": "analytics",
        "label": "Computed arithmetic mean.",
        "refs": [],
        "data": output_packet["payload"],
    }]
