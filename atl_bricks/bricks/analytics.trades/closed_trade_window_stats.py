from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.trades.closed_trade_window_stats",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.trade_window_request.v1"],
    "outputs": ["analytics.trade_window_response.v1"],
    "requires": [],
    "provides": ["analytics.closed_trade_window_stats"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["trades", "analytics", "window"],
    "description": "Compute closed-trade stats for records whose close_date falls inside a requested UTC window.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [field for field in ("records", "started_utc", "stopped_utc") if field not in payload]
    if missing:
        return [{"code": "missing_fields", "message": f"Missing payload fields: {', '.join(missing)}"}]
    return []


def resolve_optional_datetime(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def normalize_utc(moment: datetime | None) -> datetime | None:
    if not moment:
        return None
    if moment.tzinfo is None:
        return moment.replace(tzinfo=UTC)
    return moment.astimezone(UTC)


def parse_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def percentage(total: float, count: int) -> float:
    return (total / count) * 100.0 if count else 0.0


def trade_window_stats(records: list[dict[str, Any]], started_utc: datetime, stopped_utc: datetime) -> dict[str, Any]:
    stats = {"closed_trades": 0, "wins": 0, "losses": 0, "win_rate": 0.0, "avg_roi": 0.0, "realized_pnl": 0.0}
    filtered: list[dict[str, Any]] = []
    for record in records:
        close_date = normalize_utc(resolve_optional_datetime(str(record.get("close_date") or "")))
        if close_date and started_utc <= close_date <= stopped_utc:
            filtered.append(record)
    if not filtered:
        return stats
    stats["closed_trades"] = len(filtered)
    stats["wins"] = sum(1 for record in filtered if parse_float(record.get("close_profit_abs")) > 0)
    stats["losses"] = max(0, len(filtered) - stats["wins"])
    stats["win_rate"] = percentage(stats["wins"], len(filtered))
    stats["avg_roi"] = percentage(sum(parse_float(record.get("close_profit")) for record in filtered), len(filtered))
    stats["realized_pnl"] = round(
        sum(parse_float(record.get("realized_profit")) or parse_float(record.get("close_profit_abs")) for record in filtered),
        4,
    )
    return stats


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    records = list(payload.get("records") or [])
    started_utc = normalize_utc(resolve_optional_datetime(str(payload.get("started_utc") or "")))
    stopped_utc = normalize_utc(resolve_optional_datetime(str(payload.get("stopped_utc") or "")))
    if not started_utc or not stopped_utc:
        return {
            "ok": False,
            "output_packet": {},
            "receipts": [],
            "issues": [{"code": "invalid_window", "message": "Could not parse started_utc or stopped_utc."}],
            "meta": {},
        }
    stats = trade_window_stats(records, started_utc, stopped_utc)
    output_packet = {
        "packet_type": "analytics.trade_window_response.v1",
        "packet_version": "analytics.trade_window_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": stats,
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
            "receipt_id": "closed-trade-window-stats-computed",
            "brick_id": CONCEPT["id"],
            "kind": "analytics",
            "label": "Computed closed-trade window stats.",
            "refs": [],
            "data": {"closed_trades": output_packet["payload"]["closed_trades"]},
        }
    ]
