from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.timeline.futuresight_timeline_item_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔮",
    "deterministic": True,
    "inputs": ["runtime.timeline_request.v1"],
    "outputs": ["runtime.timeline_response.v1"],
    "requires": [],
    "provides": ["runtime.futuresight_timeline_item_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "timeline", "futuresight", "item", "schedule"],
    "description": "Package a FutureSight timeline item with offset, kind, label, payload, and enabled state for scheduled visual or other ingest.",
}


def build_futuresight_timeline_item_packet(
    item_id: str,
    enabled: bool,
    offset_sec: float,
    label: str,
    kind: str,
    payload: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "item_id": str(item_id),
        "enabled": bool(enabled),
        "offset_sec": float(offset_sec),
        "label": str(label),
        "kind": str(kind),
        "payload": dict(payload or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_futuresight_timeline_item_packet(
        item_id=str(payload.get("item_id") or ""),
        enabled=bool(payload.get("enabled")),
        offset_sec=float(payload.get("offset_sec") or 0.0),
        label=str(payload.get("label") or ""),
        kind=str(payload.get("kind") or ""),
        payload=dict(payload.get("item_payload") or payload.get("payload") or {}),
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
        "receipt_id": "futuresight-timeline-item-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built FutureSight timeline-item packet.",
        "refs": [],
        "data": {
            "item_id": value.get("item_id", ""),
            "kind": value.get("kind", ""),
            "offset_sec": value.get("offset_sec", 0.0),
        },
    }]
