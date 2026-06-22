from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "archive.query.decision_history_read_model",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["archive.query_request.v1"],
    "outputs": ["archive.query_response.v1"],
    "requires": [],
    "provides": ["archive.decision_history_read_model"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["archive", "query", "decision", "history"],
    "description": "Filter and normalize decision history into a portable read model ordered newest first.",
}


def build_decision_history_read_model(
    records: list[dict[str, Any]] | None,
    categories: list[str] | None = None,
    seasons: list[int] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    category_filter = set(categories or [])
    season_filter = set(int(value) for value in (seasons or []))
    rows = []
    for record in records or []:
        row = dict(record)
        if category_filter and str(row.get("category") or "") not in category_filter:
            continue
        if season_filter and int(row.get("season") or 0) not in season_filter:
            continue
        rows.append(row)
    rows.sort(key=lambda row: int(row.get("tick") or 0), reverse=True)
    if limit is not None:
        rows = rows[: max(int(limit), 0)]
    return {
        "records": rows,
        "record_count": len(rows),
        "categories": sorted({str(row.get("category") or "") for row in rows if row.get("category")}),
        "resolved_by_counts": _counts(rows, "resolved_by"),
    }


def _counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        label = str(row.get(key) or "unknown")
        counts[label] = counts.get(label, 0) + 1
    return counts


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_decision_history_read_model(
        records=list(payload.get("records") or []),
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
        "receipt_id": "decision-history-read-model",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Built decision history read model.",
        "refs": [],
        "data": {"record_count": value.get("record_count", 0)},
    }]
