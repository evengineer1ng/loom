from __future__ import annotations

import re
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.python_dict_literal_value_reader",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.file_request.v1"],
    "outputs": ["runtime.value_response.v1"],
    "requires": [],
    "provides": ["runtime.read_python_dict_literal_value"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["python", "dict", "source"],
    "description": "Read a named dict literal block from Python source and extract a quoted key's quoted value.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [
        field
        for field in ("path", "dict_name", "key_name")
        if not payload.get(field)
    ]
    if missing:
        return [{"code": "missing_fields", "message": f"Missing payload fields: {', '.join(missing)}"}]
    return []


def python_dict_literal_value(path: Path, dict_name: str, key_name: str) -> str:
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    block = re.search(rf"{re.escape(dict_name)}\s*=\s*\{{(.*?)\}}", text, re.DOTALL)
    if not block:
        return ""
    match = re.search(rf"['\"]{re.escape(key_name)}['\"]\s*:\s*['\"](\w+)['\"]", block.group(1))
    return match.group(1).lower() if match else ""


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    value = python_dict_literal_value(
        Path(str(payload["path"])),
        str(payload["dict_name"]),
        str(payload["key_name"]),
    )
    output_packet = {
        "packet_type": "runtime.value_response.v1",
        "packet_version": "runtime.value_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {
            "path": str(payload["path"]),
            "dict_name": str(payload["dict_name"]),
            "key_name": str(payload["key_name"]),
            "value": value,
        },
        "refs": [str(payload["path"])],
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
            "receipt_id": "python-dict-literal-value-read",
            "brick_id": CONCEPT["id"],
            "kind": "source_read",
            "label": "Read dict literal value from Python source.",
            "refs": output_packet["refs"],
            "data": {
                "dict_name": output_packet["payload"]["dict_name"],
                "key_name": output_packet["payload"]["key_name"],
                "value": output_packet["payload"]["value"],
            },
        }
    ]
