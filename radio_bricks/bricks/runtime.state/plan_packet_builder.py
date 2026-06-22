from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.plan_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗺️",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.plan_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "plan", "workspace", "goal", "scope"],
    "description": "Package a plan record with session ownership, goal fields, workspace scope, activation state, and timestamps.",
}


def build_plan_packet(
    plan_id: str,
    session_id: str,
    title: str,
    active_goal: str,
    want_to_know: list[str] | None,
    handoff: dict[str, Any] | None,
    plan_status: str,
    workspace_id: str | None,
    build_project_id: str | None,
    is_active: bool,
    created_at: str,
    updated_at: str,
) -> dict[str, Any]:
    return {
        "id": str(plan_id),
        "session_id": str(session_id),
        "title": str(title),
        "active_goal": str(active_goal),
        "want_to_know": [str(item) for item in (want_to_know or [])],
        "handoff": dict(handoff or {}) if handoff else None,
        "plan_status": str(plan_status),
        "workspace_id": workspace_id,
        "build_project_id": build_project_id,
        "is_active": bool(is_active),
        "created_at": str(created_at),
        "updated_at": str(updated_at),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_plan_packet(
        plan_id=str(payload.get("id") or ""),
        session_id=str(payload.get("session_id") or ""),
        title=str(payload.get("title") or ""),
        active_goal=str(payload.get("active_goal") or ""),
        want_to_know=list(payload.get("want_to_know") or []),
        handoff=dict(payload.get("handoff") or {}) if payload.get("handoff") else None,
        plan_status=str(payload.get("plan_status") or payload.get("status") or ""),
        workspace_id=payload.get("workspace_id"),
        build_project_id=payload.get("build_project_id"),
        is_active=bool(payload.get("is_active")),
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
        "receipt_id": "plan-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built plan packet.",
        "refs": [],
        "data": {
            "plan_status": value.get("plan_status", ""),
            "is_active": value.get("is_active", False),
        },
    }]
