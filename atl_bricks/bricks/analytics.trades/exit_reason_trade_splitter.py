from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.trades.exit_reason_trade_splitter",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.trade_window_request.v1"],
    "outputs": ["analytics.trade_window_response.v1"],
    "requires": [],
    "provides": ["analytics.split_trades_by_exit_reason"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["trades", "exit", "split"],
    "description": "Split closed trades into forced-exit and strategy-exit cohorts and summarize both groups.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if "records" not in payload:
        return [{"code": "missing_records", "message": "payload.records is required."}]
    if "forced_exit_reasons" not in payload:
        return [{"code": "missing_forced_exit_reasons", "message": "payload.forced_exit_reasons is required."}]
    return []


def parse_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def percentage(total: float, count: int) -> float:
    return (total / count) * 100.0 if count else 0.0


def split_trades(records: list[dict[str, Any]], forced_exit_reasons: set[str]) -> dict[str, Any]:
    forced = [r for r in records if str(r.get("exit_reason") or "").lower() in forced_exit_reasons]
    strategy = [r for r in records if str(r.get("exit_reason") or "").lower() not in forced_exit_reasons]

    def pnl(rows: list[dict[str, Any]]) -> float:
        return round(sum(parse_float(r.get("realized_profit")) or parse_float(r.get("close_profit_abs")) for r in rows), 4)

    def wins(rows: list[dict[str, Any]]) -> int:
        return sum(1 for r in rows if parse_float(r.get("close_profit_abs")) > 0)

    s_wins = wins(strategy)
    all_wins = wins(records)
    return {
        "closed_trades": len(records),
        "wins": all_wins,
        "losses": max(0, len(records) - all_wins),
        "win_rate": percentage(all_wins, len(records)),
        "avg_roi": percentage(sum(parse_float(r.get("close_profit")) for r in records), len(records)),
        "realized_pnl": pnl(records),
        "forced_exits": len(forced),
        "forced_realized_pnl": pnl(forced),
        "strategy_closed_trades": len(strategy),
        "strategy_wins": s_wins,
        "strategy_win_rate": percentage(s_wins, len(strategy)),
        "strategy_avg_roi": percentage(sum(parse_float(r.get("close_profit")) for r in strategy), len(strategy)),
        "strategy_realized_pnl": pnl(strategy),
    }


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    records = list(payload.get("records") or [])
    forced_exit_reasons = {str(value).lower() for value in payload.get("forced_exit_reasons") or []}
    summary = split_trades(records, forced_exit_reasons)
    output_packet = {
        "packet_type": "analytics.trade_window_response.v1",
        "packet_version": "analytics.trade_window_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": summary,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {
        "ok": True,
        "output_packet": output_packet,
        "receipts": receipts(output_packet),
        "issues": [],
        "meta": {},
    }


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "receipt_id": "exit-reason-trades-split",
            "brick_id": CONCEPT["id"],
            "kind": "analytics",
            "label": "Split trades by forced vs strategy exit reasons.",
            "refs": [],
            "data": {
                "closed_trades": output_packet["payload"]["closed_trades"],
                "forced_exits": output_packet["payload"]["forced_exits"],
            },
        }
    ]
