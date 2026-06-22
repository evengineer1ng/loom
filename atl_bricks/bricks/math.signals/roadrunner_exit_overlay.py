from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.roadrunner_exit_overlay",
    "kind": "classifier",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.roadrunner_exit_overlay"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "exit", "overlay"],
    "description": "Classify Roadrunner-style discretionary exits from candle state, side, profit, and holding age.",
}


def roadrunner_exit_overlay(last_candle: dict[str, Any], is_short: bool, current_profit: float, bars_since_entry: int, adx_weak: float, max_hold_bars: int, time_exit_profit: float) -> str | None:
    close = float(last_candle.get("close") or 0.0)
    ema_8 = float(last_candle.get("ema_8") or 0.0)
    ema_21 = float(last_candle.get("ema_21") or 0.0)
    adx = float(last_candle.get("adx") or 0.0)
    plus_di = float(last_candle.get("plus_di") or 0.0)
    minus_di = float(last_candle.get("minus_di") or 0.0)
    rsi = float(last_candle.get("rsi") or 0.0)
    bearish = bool(last_candle.get("bearish", False))
    bullish = bool(last_candle.get("bullish", False))

    if not is_short:
        if current_profit > 0.025 and close < ema_8:
            return "profit_protect_long"
        if close < ema_21 and adx < adx_weak and plus_di < minus_di:
            return "mom_death_long"
        if current_profit < 0 and close < ema_21 and adx < adx_weak:
            return "soft_stop_long"
        if rsi > 82 and bearish and current_profit > 0.02:
            return "blowoff_long"
        if bars_since_entry > max_hold_bars and current_profit < time_exit_profit:
            return "time_bleed_long"
        return None

    if current_profit > 0.025 and close > ema_8:
        return "profit_protect_short"
    if close > ema_21 and adx < adx_weak and minus_di < plus_di:
        return "mom_death_short"
    if current_profit < 0 and close > ema_21 and adx < adx_weak:
        return "soft_stop_short"
    if rsi < 18 and bullish and current_profit > 0.02:
        return "blowoff_short"
    if bars_since_entry > max_hold_bars and current_profit < time_exit_profit:
        return "time_bleed_short"
    return None


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    label = roadrunner_exit_overlay(
        last_candle=dict(payload.get("last_candle") or {}),
        is_short=bool(payload.get("is_short", False)),
        current_profit=float(payload.get("current_profit") or 0.0),
        bars_since_entry=int(payload.get("bars_since_entry") or 0),
        adx_weak=float(payload.get("adx_weak") or 0.0),
        max_hold_bars=int(payload.get("max_hold_bars") or 0),
        time_exit_profit=float(payload.get("time_exit_profit") or 0.0),
    )
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"label": label},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(label), "issues": [], "meta": {}}


def receipts(label: str | None) -> list[dict[str, Any]]:
    return [{"receipt_id": "roadrunner-exit-overlay", "brick_id": CONCEPT["id"], "kind": "classification", "label": "Evaluated Roadrunner exit overlay.", "refs": [], "data": {"label": label}}]
