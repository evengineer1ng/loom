from __future__ import annotations

import math
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.numeric_parser",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.value_request.v1"],
    "outputs": ["runtime.value_response.v1"],
    "requires": [],
    "provides": ["runtime.parse_float", "runtime.parse_intish", "runtime.first_present_value"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["number", "parsing", "coercion"],
    "description": "Coerce loosely-typed values into stable float and int-ish forms.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    operation = str(input_packet.get("payload", {}).get("operation") or "")
    if operation not in {"parse_float", "parse_intish", "first_present_value"}:
        return [{"code": "unknown_operation", "message": "Supported operations: parse_float, parse_intish, first_present_value."}]
    return []


def extract_first_integer(value: str) -> int | None:
    digits = ""
    for char in value:
        if char.isdigit():
            digits += char
        elif digits:
            return int(digits)
    if digits:
        return int(digits)
    return None


def parse_float(value: Any) -> float:
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def parse_intish(value: Any) -> int:
    if value is None:
        return 0
    try:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return 0
            if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
                return int(value)
            embedded = extract_first_integer(value)
            return embedded or 0
        return int(value)
    except (TypeError, ValueError):
        return 0


def first_present_value(*values: Any) -> Any:
    for value in values:
        if value is not None and value != "":
            return value
    return None


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    operation = payload["operation"]
    if operation == "parse_float":
        value = parse_float(payload.get("value"))
    elif operation == "parse_intish":
        value = parse_intish(payload.get("value"))
    else:
        value = first_present_value(*payload.get("values", []))
    output_packet = {
        "packet_type": "runtime.value_response.v1",
        "packet_version": "runtime.value_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"operation": operation, "value": value},
        "refs": [],
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
            "receipt_id": "numeric-parser-result",
            "brick_id": CONCEPT["id"],
            "kind": "coercion",
            "label": "Coerced loosely-typed numeric input.",
            "refs": [],
            "data": {"operation": output_packet["payload"]["operation"]},
        }
    ]
