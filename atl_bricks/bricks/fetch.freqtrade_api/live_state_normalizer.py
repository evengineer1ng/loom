from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.freqtrade_api.live_state_normalizer",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["fetch.http_response.v1"],
    "outputs": ["fetch.http_response.v1"],
    "requires": [],
    "provides": ["fetch.freqtrade_live_state_normalize"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["freqtrade", "live-state", "normalization"],
    "description": "Normalize raw Freqtrade profit, status, config, and balance payloads into a stable live-state record.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [field for field in ("entity_id", "captured_at", "starting_capital", "profit", "status", "config") if field not in payload]
    if missing:
        return [{"code": "missing_fields", "message": f"Missing payload fields: {', '.join(missing)}"}]
    return []


def parse_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def normalize_live_state(
    entity_id: str,
    captured_at: str,
    starting_capital: float,
    profit: dict[str, Any],
    status: Any,
    config: dict[str, Any],
    balance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    realized = parse_float(profit.get("profit_closed_coin"))
    total = parse_float(profit.get("profit_all_coin"))
    unrealized = total - realized
    equity = starting_capital + total
    if isinstance(balance, dict):
        equity = (
            parse_float(balance.get("total_bot"))
            or parse_float(balance.get("value_bot"))
            or parse_float(balance.get("total"))
            or parse_float(balance.get("value"))
            or equity
        )
    closed = int(profit.get("closed_trade_count") or 0)
    wins = int(profit.get("winning_trades") or 0)
    current_record = f"{wins}-{max(closed - wins, 0)}"
    if isinstance(status, list):
        open_trade_count = len(status)
    elif isinstance(status, dict) and isinstance(status.get("value"), list):
        open_trade_count = len(status.get("value", []))
    else:
        open_trade_count = 0
    return {
        "entity_id": entity_id,
        "captured_at": captured_at,
        "status": "online",
        "status_detail": "healthy",
        "bot_name": config.get("bot_name"),
        "strategy_name": config.get("strategy"),
        "strategy_version": config.get("strategy_version"),
        "current_record": current_record,
        "equity": equity,
        "realized_pnl": realized,
        "unrealized_pnl": unrealized,
        "total_pnl": total,
        "trade_count": int(profit.get("trade_count") or 0),
        "closed_trade_count": closed,
        "win_rate": parse_float(profit.get("winrate")) * 100.0,
        "avg_roi": parse_float(profit.get("profit_closed_ratio_mean")) * 100.0,
        "max_drawdown": parse_float(profit.get("max_drawdown")) * 100.0,
        "current_drawdown": parse_float(profit.get("current_drawdown")) * 100.0,
        "best_pair": profit.get("best_pair"),
        "best_rate": parse_float(profit.get("best_rate")),
        "last_trade_at": profit.get("latest_trade_date"),
        "bot_start_at": profit.get("bot_start_date"),
        "open_trade_count": open_trade_count,
        "heartbeat_ok": 1,
    }


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    state = normalize_live_state(
        entity_id=str(payload["entity_id"]),
        captured_at=str(payload["captured_at"]),
        starting_capital=parse_float(payload.get("starting_capital")),
        profit=dict(payload.get("profit") or {}),
        status=payload.get("status"),
        config=dict(payload.get("config") or {}),
        balance=dict(payload.get("balance") or {}) if isinstance(payload.get("balance"), dict) else None,
    )
    output_packet = {
        "packet_type": "fetch.http_response.v1",
        "packet_version": "fetch.http_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": state,
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
            "receipt_id": "freqtrade-live-state-normalized",
            "brick_id": CONCEPT["id"],
            "kind": "normalization",
            "label": "Normalized Freqtrade live payloads into a stable state record.",
            "refs": [],
            "data": {
                "entity_id": output_packet["payload"]["entity_id"],
                "open_trade_count": output_packet["payload"]["open_trade_count"],
            },
        }
    ]
