from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.metrics.character_usage_summary_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📈",
    "deterministic": True,
    "inputs": ["history.metrics_request.v1"],
    "outputs": ["history.metrics_response.v1"],
    "requires": [],
    "provides": ["history.character_usage_summary_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "metrics", "character", "usage", "balance"],
    "description": "Package character-usage summaries with total counts, percentages, balance score, and underused or overused voice lists.",
}


def build_character_usage_summary_packet(
    total: int,
    characters: dict[str, Any] | None,
    percentages: dict[str, Any] | None,
    balance_score: float,
    underused: list[str] | None,
    overused: list[str] | None,
) -> dict[str, Any]:
    return {
        "total": int(total),
        "characters": dict(characters or {}),
        "percentages": dict(percentages or {}),
        "balance_score": float(balance_score),
        "underused": [str(item) for item in (underused or [])],
        "overused": [str(item) for item in (overused or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_character_usage_summary_packet(
        total=int(payload.get("total") or 0),
        characters=dict(payload.get("characters") or {}),
        percentages=dict(payload.get("percentages") or {}),
        balance_score=float(payload.get("balance_score") or 0.0),
        underused=list(payload.get("underused") or []),
        overused=list(payload.get("overused") or []),
    )
    output_packet = {
        "packet_type": "history.metrics_response.v1",
        "packet_version": "history.metrics_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "character-usage-summary-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built character-usage summary packet.",
        "refs": [],
        "data": {
            "total": value.get("total", 0),
            "balance_score": value.get("balance_score", 0.0),
            "underused_count": len(value.get("underused", [])),
        },
    }]
