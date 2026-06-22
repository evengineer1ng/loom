from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.trades.trade_bucket_metrics",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.trades_request.v1"],
    "outputs": ["analytics.trades_response.v1"],
    "requires": [],
    "provides": ["analytics.trade_bucket_metrics"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "trades", "buckets"],
    "description": "Compute bucket-level counts, win rates, mean ROI, and total PnL for a filtered trade cohort.",
}


def trade_bucket_metrics(trades: list[dict[str, Any]] | None) -> dict[str, Any]:
    rows = [dict(item) for item in (trades or [])]
    if not rows:
        return {"count": 0, "win_rate": 0.0, "avg_roi": 0.0, "pnl": 0.0}
    pnl_values = [float(row.get("profit_abs") or 0.0) for row in rows]
    roi_values = [float(row.get("profit_ratio") or 0.0) for row in rows]
    wins = sum(1 for value in pnl_values if value > 0)
    return {
        "count": len(rows),
        "win_rate": round(wins / len(rows) * 100, 1),
        "avg_roi": round(sum(roi_values) / len(rows) * 100, 2),
        "pnl": round(sum(pnl_values), 1),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = trade_bucket_metrics(input_packet.get("payload"))
    output_packet = {
        "packet_type": "analytics.trades_response.v1",
        "packet_version": "analytics.trades_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "trade-bucket-metrics",
        "brick_id": CONCEPT["id"],
        "kind": "analysis",
        "label": "Computed trade bucket metrics.",
        "refs": [],
        "data": {"count": value.get("count", 0), "pnl": value.get("pnl", 0.0)},
    }]
