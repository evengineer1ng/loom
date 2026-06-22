from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.timeline.calendar_projection_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.timeline_request.v1"],
    "outputs": ["runtime.timeline_response.v1"],
    "requires": [],
    "provides": ["runtime.calendar_projection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "timeline", "calendar", "projection"],
    "description": "Merge competition, personnel, financial, and pressure entries into a sorted strategic calendar.",
}


def build_calendar_projection_packet(layers: dict[str, Any] | None) -> dict[str, Any]:
    source = dict(layers or {})
    entries: list[dict[str, Any]] = []
    for key in ("competition", "personnel", "financial", "pressure"):
        entries.extend([dict(item) for item in list(source.get(key) or [])])
    entries.sort(key=lambda item: (int(item.get("entry_day") or 0), -int(item.get("priority") or 50)))
    return {
        "entries": entries,
        "entry_count": len(entries),
        "action_required_count": sum(1 for item in entries if bool(item.get("action_required"))),
        "categories": sorted({str(item.get("category") or "") for item in entries if item.get("category")}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_calendar_projection_packet(dict(payload.get("layers") or {}))
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
        "receipt_id": "calendar-projection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built calendar projection packet.",
        "refs": [],
        "data": {"entry_count": value.get("entry_count", 0), "action_required_count": value.get("action_required_count", 0)},
    }]
