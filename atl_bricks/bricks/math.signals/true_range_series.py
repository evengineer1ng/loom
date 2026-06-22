from __future__ import annotations

from typing import Any

import pandas as pd


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.true_range_series",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.frame_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.true_range"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "true-range"],
    "description": "Compute true range from high, low, and close series.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [field for field in ("high", "low", "close") if not isinstance(payload.get(field), list)]
    if missing:
        return [{"code": "missing_fields", "message": f"payload lists required: {', '.join(missing)}"}]
    return []


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    return pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    df = pd.DataFrame({"high": payload["high"], "low": payload["low"], "close": payload["close"]})
    result = true_range(df).tolist()
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"values": result},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "true-range-computed",
        "brick_id": CONCEPT["id"],
        "kind": "analytics",
        "label": "Computed true range series.",
        "refs": [],
        "data": {"count": len(output_packet["payload"]["values"])},
    }]
