from __future__ import annotations

import re
from typing import Any


FREQTRADE_TIMEFRAMES = {
    "1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M",
}

CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "registry.settings.freqtrade_timeframe_resolver",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["registry.request.v1"],
    "outputs": ["registry.response.v1"],
    "requires": [],
    "provides": ["registry.resolve_freqtrade_timeframe"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["freqtrade", "timeframe", "resolution"],
    "description": "Resolve a valid Freqtrade timeframe from suggested, declared, existing, and default candidates.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if "default" not in payload:
        return [{"code": "missing_default", "message": "payload.default is required."}]
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


def resolve_freqtrade_timeframe(
    suggested: Any = "",
    candidate_timeframe: Any = "",
    declared: Any = "",
    existing: Any = "",
    default: Any = "5m",
) -> str:
    return (
        normalize_freqtrade_timeframe(suggested)
        or normalize_freqtrade_timeframe(candidate_timeframe)
        or normalize_freqtrade_timeframe(declared)
        or normalize_freqtrade_timeframe(existing)
        or normalize_freqtrade_timeframe(default)
        or "5m"
    )


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    timeframe = resolve_freqtrade_timeframe(
        suggested=payload.get("suggested"),
        candidate_timeframe=payload.get("candidate_timeframe"),
        declared=payload.get("declared"),
        existing=payload.get("existing"),
        default=payload.get("default"),
    )
    output_packet = {
        "packet_type": "registry.response.v1",
        "packet_version": "registry.response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"timeframe": timeframe},
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
            "receipt_id": "freqtrade-timeframe-resolved",
            "brick_id": CONCEPT["id"],
            "kind": "resolution",
            "label": "Resolved valid Freqtrade timeframe.",
            "refs": [],
            "data": {"timeframe": output_packet["payload"]["timeframe"]},
        }
    ]
