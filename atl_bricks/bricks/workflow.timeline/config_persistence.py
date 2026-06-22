from __future__ import annotations

import json
import os
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "workflow.timeline.config_persistence",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["workflow.timeline_request.v1"],
    "outputs": ["workflow.timeline_response.v1"],
    "requires": [],
    "provides": ["workflow.load_config_json", "workflow.save_config_json"],
    "side_effects": ["file_read", "file_write"],
    "ui_slots": [],
    "tags": ["workflow", "timeline", "persistence"],
    "description": "Load and save JSON config state with atomic replace semantics.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def load_cfg(path: str) -> dict[str, Any]:
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def save_cfg(path: str, cfg: dict[str, Any]) -> bool:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(cfg, handle, indent=2)
    os.replace(tmp, path)
    return True


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    operation = str(payload.get("operation") or "load")
    path = str(payload.get("path") or "")
    if operation == "save":
        ok = save_cfg(path, dict(payload.get("value") or {}))
        value: Any = {"saved": ok}
    else:
        value = load_cfg(path)
    output_packet = {
        "packet_type": "workflow.timeline_response.v1",
        "packet_version": "workflow.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"value": value},
        "refs": [path] if path else [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "config-persistence-complete",
        "brick_id": CONCEPT["id"],
        "kind": "storage",
        "label": "Completed config persistence operation.",
        "refs": output_packet["refs"],
        "data": {"has_value": bool(output_packet["payload"]["value"])},
    }]
