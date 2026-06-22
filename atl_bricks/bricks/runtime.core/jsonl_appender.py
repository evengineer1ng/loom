from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.jsonl_appender",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.file_request.v1"],
    "outputs": ["storage.file_record.v1"],
    "requires": [],
    "provides": ["storage.append_jsonl"],
    "side_effects": ["file_write"],
    "ui_slots": [],
    "tags": ["jsonl", "append", "storage"],
    "description": "Append one JSON object as a line to a JSONL file, creating parents as needed.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    path = Path(str(payload.get("path") or ""))
    value = dict(payload.get("value") or {})
    append_jsonl(path, value)
    output_packet = {
        "packet_type": "storage.file_record.v1",
        "packet_version": "storage.file_record.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"path": str(path), "appended": True},
        "refs": [str(path)],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "jsonl-appended",
        "brick_id": CONCEPT["id"],
        "kind": "file_write",
        "label": "Appended JSON object to JSONL file.",
        "refs": output_packet["refs"],
        "data": output_packet["payload"],
    }]
