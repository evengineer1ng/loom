from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.trades.tag_conversion_matrix",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.trades_request.v1"],
    "outputs": ["analytics.trades_response.v1"],
    "requires": [],
    "provides": ["analytics.entry_tag_conversion_matrix"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "trades", "tags", "conversion"],
    "description": "Build per-entry-tag conversion rows for a chosen exit bucket.",
}


def entry_tag_conversion_matrix(trades: list[dict[str, Any]] | None, exit_reason: str) -> list[dict[str, Any]]:
    rows = [dict(item) for item in (trades or [])]
    selected_reason = str(exit_reason or "")
    sub = [row for row in rows if str(row.get("exit_reason") or "") == selected_reason]
    tags = sorted({str(row.get("enter_tag") or "") for row in rows})
    out: list[dict[str, Any]] = []
    for tag in tags:
        tag_rows = [row for row in rows if str(row.get("enter_tag") or "") == tag]
        bucket_rows = [row for row in sub if str(row.get("enter_tag") or "") == tag]
        if not bucket_rows:
            continue
        total = len(tag_rows)
        wins = sum(1 for row in bucket_rows if float(row.get("profit_abs") or 0.0) > 0)
        avg_roi = sum(float(row.get("profit_ratio") or 0.0) for row in bucket_rows) / len(bucket_rows)
        pnl = sum(float(row.get("profit_abs") or 0.0) for row in bucket_rows)
        out.append({
            "enter_tag": tag,
            "n_in_bucket": len(bucket_rows),
            "tag_total": total,
            "conversion_pct": round(len(bucket_rows) / total * 100, 0) if total else 0.0,
            "win_pct": round(wins / len(bucket_rows) * 100, 0),
            "avg_roi": round(avg_roi * 100, 2),
            "pnl": round(pnl, 1),
        })
    return out


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = entry_tag_conversion_matrix(list(payload.get("trades") or []), str(payload.get("exit_reason") or ""))
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


def receipts(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "tag-conversion-matrix",
        "brick_id": CONCEPT["id"],
        "kind": "analysis",
        "label": "Built entry-tag conversion matrix.",
        "refs": [],
        "data": {"rows": len(value)},
    }]
