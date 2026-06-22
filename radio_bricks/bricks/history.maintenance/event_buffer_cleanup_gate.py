from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.maintenance.event_buffer_cleanup_gate",
    "kind": "gate",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["history.maintenance_request.v1"],
    "outputs": ["history.maintenance_response.v1"],
    "requires": [],
    "provides": ["history.event_buffer_cleanup_decision"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "maintenance", "cleanup", "events"],
    "description": "Decide the archival cutoff for old event-buffer cleanup to prevent storage bloat.",
}


def build_event_buffer_cleanup_decision(max_tick: int, keep_recent_ticks: int = 1000) -> dict[str, Any]:
    cutoff_tick = int(max_tick) - int(keep_recent_ticks)
    return {
        "max_tick": int(max_tick),
        "keep_recent_ticks": int(keep_recent_ticks),
        "cutoff_tick": cutoff_tick,
        "cleanup_required": cutoff_tick > 0,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_event_buffer_cleanup_decision(
        max_tick=int(payload.get("max_tick") or 0),
        keep_recent_ticks=int(payload.get("keep_recent_ticks") or 1000),
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
        "receipt_id": "event-buffer-cleanup-decision",
        "brick_id": CONCEPT["id"],
        "kind": "decision",
        "label": "Built event-buffer cleanup decision.",
        "refs": [],
        "data": {"cutoff_tick": value.get("cutoff_tick", 0), "cleanup_required": value.get("cleanup_required", False)},
    }]
