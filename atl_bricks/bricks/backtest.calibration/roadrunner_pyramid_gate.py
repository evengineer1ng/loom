from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.roadrunner_pyramid_gate",
    "kind": "gate",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.roadrunner_pyramid_gate"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "management", "pyramid"],
    "description": "Evaluate Roadrunner-style pyramid add conditions from profit, entry count, ATR move, and trend state.",
}


def roadrunner_pyramid_gate(last_candle: dict[str, Any], is_short: bool, current_profit: float, entry_count: int, max_pyramid_entries: int, pyramid_profit: float, current_entry_rate: float, current_rate: float, stake_amount: float, pyramid_size_ratio: float, adx_strong: float) -> float | None:
    if current_profit <= pyramid_profit:
        return None
    if entry_count >= max_pyramid_entries:
        return None
    if current_entry_rate and current_rate:
        atr_pct = float(last_candle.get("atr_14") or 0.0) / float(current_rate)
        price_move = abs(float(current_rate) - float(current_entry_rate)) / float(current_entry_rate)
        if price_move < 0.5 * atr_pct:
            return None
    adx = float(last_candle.get("adx") or 0.0)
    plus_di = float(last_candle.get("plus_di") or 0.0)
    minus_di = float(last_candle.get("minus_di") or 0.0)
    close = float(last_candle.get("close") or 0.0)
    ema_8 = float(last_candle.get("ema_8") or 0.0)
    if not is_short:
        if bool(last_candle.get("trend_up", False)) and adx > adx_strong and plus_di > minus_di and close > ema_8:
            return float(stake_amount) * float(pyramid_size_ratio)
        return None
    if bool(last_candle.get("trend_down", False)) and adx > adx_strong and minus_di > plus_di and close < ema_8:
        return float(stake_amount) * float(pyramid_size_ratio)
    return None


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = roadrunner_pyramid_gate(
        last_candle=dict(payload.get("last_candle") or {}),
        is_short=bool(payload.get("is_short", False)),
        current_profit=float(payload.get("current_profit") or 0.0),
        entry_count=int(payload.get("entry_count") or 0),
        max_pyramid_entries=int(payload.get("max_pyramid_entries") or 0),
        pyramid_profit=float(payload.get("pyramid_profit") or 0.0),
        current_entry_rate=float(payload.get("current_entry_rate") or 0.0),
        current_rate=float(payload.get("current_rate") or 0.0),
        stake_amount=float(payload.get("stake_amount") or 0.0),
        pyramid_size_ratio=float(payload.get("pyramid_size_ratio") or 0.0),
        adx_strong=float(payload.get("adx_strong") or 0.0),
    )
    output_packet = {
        "packet_type": "backtest.sim_response.v1",
        "packet_version": "backtest.sim_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"add_stake": value},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: float | None) -> list[dict[str, Any]]:
    return [{"receipt_id": "roadrunner-pyramid-gate", "brick_id": CONCEPT["id"], "kind": "gate", "label": "Evaluated Roadrunner pyramid gate.", "refs": [], "data": {"add_stake": value}}]
