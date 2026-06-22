from __future__ import annotations

import json
from collections import Counter
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.ghost_slot_aggregator",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.aggregate_ghost_slot"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "ghost", "aggregation"],
    "description": "Aggregate ghost paper-trade outputs into scouting metrics for one entry-exit slot.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if not isinstance(payload.get("trades"), list):
        return [{"code": "missing_trades", "message": "payload.trades must be a list."}]
    return []


def aggregate_ghost_slot(
    trades: list[dict[str, Any]],
    exchange: str,
    timeframe: str,
    used_pairs: int,
    exit_approximated: bool = False,
) -> dict[str, Any]:
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


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    summary = aggregate_ghost_slot(
        trades=list(payload["trades"]),
        exchange=str(payload.get("exchange") or ""),
        timeframe=str(payload.get("timeframe") or ""),
        used_pairs=int(payload.get("used_pairs") or 0),
        exit_approximated=bool(payload.get("exit_approximated")),
    )
    output_packet = {
        "packet_type": "backtest.sim_response.v1",
        "packet_version": "backtest.sim_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": summary,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "ghost-slot-aggregated",
        "brick_id": CONCEPT["id"],
        "kind": "simulation",
        "label": "Aggregated ghost slot scouting metrics.",
        "refs": [],
        "data": {"trades": output_packet["payload"]["trades"], "pnl": output_packet["payload"]["pnl"]},
    }]
