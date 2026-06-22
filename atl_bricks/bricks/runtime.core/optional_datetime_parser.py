from __future__ import annotations

from datetime import datetime
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.optional_datetime_parser",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.value_request.v1"],
    "outputs": ["runtime.value_response.v1"],
    "requires": [],
    "provides": ["runtime.resolve_optional_datetime"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["datetime", "iso8601", "parsing"],
    "description": "Parse an optional ISO-like datetime string and return None on failure.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    if "value" not in input_packet.get("payload", {}):
        return [{"code": "missing_value", "message": "payload.value is required."}]
    return []


def resolve_optional_datetime(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    raw = input_packet["payload"].get("value")
    moment = resolve_optional_datetime(str(raw) if raw is not None else None)
    output_packet = {
        "packet_type": "runtime.value_response.v1",
        "packet_version": "runtime.value_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"value": moment},
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
    moment = output_packet["payload"]["value"]
    return [
        {
            "receipt_id": "optional-datetime-parsed",
            "brick_id": CONCEPT["id"],
            "kind": "parsing",
            "label": "Parsed optional datetime value.",
            "refs": [],
            "data": {"parsed": bool(moment)},
        }
    ]
