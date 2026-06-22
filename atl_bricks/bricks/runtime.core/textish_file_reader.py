from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.textish_file_reader",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.file_request.v1"],
    "outputs": ["storage.text_payload.v1"],
    "requires": [],
    "provides": ["storage.read_textish_file"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["file", "text", "ipynb"],
    "description": "Read text-like files, including notebook cell excerpts, with a character cap.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    if not input_packet.get("payload", {}).get("path"):
        return [{"code": "missing_path", "message": "payload.path is required."}]
    return []


def read_textish_file(path: Path, max_chars: int = 3000) -> str:
    suffix = path.suffix.lower()
    try:
        if suffix == ".ipynb":
            payload = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            parts: list[str] = []
            for cell in payload.get("cells", [])[:8]:
                source = cell.get("source", [])
                if isinstance(source, list):
                    parts.append("".join(source))
                elif isinstance(source, str):
                    parts.append(source)
            return "\n".join(parts)[:max_chars]
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except Exception:
        return ""


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    path = Path(str(payload["path"]))
    max_chars = int(payload.get("max_chars") or 3000)
    text = read_textish_file(path, max_chars=max_chars)
    output_packet = {
        "packet_type": "storage.text_payload.v1",
        "packet_version": "storage.text_payload.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"path": str(path), "text": text, "max_chars": max_chars},
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
            "receipt_id": "textish-file-read",
            "brick_id": CONCEPT["id"],
            "kind": "file_read",
            "label": "Read text-like file excerpt.",
            "refs": output_packet["refs"],
            "data": {"max_chars": output_packet["payload"]["max_chars"]},
        }
    ]
