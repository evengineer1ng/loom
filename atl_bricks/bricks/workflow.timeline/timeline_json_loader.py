from __future__ import annotations

import json
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "workflow.timeline.timeline_json_loader",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["workflow.timeline_request.v1"],
    "outputs": ["workflow.timeline_response.v1"],
    "requires": [],
    "provides": ["workflow.load_timeline_json"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["workflow", "timeline", "json"],
    "description": "Load a timeline JSON file into normalized timeline step dictionaries.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def load_timeline_json(path: str) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise RuntimeError(f"Timeline file must be a list: {path}")
    return [{"type": str(x.get("type", "")).strip(), "params": dict(x.get("params", {}) or {})} for x in data if isinstance(x, dict)]


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    path = str(payload.get("path") or "")
    value = load_timeline_json(path)
    output_packet = {
        "packet_type": "workflow.timeline_response.v1",
        "packet_version": "workflow.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"value": value},
        "refs": [path],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "timeline-json-loaded",
        "brick_id": CONCEPT["id"],
        "kind": "file_read",
        "label": "Loaded timeline JSON.",
        "refs": output_packet["refs"],
        "data": {"count": len(output_packet["payload"]["value"])},
    }]
