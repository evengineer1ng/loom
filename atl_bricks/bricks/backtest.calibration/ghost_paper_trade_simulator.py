from __future__ import annotations

from typing import Any

import pandas as pd


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.ghost_paper_trade_simulator",
    "kind": "world_operator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.ghost_paper_trade"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "ghost", "simulator"],
    "description": "Run a single-position paper trade simulator over tape using entry signals and an exit evaluator.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    required_lists = ("close", "enter_long", "enter_short")
    missing = [field for field in required_lists if not isinstance(payload.get(field), list)]
    if missing:
        return [{"code": "missing_fields", "message": f"payload lists required: {', '.join(missing)}"}]
    return []


def ghost_paper_trade(
    close: list[float],
    enter_long: list[bool],
    enter_short: list[bool],
    exit_mode: str,
    tf_min: int,
    stop: float = -0.03,
    max_minutes: int = 2880,
    stake: float = 100.0,
) -> list[dict[str, Any]]:
    def exit_fn(profit: float, minutes: float, is_short: bool) -> str | None:
        if exit_mode == "roi-ladder-stop":
            for floor_min, roi in ((60, 0.01), (30, 0.025), (0, 0.05)):
                if minutes >= floor_min and profit >= roi:
                    return "roi"
            return None
        if exit_mode == "ignition-harvest":
            if profit > 0.012 and minutes <= 5:
                return "ignition_scalp"
            if profit > 0.025 and minutes > 5:
                return "ignition_runner"
            if minutes >= 20:
                return "ignition_time"
            if minutes >= 8 and abs(profit) < 0.003:
                return "ignition_time"
            return None
        return None

    n = len(close)
    trades: list[dict[str, Any]] = []
    i = 0
    while i < n - 1:
        go_long = bool(enter_long[i])
        go_short = bool(enter_short[i])
        if not (go_long or go_short):
            i += 1
            continue
        is_short = go_short and not go_long
        entry_price = float(close[i])
        if entry_price <= 0:
            i += 1
            continue
        j = i + 1
        reason = None
        profit = 0.0
        while j < n:
            price = float(close[j])
            profit = (entry_price - price) / entry_price if is_short else (price - entry_price) / entry_price
            minutes = (j - i) * tf_min
            if profit <= stop:
                reason = "stop_loss"
                break
            triggered = exit_fn(profit, minutes, is_short)
            if triggered:
                reason = triggered
                break
            if minutes >= max_minutes:
                reason = "max_hold"
                break
            j += 1
        if j >= n:
            j = n - 1
            reason = reason or "force_exit"
            last_price = float(close[j])
            profit = (entry_price - last_price) / entry_price if is_short else (last_price - entry_price) / entry_price
        trades.append({
            "profit_ratio": float(profit),
            "profit_abs": float(profit * stake),
            "minutes": int((j - i) * tf_min),
            "reason": reason,
            "is_short": is_short,
        })
        i = j + 1
    return trades


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    trades = ghost_paper_trade(
        close=[float(x) for x in payload["close"]],
        enter_long=[bool(x) for x in payload["enter_long"]],
        enter_short=[bool(x) for x in payload["enter_short"]],
        exit_mode=str(payload.get("exit_mode") or "__stop_only__"),
        tf_min=int(payload.get("tf_min") or 5),
        stop=float(payload.get("stop") or -0.03),
        max_minutes=int(payload.get("max_minutes") or 2880),
        stake=float(payload.get("stake") or 100.0),
    )
    output_packet = {
        "packet_type": "backtest.sim_response.v1",
        "packet_version": "backtest.sim_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"trades": trades, "count": len(trades)},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "ghost-paper-trades-simulated",
        "brick_id": CONCEPT["id"],
        "kind": "simulation",
        "label": "Ran ghost paper-trade simulation.",
        "refs": [],
        "data": {"count": output_packet["payload"]["count"]},
    }]
