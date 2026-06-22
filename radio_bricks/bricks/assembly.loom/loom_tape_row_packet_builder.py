from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.loom_tape_row_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎞️",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.loom_tape_row_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "tape", "row", "tags"],
    "description": "Package one Loom tape row built from actor/action/object roles, extra tags, priority, and optional raw payload.",
}


def build_loom_tape_row_packet(tags: list[str] | None, priority: float, raw: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "tags": [str(item) for item in (tags or [])],
        "priority": float(priority),
        "raw": dict(raw or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_loom_tape_row_packet(
        tags=list(payload.get("tags") or []),
        priority=float(payload.get("priority") or 0.0),
        raw=dict(payload.get("raw") or {}),
    )
    output_packet = {
        "packet_type": "assembly.loom_response.v1",
        "packet_version": "assembly.loom_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "loom-tape-row-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Loom tape-row packet.",
        "refs": [],
        "data": {
            "tag_count": len(value.get("tags", [])),
            "priority": value.get("priority", 0.0),
        },
    }]
