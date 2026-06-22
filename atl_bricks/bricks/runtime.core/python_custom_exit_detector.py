from __future__ import annotations

import re
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.python_custom_exit_detector",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.file_request.v1"],
    "outputs": ["runtime.value_response.v1"],
    "requires": [],
    "provides": ["runtime.detect_python_custom_exit"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["python", "freqtrade", "custom_exit"],
    "description": "Detect whether a Python strategy source declares a custom_exit method.",
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


def strategy_has_custom_exit(path: Path) -> bool:
    text = read_python_source_text(path)
    return bool(re.search(r"^\s*def\s+custom_exit\s*\(", text, re.MULTILINE))


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    path = Path(str(input_packet["payload"]["path"]))
    has_custom_exit = strategy_has_custom_exit(path)
    output_packet = {
        "packet_type": "runtime.value_response.v1",
        "packet_version": "runtime.value_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"path": str(path), "has_custom_exit": has_custom_exit},
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
            "receipt_id": "python-custom-exit-detected",
            "brick_id": CONCEPT["id"],
            "kind": "source_read",
            "label": "Checked source for custom_exit method.",
            "refs": output_packet["refs"],
            "data": {"has_custom_exit": output_packet["payload"]["has_custom_exit"]},
        }
    ]
