from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.file_record_gatherer",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.file_request.v1"],
    "outputs": ["storage.file_record.v1"],
    "requires": [],
    "provides": ["storage.gather_file_record"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["file", "record", "excerpt"],
    "description": "Build a simple file record with existence and excerpt fields.",
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


def gather_file_record(path: Path, label: str | None = None, max_chars: int = 2200) -> dict[str, Any]:
    return {
        "label": label or path.name,
        "path": str(path),
        "exists": path.exists(),
        "excerpt": read_textish_file(path, max_chars=max_chars) if path.exists() else "",
    }


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    record = gather_file_record(
        Path(str(payload["path"])),
        label=str(payload.get("label") or "") or None,
        max_chars=int(payload.get("max_chars") or 2200),
    )
    output_packet = {
        "packet_type": "storage.file_record.v1",
        "packet_version": "storage.file_record.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": record,
        "refs": [record["path"]],
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
            "receipt_id": "file-record-gathered",
            "brick_id": CONCEPT["id"],
            "kind": "file_read",
            "label": "Gathered file existence and excerpt record.",
            "refs": output_packet["refs"],
            "data": {"exists": output_packet["payload"]["exists"]},
        }
    ]
