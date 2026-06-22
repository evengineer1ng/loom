from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.mobile_session_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🛰️",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.mobile_session_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "mobile", "session", "run", "timeline"],
    "description": "Package a mobile-facing session read model with run status, token posture, and workspace/project bindings.",
}


def build_mobile_session_packet(
    session_id: str,
    label: str,
    model: str,
    provider: str,
    status: str,
    token_count: int,
    context_window: int,
    workspace_id: str,
    build_project_id: str | None,
    created_at: str,
    updated_at: str,
    current_run: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "id": str(session_id),
        "label": str(label),
        "model": str(model),
        "provider": str(provider),
        "status": str(status),
        "token_count": int(token_count),
        "context_window": int(context_window),
        "workspace_id": str(workspace_id),
        "build_project_id": build_project_id,
        "created_at": str(created_at),
        "updated_at": str(updated_at),
        "current_run": dict(current_run or {}) if current_run else None,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_mobile_session_packet(
        session_id=str(payload.get("id") or ""),
        label=str(payload.get("label") or ""),
        model=str(payload.get("model") or ""),
        provider=str(payload.get("provider") or ""),
        status=str(payload.get("status") or ""),
        token_count=int(payload.get("token_count") or 0),
        context_window=int(payload.get("context_window") or 0),
        workspace_id=str(payload.get("workspace_id") or ""),
        build_project_id=payload.get("build_project_id"),
        created_at=str(payload.get("created_at") or ""),
        updated_at=str(payload.get("updated_at") or ""),
        current_run=dict(payload.get("current_run") or {}) if payload.get("current_run") else None,
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
        "receipt_id": "mobile-session-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built mobile session packet.",
        "refs": [],
        "data": {
            "workspace_id": value.get("workspace_id", ""),
            "status": value.get("status", ""),
            "has_current_run": bool(value.get("current_run")),
        },
    }]
