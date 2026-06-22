from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "archive.query.financial_transaction_read_model",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["archive.query_request.v1"],
    "outputs": ["archive.query_response.v1"],
    "requires": [],
    "provides": ["archive.financial_transaction_read_model"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["archive", "query", "finance", "transactions"],
    "description": "Filter and summarize financial transactions into a portable read model.",
}


def build_financial_transaction_read_model(
    records: list[dict[str, Any]] | None,
    tx_type: str | None = None,
    categories: list[str] | None = None,
    seasons: list[int] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    category_filter = set(categories or [])
    season_filter = set(int(value) for value in (seasons or []))
    rows = []
    for record in records or []:
        row = dict(record)
        if tx_type and str(row.get("type") or "") != str(tx_type):
            continue
        if category_filter and str(row.get("category") or "") not in category_filter:
            continue
        if season_filter and int(row.get("season") or 0) not in season_filter:
            continue
        rows.append(row)
    rows.sort(key=lambda row: int(row.get("tick") or 0), reverse=True)
    if limit is not None:
        rows = rows[: max(int(limit), 0)]
    income_total = sum(float(row.get("amount") or 0.0) for row in rows if str(row.get("type") or "") == "income")
    expense_total = sum(float(row.get("amount") or 0.0) for row in rows if str(row.get("type") or "") == "expense")
    return {
        "records": rows,
        "record_count": len(rows),
        "income_total": income_total,
        "expense_total": expense_total,
        "net_flow": income_total - expense_total,
        "categories": sorted({str(row.get("category") or "") for row in rows if row.get("category")}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_financial_transaction_read_model(
        records=list(payload.get("records") or []),
        tx_type=payload.get("type"),
        categories=list(payload.get("categories") or []),
        seasons=list(payload.get("seasons") or []),
        limit=payload.get("limit"),
    )
    output_packet = {
        "packet_type": "archive.query_response.v1",
        "packet_version": "archive.query_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "financial-transaction-read-model",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Built financial transaction read model.",
        "refs": [],
        "data": {"record_count": value.get("record_count", 0), "net_flow": value.get("net_flow", 0.0)},
    }]
