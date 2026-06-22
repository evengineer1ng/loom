from __future__ import annotations

from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.python_source_text_reader",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.file_request.v1"],
    "outputs": ["storage.text_payload.v1"],
    "requires": [],
    "provides": ["storage.read_python_source_text"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["python", "source", "text"],
    "description": "Read a Python source file as text, returning an empty string on failure.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    if not input_packet.get("payload", {}).get("path"):
        return [{"code": "missing_path", "message": "payload.path is required."}]
    return []


def read_python_source_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    path = Path(str(input_packet["payload"]["path"]))
    text = read_python_source_text(path)
    output_packet = {
        "packet_type": "storage.text_payload.v1",
        "packet_version": "storage.text_payload.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"path": str(path), "text": text},
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
            "receipt_id": "python-source-text-read",
            "brick_id": CONCEPT["id"],
            "kind": "file_read",
            "label": "Read Python source text.",
            "refs": output_packet["refs"],
            "data": {"chars": len(output_packet["payload"]["text"])},
        }
    ]
