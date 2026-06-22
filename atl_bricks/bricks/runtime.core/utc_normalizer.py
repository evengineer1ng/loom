from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.utc_normalizer",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.datetime_packet.v1"],
    "outputs": ["runtime.datetime_packet.v1"],
    "requires": [],
    "provides": ["runtime.normalize_utc"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["time", "timezone", "utc"],
    "description": "Normalize naive or timezone-aware datetimes into UTC.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if "moment" not in payload:
        return [{"code": "missing_moment", "message": "payload.moment is required."}]
    return []


def normalize_utc(moment: datetime | None) -> datetime | None:
    if not moment:
        return None
    if moment.tzinfo is None:
        return moment.replace(tzinfo=UTC)
    return moment.astimezone(UTC)


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    normalized = normalize_utc(input_packet["payload"].get("moment"))
    output_packet = {
        "packet_type": "runtime.datetime_packet.v1",
        "packet_version": "runtime.datetime_packet.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"moment": normalized},
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
    moment = output_packet["payload"]["moment"]
    return [
        {
            "receipt_id": "utc-normalized",
            "brick_id": CONCEPT["id"],
            "kind": "normalization",
            "label": "Normalized datetime to UTC.",
            "refs": [],
            "data": {"iso_utc": moment.isoformat() if moment else ""},
        }
    ]
