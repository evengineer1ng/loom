from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "archive.ml.team_outcome_training_read_model",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["archive.ml_request.v1"],
    "outputs": ["archive.ml_response.v1"],
    "requires": [],
    "provides": ["archive.team_outcome_training_read_model"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["archive", "ml", "team", "outcomes", "training"],
    "description": "Filter and normalize team outcome success records into a portable training read model.",
}


def build_team_outcome_training_read_model(
    records: list[dict[str, Any]] | None,
    team_id: str | None = None,
    min_budget_health: float | None = None,
    min_roi: float | None = None,
    survived_only: bool = False,
    limit: int = 1000,
) -> dict[str, Any]:
    rows = []
    for record in records or []:
        row = dict(record)
        if team_id and str(row.get("team_id") or "") != str(team_id):
            continue
        if min_budget_health is not None and float(row.get("budget_health_score") or 0.0) < float(min_budget_health):
            continue
        if min_roi is not None and float(row.get("roi_score") or 0.0) < float(min_roi):
            continue
        if survived_only and not bool(row.get("survival_flag")):
            continue
        rows.append(row)
    rows.sort(key=lambda row: int(row.get("season") or 0), reverse=True)
    rows = rows[: max(int(limit), 0)]
    return {
        "records": rows,
        "record_count": len(rows),
        "survived_count": sum(1 for row in rows if bool(row.get("survival_flag"))),
        "avg_budget_health": (sum(float(row.get("budget_health_score") or 0.0) for row in rows) / len(rows)) if rows else 0.0,
        "avg_roi_score": (sum(float(row.get("roi_score") or 0.0) for row in rows) / len(rows)) if rows else 0.0,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_team_outcome_training_read_model(
        records=list(payload.get("records") or []),
        team_id=payload.get("team_id"),
        min_budget_health=payload.get("min_budget_health"),
        min_roi=payload.get("min_roi"),
        survived_only=bool(payload.get("survived_only", False)),
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
        "receipt_id": "team-outcome-training-read-model",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Built team outcome training read model.",
        "refs": [],
        "data": {"record_count": value.get("record_count", 0), "survived_count": value.get("survived_count", 0)},
    }]
