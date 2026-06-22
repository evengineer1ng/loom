from __future__ import annotations

import re
from typing import Any


FREQTRADE_TIMEFRAMES = {
    "1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M",
}

CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.freqtrade_timeframe_normalizer",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.value_request.v1"],
    "outputs": ["runtime.value_response.v1"],
    "requires": [],
    "provides": ["runtime.normalize_freqtrade_timeframe"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["freqtrade", "timeframe", "normalization"],
    "description": "Extract the first freqtrade-legal timeframe token from messy text.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    if "value" not in input_packet.get("payload", {}):
        return [{"code": "missing_value", "message": "payload.value is required."}]
    return []


def normalize_freqtrade_timeframe(raw: Any) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    tokens = re.findall(r"[0-9]+[a-zA-Z]+", text)
    for token in tokens:
        if token in FREQTRADE_TIMEFRAMES:
            return token
    for token in tokens:
        lowered = token[:-1] + token[-1].lower()
        if lowered in FREQTRADE_TIMEFRAMES:
            return lowered
    return ""


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    normalized = normalize_freqtrade_timeframe(input_packet["payload"].get("value"))
    output_packet = {
        "packet_type": "runtime.value_response.v1",
        "packet_version": "runtime.value_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"value": normalized},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {
        "ok": True,
        "output_packet": output_packet,
        "receipts": receipts(output_packet),
        "issues": [],
        "meta": {},
    }


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "receipt_id": "freqtrade-timeframe-normalized",
            "brick_id": CONCEPT["id"],
            "kind": "normalization",
            "label": "Normalized a freqtrade timeframe token.",
            "refs": [],
            "data": {"value": output_packet["payload"]["value"]},
        }
    ]
