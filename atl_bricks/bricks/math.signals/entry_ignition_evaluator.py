from __future__ import annotations

from typing import Any

import pandas as pd


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.entry_ignition_evaluator",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.frame_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.eval_entry_ignition"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "entry", "ignition"],
    "description": "Evaluate pure-pandas ignition entry conditions and return long/short boolean series.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [field for field in ("open", "high", "low", "close", "volume") if not isinstance(payload.get(field), list)]
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


def eval_entry_ignition(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    d = df.copy()
    d["volume_avg"] = d["volume"].rolling(20).mean()
    d["range"] = d["high"] - d["low"]
    d["range_avg"] = d["range"].rolling(20).mean()
    d["atr"] = true_range(d).rolling(14).mean()
    d["atr_avg"] = d["atr"].rolling(20).mean()
    d["delta_abs"] = (d["close"] - d["close"].shift(1)).abs()
    d["delta_avg"] = d["delta_abs"].rolling(20).mean()
    d["delta_pct"] = (d["close"] - d["close"].shift(1)) / d["close"].shift(1) * 100
    quiet = ((d["volume"] < d["volume_avg"] * 1.05).astype(int)
             + (d["range"] < d["range_avg"] * 1.05).astype(int)
             + (d["atr"] < d["atr_avg"] * 1.05).astype(int)) >= 2
    quiet_count = quiet.rolling(5).sum()
    expand = ((d["volume"] / d["volume_avg"]).fillna(0) + (d["range"] / d["range_avg"]).fillna(0)
              + (d["atr"] / d["atr_avg"]).fillna(0) + (d["delta_abs"] / d["delta_avg"]).fillna(0)) / 4.0
    expansion_event = (expand >= 1.5) & (d["delta_pct"].abs() > 0.12)
    first_expansion = expansion_event & ~expansion_event.shift(1, fill_value=False)
    ignition = first_expansion & (quiet_count >= 1)
    ignition = ignition & ~(ignition.shift(1, fill_value=False) | ignition.shift(2, fill_value=False))
    body = (d["close"] - d["open"]).abs()
    readable = body > (d["range"] * 0.20)
    range_contracted = d["range"].rolling(3).mean() < d["range_avg"] * 1.15
    el = ignition & (d["close"] > d["open"]) & readable & (d["close"] > d["close"].shift(1)) & range_contracted
    es = ignition & (d["close"] < d["open"]) & readable & (d["close"] < d["close"].shift(1)) & range_contracted
    return el.fillna(False), es.fillna(False)


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    df = pd.DataFrame({k: payload[k] for k in ("open", "high", "low", "close", "volume")})
    enter_long, enter_short = eval_entry_ignition(df)
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
        "receipt_id": "entry-ignition-evaluated",
        "brick_id": CONCEPT["id"],
        "kind": "analytics",
        "label": "Evaluated ignition entry signals.",
        "refs": [],
        "data": {
            "long_signals": sum(bool(x) for x in output_packet["payload"]["enter_long"]),
            "short_signals": sum(bool(x) for x in output_packet["payload"]["enter_short"]),
        },
    }]
