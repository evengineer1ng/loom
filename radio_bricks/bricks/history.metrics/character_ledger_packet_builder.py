from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.metrics.character_ledger_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📚",
    "deterministic": True,
    "inputs": ["history.metrics_request.v1"],
    "outputs": ["history.metrics_response.v1"],
    "requires": [],
    "provides": ["history.character_ledger_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "metrics", "character", "ledger"],
    "description": "Package a ForkUniverse character ledger with wins, losses, promises, touched threads, predictions, major events, and myth tags.",
}


def build_character_ledger_packet(
    wins: int,
    losses: int,
    promises_made: list[str] | None,
    promises_broken: list[str] | None,
    threads_touched: list[str] | None,
    predictions_about: list[str] | None,
    major_event_ids: list[str] | None,
    myth_tags: list[str] | None,
) -> dict[str, Any]:
    return {
        "wins": int(wins),
        "losses": int(losses),
        "promises_made": list(promises_made or []),
        "promises_broken": list(promises_broken or []),
        "threads_touched": list(threads_touched or []),
        "predictions_about": list(predictions_about or []),
        "major_event_ids": list(major_event_ids or []),
        "myth_tags": list(myth_tags or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_character_ledger_packet(
        wins=int(payload.get("wins") or 0),
        losses=int(payload.get("losses") or 0),
        promises_made=list(payload.get("promises_made") or []),
        promises_broken=list(payload.get("promises_broken") or []),
        threads_touched=list(payload.get("threads_touched") or []),
        predictions_about=list(payload.get("predictions_about") or []),
        major_event_ids=list(payload.get("major_event_ids") or []),
        myth_tags=list(payload.get("myth_tags") or []),
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
        "receipt_id": "character-ledger-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built character-ledger packet.",
        "refs": [],
        "data": {"wins": value.get("wins", 0), "myth_tag_count": len(value.get("myth_tags", []))},
    }]
