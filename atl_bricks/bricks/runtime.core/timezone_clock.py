from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.timezone_clock",
    "kind": "world_operator",
    "version": "0.1.0",
    "deterministic": False,
    "inputs": ["runtime.clock_request.v1"],
    "outputs": ["runtime.clock_response.v1"],
    "requires": [],
    "provides": ["runtime.local_now", "runtime.iso_local_now"],
    "side_effects": ["clock_read"],
    "ui_slots": [],
    "tags": ["time", "clock", "timezone"],
    "description": "Return the current time in a requested IANA timezone.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    timezone_name = str(input_packet.get("payload", {}).get("timezone") or "")
    if not timezone_name:
        return [{"code": "missing_timezone", "message": "payload.timezone is required."}]
    try:
        ZoneInfo(timezone_name)
    except Exception:
        return [{"code": "invalid_timezone", "message": f"Unknown timezone: {timezone_name}"}]
    return []


def local_now(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


def iso_local_now(timezone_name: str) -> str:
    return local_now(timezone_name).isoformat()


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    timezone_name = str(input_packet["payload"]["timezone"])
    now = local_now(timezone_name)
    output_packet = {
        "packet_type": "runtime.clock_response.v1",
        "packet_version": "runtime.clock_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {
            "timezone": timezone_name,
            "local_datetime": now,
            "iso_local": now.isoformat(),
        },
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
            "receipt_id": "timezone-clock-read",
            "brick_id": CONCEPT["id"],
            "kind": "clock_read",
            "label": "Read current local time.",
            "refs": [],
            "data": {
                "timezone": output_packet["payload"]["timezone"],
                "iso_local": output_packet["payload"]["iso_local"],
            },
        }
    ]
