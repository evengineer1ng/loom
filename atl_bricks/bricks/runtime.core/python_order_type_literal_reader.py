from __future__ import annotations

import re
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.python_order_type_literal_reader",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.file_request.v1"],
    "outputs": ["runtime.value_response.v1"],
    "requires": [],
    "provides": ["runtime.read_python_order_type_literal"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["python", "freqtrade", "order_types"],
    "description": "Read an order_types dict literal from Python source and extract a side's quoted order type.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [field for field in ("path", "side") if not payload.get(field)]
    if missing:
        return [{"code": "missing_fields", "message": f"Missing payload fields: {', '.join(missing)}"}]
    return []


def read_python_source_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def strategy_declared_order_type(path: Path, side: str) -> str:
    text = read_python_source_text(path)
    block = re.search(r"order_types\s*=\s*\{(.*?)\}", text, re.DOTALL)
    if not block:
        return ""
    match = re.search(rf"['\"]{re.escape(side)}['\"]\s*:\s*['\"](\w+)['\"]", block.group(1))
    return match.group(1).lower() if match else ""


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    path = Path(str(input_packet["payload"]["path"]))
    side = str(input_packet["payload"]["side"])
    order_type = strategy_declared_order_type(path, side)
    output_packet = {
        "packet_type": "runtime.value_response.v1",
        "packet_version": "runtime.value_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"path": str(path), "side": side, "order_type": order_type},
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
            "receipt_id": "python-order-type-literal-read",
            "brick_id": CONCEPT["id"],
            "kind": "source_read",
            "label": "Read order_types literal from Python source.",
            "refs": output_packet["refs"],
            "data": {"side": output_packet["payload"]["side"], "order_type": output_packet["payload"]["order_type"]},
        }
    ]
