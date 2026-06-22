from __future__ import annotations

import re
from pathlib import Path
from typing import Any


FREQTRADE_TIMEFRAMES = {
    "1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M",
}

CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.python_timeframe_literal_reader",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.file_request.v1"],
    "outputs": ["runtime.value_response.v1"],
    "requires": [],
    "provides": ["runtime.read_python_timeframe_literal"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["python", "timeframe", "source"],
    "description": "Read a declared Python timeframe literal and normalize it to a freqtrade token.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    if not input_packet.get("payload", {}).get("path"):
        return [{"code": "missing_path", "message": "payload.path is required."}]
    return []


def normalize_freqtrade_timeframe(raw: Any) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    tokens = re.findall(r"[0-9]+[a-zA-Z]+", text)
    for token in tokens:
        if token in FREQTRADE_TIMEFRAMES:
            return token
    for token in tokens:
        lowered = token[:-1] + token[-1].lower()
        if lowered in FREQTRADE_TIMEFRAMES:
            return lowered
    return ""


def strategy_declared_timeframe(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    match = re.search(r"^\s*timeframe\s*=\s*['\"]([^'\"]+)['\"]", text, re.MULTILINE)
    return normalize_freqtrade_timeframe(match.group(1)) if match else ""


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    path = Path(str(input_packet["payload"]["path"]))
    timeframe = strategy_declared_timeframe(path)
    output_packet = {
        "packet_type": "runtime.value_response.v1",
        "packet_version": "runtime.value_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"path": str(path), "timeframe": timeframe},
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
            "receipt_id": "python-timeframe-literal-read",
            "brick_id": CONCEPT["id"],
            "kind": "source_read",
            "label": "Read Python timeframe literal from source.",
            "refs": output_packet["refs"],
            "data": {"timeframe": output_packet["payload"]["timeframe"]},
        }
    ]
