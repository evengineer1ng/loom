from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.multihorizon_alignment_gate",
    "kind": "gate",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.multihorizon_alignment_gate"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "alignment", "multihorizon"],
    "description": "Evaluate strict long and short multi-horizon alignment with tenure, momentum, and quality confirmations.",
}


def multihorizon_alignment_gate(align_long: bool, align_short: bool, adx_ok: bool, rsi_long_ok: bool, rsi_short_ok: bool, vol_ok: bool, atr_ok: bool, candle_long_ok: bool, candle_short_ok: bool) -> dict[str, bool]:
    return {
        "enter_long": bool(align_long and adx_ok and rsi_long_ok and vol_ok and atr_ok and candle_long_ok),
        "enter_short": bool(align_short and adx_ok and rsi_short_ok and vol_ok and atr_ok and candle_short_ok),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = multihorizon_alignment_gate(
        align_long=bool(payload.get("align_long", False)),
        align_short=bool(payload.get("align_short", False)),
        adx_ok=bool(payload.get("adx_ok", False)),
        rsi_long_ok=bool(payload.get("rsi_long_ok", False)),
        rsi_short_ok=bool(payload.get("rsi_short_ok", False)),
        vol_ok=bool(payload.get("vol_ok", False)),
        atr_ok=bool(payload.get("atr_ok", False)),
        candle_long_ok=bool(payload.get("candle_long_ok", False)),
        candle_short_ok=bool(payload.get("candle_short_ok", False)),
    )
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


def receipts(value: dict[str, bool]) -> list[dict[str, Any]]:
    return [{"receipt_id": "multihorizon-alignment-gate", "brick_id": CONCEPT["id"], "kind": "gate", "label": "Evaluated multihorizon alignment gate.", "refs": [], "data": value}]
