from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.plan_item_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪜",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.plan_item_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "plan", "item", "timeline", "position"],
    "description": "Package a plan item with status, order, archival posture, and lifecycle timestamps.",
}


def build_plan_item_packet(
    item_id: str,
    plan_id: str,
    content: str,
    status: str,
    position: int,
    archived: bool,
    archived_at: str | None,
    created_at: str,
    updated_at: str,
) -> dict[str, Any]:
    return {
        "id": str(item_id),
        "plan_id": str(plan_id),
        "content": str(content),
        "status": str(status),
        "position": int(position),
        "archived": bool(archived),
        "archived_at": archived_at,
        "created_at": str(created_at),
        "updated_at": str(updated_at),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_plan_item_packet(
        item_id=str(payload.get("id") or ""),
        plan_id=str(payload.get("plan_id") or ""),
        content=str(payload.get("content") or ""),
        status=str(payload.get("status") or ""),
        position=int(payload.get("position") or 0),
        archived=bool(payload.get("archived")),
        archived_at=payload.get("archived_at"),
        created_at=str(payload.get("created_at") or ""),
        updated_at=str(payload.get("updated_at") or ""),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "plan-item-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built plan item packet.",
        "refs": [],
        "data": {
            "status": value.get("status", ""),
            "position": value.get("position", 0),
            "archived": value.get("archived", False),
        },
    }]
