from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.utc_clock",
    "kind": "world_operator",
    "version": "0.1.0",
    "deterministic": False,
    "inputs": ["runtime.clock_request.v1"],
    "outputs": ["runtime.clock_response.v1"],
    "requires": [],
    "provides": ["runtime.utc_now", "runtime.iso_now"],
    "side_effects": ["clock_read"],
    "ui_slots": [],
    "tags": ["time", "clock", "utc"],
    "description": "Return the current UTC time in datetime and ISO forms.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    packet_type = str(input_packet.get("packet_type") or "")
    if packet_type and packet_type != "runtime.clock_request.v1":
        return [{"code": "packet_type_mismatch", "message": "Expected runtime.clock_request.v1."}]
    return []


def utc_now() -> datetime:
    return datetime.now(UTC)


def iso_now() -> str:
    return utc_now().isoformat()


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    now = utc_now()
    output_packet = {
        "packet_type": "runtime.clock_response.v1",
        "packet_version": "runtime.clock_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {
            "utc_datetime": now,
            "iso_utc": now.isoformat(),
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
            "receipt_id": "utc-clock-read",
            "brick_id": CONCEPT["id"],
            "kind": "clock_read",
            "label": "Read current UTC time.",
            "refs": [],
            "data": {"iso_utc": output_packet["payload"]["iso_utc"]},
        }
    ]
