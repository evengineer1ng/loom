from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.adx_signal_kit",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.frame_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.adx", "math.plus_di", "math.minus_di"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "adx"],
    "description": "Compute ADX, plus_di, and minus_di from OHLC series using the local pure-pandas kit.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [field for field in ("high", "low", "close") if not isinstance(payload.get(field), list)]
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


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    period = int(payload.get("period") or 14)
    df = pd.DataFrame({"high": payload["high"], "low": payload["low"], "close": payload["close"]})
    adx_series, plus_di, minus_di = adx(df, period)
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {
            "adx": adx_series.tolist(),
            "plus_di": plus_di.tolist(),
            "minus_di": minus_di.tolist(),
            "period": period,
        },
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "adx-kit-computed",
        "brick_id": CONCEPT["id"],
        "kind": "analytics",
        "label": "Computed ADX signal kit.",
        "refs": [],
        "data": {"period": output_packet["payload"]["period"]},
    }]
