from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.json_file_loader",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.file_request.v1"],
    "outputs": ["storage.json_payload.v1"],
    "requires": [],
    "provides": ["storage.load_json"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["json", "file", "storage"],
    "description": "Read JSON from disk with a fallback value when the path is missing.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    if not input_packet.get("payload", {}).get("path"):
        return [{"code": "missing_path", "message": "payload.path is required."}]
    return []


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    path = Path(str(payload["path"]))
    fallback = payload.get("fallback")
    value = load_json(path, fallback)
    output_packet = {
        "packet_type": "storage.json_payload.v1",
        "packet_version": "storage.json_payload.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"path": str(path), "value": value},
        "refs": [str(path)],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {
        "ok": True,
        "output_packet": output_packet,
        "receipts": receipts(output_packet),
        "issues": [],
        "meta": {},
    }


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "receipt_id": "json-file-read",
            "brick_id": CONCEPT["id"],
            "kind": "file_read",
            "label": "Loaded JSON from disk.",
            "refs": output_packet["refs"],
            "data": {"path": output_packet["payload"]["path"]},
        }
    ]
