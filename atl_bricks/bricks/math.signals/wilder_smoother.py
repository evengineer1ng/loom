from __future__ import annotations

from typing import Any

import pandas as pd


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.wilder_smoother",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.wilder_smoother"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "wilder"],
    "description": "Apply Wilder smoothing to a numeric series.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if not isinstance(payload.get("values"), list):
        return [{"code": "missing_values", "message": "payload.values must be a list."}]
    if not payload.get("period"):
        return [{"code": "missing_period", "message": "payload.period is required."}]
    return []


def wilder(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(alpha=1.0 / period, adjust=False).mean()


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    values = pd.Series(input_packet["payload"].get("values", []), dtype="float64")
    period = int(input_packet["payload"]["period"])
    result = wilder(values, period).tolist()
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"values": result, "period": period},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "wilder-smoothing-applied",
        "brick_id": CONCEPT["id"],
        "kind": "analytics",
        "label": "Applied Wilder smoothing.",
        "refs": [],
        "data": {"period": output_packet["payload"]["period"]},
    }]
