from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.maintenance.memory_decay_promotion_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧠",
    "deterministic": True,
    "inputs": ["history.maintenance_request.v1"],
    "outputs": ["history.maintenance_response.v1"],
    "requires": [],
    "provides": ["history.memory_decay_promotion_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "maintenance", "memory", "decay", "promotion"],
    "description": "Package memory-shelf maintenance with salience decay, myth-tier promotion, and forgetting rules for weak records.",
}


def build_memory_decay_promotion_packet(
    tick: int,
    surviving_records: list[dict[str, Any]] | None,
    forgotten_record_ids: list[str] | None,
    promoted_record_ids: list[str] | None,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "surviving_records": [dict(item) for item in (surviving_records or [])],
        "forgotten_record_ids": [str(item) for item in (forgotten_record_ids or [])],
        "promoted_record_ids": [str(item) for item in (promoted_record_ids or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_memory_decay_promotion_packet(
        tick=int(payload.get("tick") or 0),
        surviving_records=list(payload.get("surviving_records") or []),
        forgotten_record_ids=list(payload.get("forgotten_record_ids") or []),
        promoted_record_ids=list(payload.get("promoted_record_ids") or []),
    )
    output_packet = {
        "packet_type": "history.maintenance_response.v1",
        "packet_version": "history.maintenance_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "memory-decay-promotion-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built memory-decay-promotion packet.",
        "refs": [],
        "data": {
            "survivor_count": len(value.get("surviving_records", [])),
            "forgotten_count": len(value.get("forgotten_record_ids", [])),
            "promoted_count": len(value.get("promoted_record_ids", [])),
        },
    }]
