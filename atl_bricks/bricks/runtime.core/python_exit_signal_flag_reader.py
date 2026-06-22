from __future__ import annotations

import re
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.python_exit_signal_flag_reader",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.file_request.v1"],
    "outputs": ["runtime.value_response.v1"],
    "requires": [],
    "provides": ["runtime.read_python_exit_signal_flag"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["python", "freqtrade", "exit_signal"],
    "description": "Read the use_exit_signal class flag from Python source, returning None if absent.",
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


def strategy_uses_exit_signal(path: Path) -> bool | None:
    text = read_python_source_text(path)
    match = re.search(r"^\s*use_exit_signal\s*=\s*(True|False)\b", text, re.MULTILINE)
    if not match:
        return None
    return match.group(1) == "True"


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    path = Path(str(input_packet["payload"]["path"]))
    value = strategy_uses_exit_signal(path)
    output_packet = {
        "packet_type": "runtime.value_response.v1",
        "packet_version": "runtime.value_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"path": str(path), "use_exit_signal": value},
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
            "receipt_id": "python-exit-signal-flag-read",
            "brick_id": CONCEPT["id"],
            "kind": "source_read",
            "label": "Read use_exit_signal flag from Python source.",
            "refs": output_packet["refs"],
            "data": {"use_exit_signal": output_packet["payload"]["use_exit_signal"]},
        }
    ]
