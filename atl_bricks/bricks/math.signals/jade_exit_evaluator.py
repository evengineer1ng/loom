from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.jade_exit_evaluator",
    "kind": "classifier",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.jade_exit_tags"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "jade", "exit"],
    "description": "Evaluate Jade-style exit tags for RSI extremes, divergence reversions, regime shifts, correlation breakdowns, and breadth stress.",
}


def evaluate_jade_exit(row: dict[str, Any] | None, prior: dict[str, Any] | None = None) -> dict[str, Any]:
    current = dict(row or {})
    previous = dict(prior or {})
    adx = float(current.get("adx") or 0.0)
    adx_prev = float(previous.get("adx", current.get("adx_prev", 0.0)) or 0.0)
    rsi = float(current.get("rsi") or 0.0)
    strong_trend = bool(current.get("strong_trend", False))
    divergence_z = float(current.get("divergence_z") or 0.0)
    candle_bearish = bool(current.get("candle_bearish", False))
    candle_bullish = bool(current.get("candle_bullish", False))
    corr = float(current.get("lead_lag_corr") or 0.0)
    corr_prev = float(previous.get("lead_lag_corr", current.get("lead_lag_corr_prev", 0.0)) or 0.0)
    breadth = float(current.get("basket_breadth") or 0.0)

    long_rsi = rsi > 88.0 and not strong_trend
    short_rsi = rsi < 12.0 and not strong_trend
    long_div = divergence_z < -3.0 and candle_bearish and adx < adx_prev
    short_div = divergence_z > 3.0 and candle_bullish and adx < adx_prev
    regime_long = adx < 20.0 and adx_prev > 30.0 and candle_bearish
    regime_short = adx < 20.0 and adx_prev > 30.0 and candle_bullish
    corr_break = corr < 0.2 and corr_prev > 0.5
    breadth_collapse_long = breadth < 0.25
    breadth_extreme_short = breadth > 0.75

    exit_long = long_rsi or long_div or regime_long or corr_break or breadth_collapse_long
    exit_short = short_rsi or short_div or regime_short or corr_break or breadth_extreme_short

    exit_tag = ""
    if long_rsi:
        exit_tag = "r1_rsi_extreme_long"
    elif long_div:
        exit_tag = "r3_divergence_revert_long"
    elif short_rsi:
        exit_tag = "r2_rsi_extreme_short"
    elif short_div:
        exit_tag = "r4_divergence_revert_short"
    elif regime_long or regime_short:
        exit_tag = "r5_regime_shift_exit"
    elif corr_break and exit_long:
        exit_tag = "r6_corr_breakdown_long"
    elif corr_break and exit_short:
        exit_tag = "r6_corr_breakdown_short"
    elif breadth_collapse_long:
        exit_tag = "r7_breadth_collapse_long"
    elif breadth_extreme_short:
        exit_tag = "r7_breadth_extreme_short"

    return {
        "exit_long": exit_long,
        "exit_short": exit_short,
        "exit_tag": exit_tag,
        "signals": {
            "rsi_extreme_long": long_rsi,
            "rsi_extreme_short": short_rsi,
            "divergence_revert_long": long_div,
            "divergence_revert_short": short_div,
            "regime_shift_long": regime_long,
            "regime_shift_short": regime_short,
            "corr_breakdown": corr_break,
            "breadth_collapse_long": breadth_collapse_long,
            "breadth_extreme_short": breadth_extreme_short,
        },
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = evaluate_jade_exit(
        row=dict(payload.get("row") or {}),
        prior=dict(payload.get("prior") or {}),
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
    return [{
        "receipt_id": "jade-exit-evaluator",
        "brick_id": CONCEPT["id"],
        "kind": "classification",
        "label": "Evaluated Jade exit signals.",
        "refs": [],
        "data": {"exit_tag": value.get("exit_tag", ""), "exit_long": value.get("exit_long", False), "exit_short": value.get("exit_short", False)},
    }]
