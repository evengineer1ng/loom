from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.entry_breakout_evaluator",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.frame_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.eval_entry_breakout"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "entry", "breakout"],
    "description": "Evaluate pure-pandas breakout entry conditions and return long/short boolean series.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [field for field in ("open", "high", "low", "close", "volume") if not isinstance(payload.get(field), list)]
    if missing:
        return [{"code": "missing_fields", "message": f"payload lists required: {', '.join(missing)}"}]
    return []


def wilder(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(alpha=1.0 / period, adjust=False).mean()


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    return pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)


def adx(df: pd.DataFrame, period: int = 14) -> tuple[pd.Series, pd.Series, pd.Series]:
    up = df["high"].diff()
    down = -df["low"].diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)
    atr = wilder(true_range(df), period)
    plus_di = 100 * wilder(pd.Series(plus_dm, index=df.index), period) / atr.replace(0, np.nan)
    minus_di = 100 * wilder(pd.Series(minus_dm, index=df.index), period) / atr.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return wilder(dx.fillna(0), period), plus_di.fillna(0), minus_di.fillna(0)


def eval_entry_breakout(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    d = df.copy()
    dc_high = d["high"].rolling(15).max().shift(1)
    dc_low = d["low"].rolling(15).min().shift(1)
    atr = true_range(d).rolling(14).mean()
    adx_series, plus_di, minus_di = adx(d, 14)
    adx_slope = adx_series.diff()
    delta = d["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rsi = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    rsi = rsi.fillna(50)
    vol_spike = d["volume"] > d["volume"].rolling(20).mean() * 1.5
    body = (d["close"] - d["open"]).abs()
    strong_body = body > (d["high"] - d["low"]) * 0.5
    roc3 = d["close"].pct_change(3)
    ema_fast = d["close"].ewm(span=8, adjust=False).mean()
    ema_slow = d["close"].ewm(span=21, adjust=False).mean()
    el = ((d["close"] > dc_high + 0.2 * atr) & (plus_di > minus_di) & (adx_series > 30) & (adx_slope > 0)
          & vol_spike & strong_body & (rsi > 55) & (rsi < 72) & (roc3 > 0.005) & (ema_fast > ema_slow))
    es = ((d["close"] < dc_low - 0.2 * atr) & (minus_di > plus_di) & (adx_series > 30) & (adx_slope > 0)
          & vol_spike & strong_body & (rsi < 45) & (rsi > 25) & (roc3 < -0.005) & (ema_fast < ema_slow))
    return el.fillna(False), es.fillna(False)


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    df = pd.DataFrame({k: payload[k] for k in ("open", "high", "low", "close", "volume")})
    enter_long, enter_short = eval_entry_breakout(df)
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"enter_long": enter_long.tolist(), "enter_short": enter_short.tolist()},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "entry-breakout-evaluated",
        "brick_id": CONCEPT["id"],
        "kind": "analytics",
        "label": "Evaluated breakout entry signals.",
        "refs": [],
        "data": {
            "long_signals": sum(bool(x) for x in output_packet["payload"]["enter_long"]),
            "short_signals": sum(bool(x) for x in output_packet["payload"]["enter_short"]),
        },
    }]
