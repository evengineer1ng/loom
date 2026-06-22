from __future__ import annotations

import json
import os
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "workflow.timeline.json_object_loader",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["workflow.timeline_request.v1"],
    "outputs": ["workflow.timeline_response.v1"],
    "requires": [],
    "provides": ["workflow.load_json_object_arg"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["workflow", "json", "loader"],
    "description": "Load a JSON object from either a filesystem path or an inline JSON string.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def load_json_arg(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    candidate = os.path.expanduser(value)
    if os.path.exists(candidate):
        with open(candidate, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    else:
        data = json.loads(value)
    if not isinstance(data, dict):
        raise RuntimeError("JSON payload must decode to an object")
    return data


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    value = load_json_arg(payload.get("value"))
    output_packet = {
        "packet_type": "workflow.timeline_response.v1",
        "packet_version": "workflow.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"value": value},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "json-object-loaded",
        "brick_id": CONCEPT["id"],
        "kind": "file_read",
        "label": "Loaded JSON object argument.",
        "refs": [],
        "data": {"keys": sorted(output_packet["payload"]["value"].keys())},
    }]
