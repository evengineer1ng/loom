from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "archive.ml.ai_decision_training_read_model",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["archive.ml_request.v1"],
    "outputs": ["archive.ml_response.v1"],
    "requires": [],
    "provides": ["archive.ai_decision_training_read_model"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["archive", "ml", "ai", "decision", "training"],
    "description": "Filter and normalize logged AI team decisions into a portable training read model.",
}


def build_ai_decision_training_read_model(
    records: list[dict[str, Any]] | None,
    team_id: str | None = None,
    season: int | None = None,
    min_tick: int | None = None,
    limit: int = 1000,
) -> dict[str, Any]:
    rows = []
    for record in records or []:
        row = dict(record)
        if team_id and str(row.get("team_id") or "") != str(team_id):
            continue
        if season is not None and int(row.get("season") or 0) != int(season):
            continue
        if min_tick is not None and int(row.get("tick") or 0) < int(min_tick):
            continue
        rows.append(row)
    rows.sort(key=lambda row: int(row.get("tick") or 0), reverse=True)
    rows = rows[: max(int(limit), 0)]
    return {
        "records": rows,
        "record_count": len(rows),
        "teams": sorted({str(row.get("team_name") or "") for row in rows if row.get("team_name")}),
        "action_names": sorted({str(dict(row.get("action_chosen") or {}).get("name") or "") for row in rows if row.get("action_chosen")}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_ai_decision_training_read_model(
        records=list(payload.get("records") or []),
        team_id=payload.get("team_id"),
        season=payload.get("season"),
        min_tick=payload.get("min_tick"),
        limit=int(payload.get("limit") or 1000),
    )
    output_packet = {
        "packet_type": "archive.ml_response.v1",
        "packet_version": "archive.ml_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "ai-decision-training-read-model",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Built AI decision training read model.",
        "refs": [],
        "data": {"record_count": value.get("record_count", 0)},
    }]
