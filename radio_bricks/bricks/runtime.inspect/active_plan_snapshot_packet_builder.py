from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.active_plan_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧠",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.active_plan_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "plan", "snapshot", "context", "next-item"],
    "description": "Package an active-plan snapshot with context guard, ordered items, next-item focus, and scope bindings.",
}


def build_active_plan_snapshot_packet(
    plan_id: str,
    session_id: str,
    title: str,
    active_goal: str,
    want_to_know: list[str] | None,
    context_guard: dict[str, Any] | None,
    handoff: dict[str, Any] | None,
    status: str,
    workspace_id: str | None,
    build_project_id: str | None,
    created_at: str,
    updated_at: str,
    plan_status: str,
    items: list[dict[str, Any]] | None,
    next_item: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "id": str(plan_id),
        "session_id": str(session_id),
        "title": str(title),
        "active_goal": str(active_goal),
        "want_to_know": [str(item) for item in (want_to_know or [])],
        "context_guard": dict(context_guard or {}),
        "handoff": dict(handoff or {}) if handoff else None,
        "status": str(status),
        "workspace_id": workspace_id,
        "build_project_id": build_project_id,
        "created_at": str(created_at),
        "updated_at": str(updated_at),
        "plan_status": str(plan_status),
        "items": [dict(item) for item in (items or [])],
        "next_item": dict(next_item or {}) if next_item else None,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_active_plan_snapshot_packet(
        plan_id=str(payload.get("id") or ""),
        session_id=str(payload.get("session_id") or ""),
        title=str(payload.get("title") or ""),
        active_goal=str(payload.get("active_goal") or ""),
        want_to_know=list(payload.get("want_to_know") or []),
        context_guard=dict(payload.get("context_guard") or {}),
        handoff=dict(payload.get("handoff") or {}) if payload.get("handoff") else None,
        status=str(payload.get("status") or ""),
        workspace_id=payload.get("workspace_id"),
        build_project_id=payload.get("build_project_id"),
        created_at=str(payload.get("created_at") or ""),
        updated_at=str(payload.get("updated_at") or ""),
        plan_status=str(payload.get("plan_status") or ""),
        items=list(payload.get("items") or []),
        next_item=dict(payload.get("next_item") or {}) if payload.get("next_item") else None,
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "active-plan-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built active-plan snapshot packet.",
        "refs": [],
        "data": {
            "plan_status": value.get("plan_status", ""),
            "item_count": len(value.get("items") or []),
            "has_next_item": bool(value.get("next_item")),
        },
    }]
