from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "registry.settings.json_registry_loader",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["registry.request.v1"],
    "outputs": ["registry.response.v1"],
    "requires": ["storage.load_json"],
    "provides": ["registry.load_json_records"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["registry", "json", "records"],
    "description": "Load a JSON record registry from disk with a list fallback.",
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


def list_records(path: Path) -> list[dict[str, Any]]:
    raw = load_json(path, [])
    return raw if isinstance(raw, list) else []


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    path = Path(str(input_packet["payload"]["path"]))
    records = list_records(path)
    output_packet = {
        "packet_type": "registry.response.v1",
        "packet_version": "registry.response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"path": str(path), "records": records, "count": len(records)},
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
            "receipt_id": "json-registry-loaded",
            "brick_id": CONCEPT["id"],
            "kind": "file_read",
            "label": "Loaded JSON registry records.",
            "refs": output_packet["refs"],
            "data": {"count": output_packet["payload"]["count"]},
        }
    ]
