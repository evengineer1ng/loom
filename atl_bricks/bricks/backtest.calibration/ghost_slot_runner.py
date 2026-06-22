from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.ghost_slot_runner",
    "kind": "world_operator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.ghost_run_slot"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "ghost", "runner"],
    "description": "Compose evaluator selection, trade simulation, and slot aggregation into an honest ghost scouting runner.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [field for field in ("entry_slug", "entry_registry", "exit_registry", "pair_frames", "tf_min") if field not in payload]
    if missing:
        return [{"code": "missing_fields", "message": f"Missing payload fields: {', '.join(missing)}"}]
    return []


def exit_reason(exit_mode: str, profit: float, minutes: float, is_short: bool) -> str | None:
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


def ghost_paper_trade(close: list[float], enter_long: list[bool], enter_short: list[bool], exit_mode: str, tf_min: int, stop: float = -0.03, max_minutes: int = 2880, stake: float = 100.0) -> list[dict[str, Any]]:
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
            r = exit_reason(exit_mode, profit, minutes, is_short)
            if r:
                reason = r
                break
            if minutes >= max_minutes:
                reason = "max_hold"
                break
            j += 1
        if j >= n:
            j = n - 1
            reason = reason or "force_exit"
            last = float(close[j])
            profit = (entry_price - last) / entry_price if is_short else (last - entry_price) / entry_price
        trades.append({"profit_ratio": float(profit), "profit_abs": float(profit * stake), "minutes": int((j - i) * tf_min), "reason": reason, "is_short": is_short})
        i = j + 1
    return trades


def aggregate_ghost_slot(trades: list[dict[str, Any]], exchange: str, timeframe: str, used_pairs: int, exit_approximated: bool = False) -> dict[str, Any]:
    import json
    from collections import Counter
    trade_count = len(trades)
    pnl = sum(float(t.get("profit_abs") or 0.0) for t in trades)
    wins = sum(1 for t in trades if float(t.get("profit_ratio") or 0.0) > 0)
    equity = 0.0
    peak = 0.0
    mdd = 0.0
    for trade in sorted(trades, key=lambda row: row.get("minutes", 0)):
        equity += float(trade.get("profit_abs") or 0.0)
        peak = max(peak, equity)
        mdd = max(mdd, peak - equity)
    return {
        "trades": trade_count,
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl / 100.0, 2) if trade_count else 0.0,
        "avg_roi": round(sum(float(t.get("profit_ratio") or 0.0) for t in trades) / trade_count * 100, 3) if trade_count else 0.0,
        "win_rate": round(wins / trade_count * 100, 1) if trade_count else 0.0,
        "max_drawdown": round(mdd, 2),
        "avg_hold_minutes": round(sum(int(t.get("minutes") or 0) for t in trades) / trade_count, 1) if trade_count else 0.0,
        "exit_tag_distribution_json": json.dumps(dict(Counter(str(t.get("reason") or "") for t in trades))),
        "evidence_source": f"ghost:{exchange}:{timeframe}:{used_pairs}pairs" + (":exit~stop" if exit_approximated else ""),
    }


def ghost_run_slot(entry_slug: str, exit_slug: str, entry_registry: dict[str, Any], exit_registry: dict[str, Any], pair_frames: list[dict[str, Any]], tf_min: int, exchange: str, timeframe: str, stop: float = -0.03, max_minutes: int = 2880, stake: float = 100.0) -> dict[str, Any] | None:
    entry_fn = entry_registry.get(entry_slug)
    if entry_fn is None:
        return None
    exit_approximated = exit_slug not in exit_registry
    all_trades: list[dict[str, Any]] = []
    used = 0
    for frame in pair_frames:
        close = list(frame.get("close") or [])
        if len(close) < 60:
            continue
        try:
            enter_long, enter_short = entry_fn(frame)
            trades = ghost_paper_trade(close, list(enter_long), list(enter_short), exit_slug, tf_min=tf_min, stop=stop, max_minutes=max_minutes, stake=stake)
            all_trades.extend(trades)
            used += 1
        except Exception:
            continue
    if used == 0:
        return None
    return aggregate_ghost_slot(all_trades, exchange=exchange, timeframe=timeframe, used_pairs=used, exit_approximated=exit_approximated)


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    value = ghost_run_slot(
        entry_slug=str(payload["entry_slug"]),
        exit_slug=str(payload.get("exit_slug") or "__stop_only__"),
        entry_registry=dict(payload["entry_registry"]),
        exit_registry=dict(payload["exit_registry"]),
        pair_frames=list(payload["pair_frames"]),
        tf_min=int(payload["tf_min"]),
        exchange=str(payload.get("exchange") or ""),
        timeframe=str(payload.get("timeframe") or ""),
        stop=float(payload.get("stop") or -0.03),
        max_minutes=int(payload.get("max_minutes") or 2880),
        stake=float(payload.get("stake") or 100.0),
    )
    output_packet = {
        "packet_type": "backtest.sim_response.v1",
        "packet_version": "backtest.sim_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": value is not None, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [] if value is not None else [{"code": "unrunnable", "message": "Entry genome had no runnable evaluator or no usable frames."}], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet["payload"] or {}
    return [{
        "receipt_id": "ghost-slot-run-complete",
        "brick_id": CONCEPT["id"],
        "kind": "simulation",
        "label": "Ran composed ghost slot scouting flow.",
        "refs": [],
        "data": {"trades": payload.get("trades", 0), "pnl": payload.get("pnl", 0.0)},
    }]
