from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "archive.query.season_summary_read_model",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["archive.query_request.v1"],
    "outputs": ["archive.query_response.v1"],
    "requires": [],
    "provides": ["archive.season_summary_read_model"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["archive", "query", "season", "summary"],
    "description": "Filter and normalize season summaries into a portable league-history read model.",
}


def build_season_summary_read_model(records: list[dict[str, Any]] | None, seasons: list[int] | None = None) -> dict[str, Any]:
    season_filter = set(int(value) for value in (seasons or []))
    rows = []
    for record in records or []:
        row = dict(record)
        if season_filter and int(row.get("season") or 0) not in season_filter:
            continue
        rows.append(row)
    rows.sort(key=lambda row: int(row.get("season") or 0), reverse=True)
    return {
        "records": rows,
        "record_count": len(rows),
        "seasons": sorted({int(row.get("season") or 0) for row in rows}, reverse=True),
        "team_names": sorted({str(row.get("team_name") or "") for row in rows if row.get("team_name")}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_season_summary_read_model(
        records=list(payload.get("records") or []),
        seasons=list(payload.get("seasons") or []),
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
        "receipt_id": "season-summary-read-model",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Built season summary read model.",
        "refs": [],
        "data": {"record_count": value.get("record_count", 0)},
    }]
