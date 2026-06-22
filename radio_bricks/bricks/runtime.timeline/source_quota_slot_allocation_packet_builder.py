from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.timeline.source_quota_slot_allocation_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧮",
    "deterministic": True,
    "inputs": ["runtime.timeline_request.v1"],
    "outputs": ["runtime.timeline_response.v1"],
    "requires": [],
    "provides": ["runtime.source_quota_slot_allocation_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "timeline", "quota", "slots", "allocation"],
    "description": "Package source-quota slot allocation using normalized weights, largest-remainder rounding, and minimum-one-slot enforcement.",
}


def build_source_quota_slot_allocation_packet(
    total_slots: int,
    normalized_weights: dict[str, Any] | None,
    raw_slots: dict[str, Any] | None,
    allocated_slots: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "total_slots": int(total_slots),
        "normalized_weights": dict(normalized_weights or {}),
        "raw_slots": dict(raw_slots or {}),
        "allocated_slots": dict(allocated_slots or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_source_quota_slot_allocation_packet(
        total_slots=int(payload.get("total_slots") or 0),
        normalized_weights=dict(payload.get("normalized_weights") or {}),
        raw_slots=dict(payload.get("raw_slots") or {}),
        allocated_slots=dict(payload.get("allocated_slots") or {}),
    )
    output_packet = {
        "packet_type": "runtime.timeline_response.v1",
        "packet_version": "runtime.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "source-quota-slot-allocation-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built source-quota slot allocation packet.",
        "refs": [],
        "data": {
            "total_slots": value.get("total_slots", 0),
            "source_count": len(value.get("allocated_slots", {})),
        },
    }]
