from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.slaking_entry_exit_pack",
    "kind": "gate",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.slaking_entry_exit_pack"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "slaking"],
    "description": "Evaluate Slaking mean-reversion entries, thesis exits, trailing stop activation, and volatility stake scaling.",
}


def slaking_entry_exit_pack(row: dict[str, Any], trail_start: float, trail_gap: float, current_profit: float, last_atr: float, atr_mean: float, proposed_stake: float) -> dict[str, Any]:
    close = float(row.get("close") or 0.0)
    bb_lower = float(row.get("bb_lowerband") or 0.0)
    bb_upper = float(row.get("bb_upperband") or 0.0)
    rsi = float(row.get("rsi") or 0.0)
    adx = float(row.get("adx") or 0.0)
    stoch_k = float(row.get("stoch_k") or 0.0)
    stoch_d = float(row.get("stoch_d") or 0.0)
    vol_ok = bool(row.get("vol_ok", False))
    daily_rsi = float(row.get("daily_rsi", 50.0) or 50.0)
    daily_adx = float(row.get("daily_adx", 20.0) or 20.0)
    enter_long = close < bb_lower and rsi < float(row.get("rsi_long_max") or 0.0) and adx < float(row.get("adx_max") or 0.0) and stoch_k < float(row.get("stoch_long_max") or 0.0) and stoch_k > stoch_d and vol_ok and daily_rsi < 70 and daily_adx < 40
    enter_short = close > bb_upper and rsi > float(row.get("rsi_short_min") or 0.0) and adx < float(row.get("adx_max") or 0.0) and stoch_k > float(row.get("stoch_short_min") or 0.0) and stoch_k < stoch_d and vol_ok and daily_rsi > 30 and daily_adx < 40
    exit_long = close > bb_upper and rsi > float(row.get("rsi_short_min") or 0.0) and stoch_k > float(row.get("stoch_short_min") or 0.0) and stoch_k < stoch_d
    exit_short = close < bb_lower and rsi < float(row.get("rsi_long_max") or 0.0) and stoch_k < float(row.get("stoch_long_max") or 0.0) and stoch_k > stoch_d
    trail_desired_profit = float(current_profit) - float(trail_gap) if float(current_profit) >= float(trail_start) else None
    stake = float(proposed_stake) * 0.65 if float(last_atr) > float(atr_mean) * 1.5 else float(proposed_stake)
    return {
        "enter_long": enter_long,
        "enter_short": enter_short,
        "exit_long": exit_long,
        "exit_short": exit_short,
        "trail_desired_profit": trail_desired_profit,
        "scaled_stake": stake,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = slaking_entry_exit_pack(
        row=dict(payload.get("row") or {}),
        trail_start=float(payload.get("trail_start") or 0.0),
        trail_gap=float(payload.get("trail_gap") or 0.0),
        current_profit=float(payload.get("current_profit") or 0.0),
        last_atr=float(payload.get("last_atr") or 0.0),
        atr_mean=float(payload.get("atr_mean") or 0.0),
        proposed_stake=float(payload.get("proposed_stake") or 0.0),
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


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"receipt_id": "slaking-pack", "brick_id": CONCEPT["id"], "kind": "gate", "label": "Evaluated Slaking entry/exit pack.", "refs": [], "data": {"scaled_stake": value.get("scaled_stake", 0.0)}}]
