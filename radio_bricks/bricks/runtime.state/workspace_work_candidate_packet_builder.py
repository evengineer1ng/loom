from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.workspace_work_candidate_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪵",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.workspace_work_candidate_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "workspace", "candidate", "signal"],
    "description": "Package a workspace runtime work candidate with priority, urgency, mutability, prerequisites, blocking posture, and source metadata.",
}


def build_workspace_work_candidate_packet(
    candidate_id: str,
    candidate_type: str,
    source: str,
    workspace_id: str,
    session_id: str,
    priority: int,
    urgency: int,
    compute_cost: int,
    interruptibility: str,
    cooldown: int,
    expires_at: str,
    prerequisites: list[str] | None,
    mutability_level: str,
    foreground_blocking: bool,
    title: str,
    summary: str,
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "candidate_id": str(candidate_id),
        "candidate_type": str(candidate_type),
        "source": str(source),
        "workspace_id": str(workspace_id),
        "session_id": str(session_id),
        "priority": int(priority),
        "urgency": int(urgency),
        "compute_cost": int(compute_cost),
        "interruptibility": str(interruptibility),
        "cooldown": int(cooldown),
        "expires_at": str(expires_at),
        "prerequisites": [str(item) for item in (prerequisites or [])],
        "mutability_level": str(mutability_level),
        "foreground_blocking": bool(foreground_blocking),
        "title": str(title),
        "summary": str(summary),
        "metadata": dict(metadata or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_workspace_work_candidate_packet(
        candidate_id=str(payload.get("candidate_id") or ""),
        candidate_type=str(payload.get("candidate_type") or ""),
        source=str(payload.get("source") or ""),
        workspace_id=str(payload.get("workspace_id") or ""),
        session_id=str(payload.get("session_id") or ""),
        priority=int(payload.get("priority") or 0),
        urgency=int(payload.get("urgency") or 0),
        compute_cost=int(payload.get("compute_cost") or 0),
        interruptibility=str(payload.get("interruptibility") or ""),
        cooldown=int(payload.get("cooldown") or 0),
        expires_at=str(payload.get("expires_at") or ""),
        prerequisites=list(payload.get("prerequisites") or []),
        mutability_level=str(payload.get("mutability_level") or ""),
        foreground_blocking=bool(payload.get("foreground_blocking")),
        title=str(payload.get("title") or ""),
        summary=str(payload.get("summary") or ""),
        metadata=dict(payload.get("metadata") or {}),
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
        "receipt_id": "workspace-work-candidate-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built workspace work-candidate packet.",
        "refs": [],
        "data": {
            "candidate_type": value.get("candidate_type", ""),
            "priority": value.get("priority", 0),
            "urgency": value.get("urgency", 0),
        },
    }]
