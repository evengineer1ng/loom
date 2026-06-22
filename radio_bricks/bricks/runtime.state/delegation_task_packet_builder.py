from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.delegation_task_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📬",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.delegation_task_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "delegation", "task", "queue", "worker"],
    "description": "Package a delegation task record with routing, budgets, results, token counts, and lifecycle timestamps.",
}


def build_delegation_task_packet(
    task_id: str,
    session_id: str,
    workspace_id: str | None,
    task_type: str,
    substrate_id: str | None,
    authority_mode: str | None,
    title: str,
    instruction: str,
    status: str,
    requested_provider: str | None,
    requested_model: str | None,
    budget: dict[str, Any] | None,
    provider_route: dict[str, Any] | None,
    worker_name: str | None,
    result_text: str | None,
    result_summary: str | None,
    result_payload: dict[str, Any] | None,
    input_tokens: int | None,
    output_tokens: int | None,
    duration_ms: int | None,
    error: str | None,
    metadata: dict[str, Any] | None,
    created_at: str,
    started_at: str | None,
    completed_at: str | None,
    updated_at: str,
) -> dict[str, Any]:
    return {
        "id": str(task_id),
        "session_id": str(session_id),
        "workspace_id": workspace_id,
        "task_type": str(task_type),
        "substrate_id": substrate_id,
        "authority_mode": authority_mode,
        "title": str(title),
        "instruction": str(instruction),
        "status": str(status),
        "requested_provider": requested_provider,
        "requested_model": requested_model,
        "budget": dict(budget or {}),
        "provider_route": dict(provider_route or {}) if provider_route else None,
        "worker_name": worker_name,
        "result_text": result_text,
        "result_summary": result_summary,
        "result_payload": dict(result_payload or {}),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "duration_ms": duration_ms,
        "error": error,
        "metadata": dict(metadata or {}),
        "created_at": str(created_at),
        "started_at": started_at,
        "completed_at": completed_at,
        "updated_at": str(updated_at),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_delegation_task_packet(
        task_id=str(payload.get("id") or ""),
        session_id=str(payload.get("session_id") or ""),
        workspace_id=payload.get("workspace_id"),
        task_type=str(payload.get("task_type") or ""),
        substrate_id=payload.get("substrate_id"),
        authority_mode=payload.get("authority_mode"),
        title=str(payload.get("title") or ""),
        instruction=str(payload.get("instruction") or ""),
        status=str(payload.get("status") or ""),
        requested_provider=payload.get("requested_provider"),
        requested_model=payload.get("requested_model"),
        budget=dict(payload.get("budget") or {}),
        provider_route=dict(payload.get("provider_route") or {}) if payload.get("provider_route") else None,
        worker_name=payload.get("worker_name"),
        result_text=payload.get("result_text"),
        result_summary=payload.get("result_summary"),
        result_payload=dict(payload.get("result_payload") or {}),
        input_tokens=payload.get("input_tokens"),
        output_tokens=payload.get("output_tokens"),
        duration_ms=payload.get("duration_ms"),
        error=payload.get("error"),
        metadata=dict(payload.get("metadata") or {}),
        created_at=str(payload.get("created_at") or ""),
        started_at=payload.get("started_at"),
        completed_at=payload.get("completed_at"),
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
        "receipt_id": "delegation-task-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built delegation task packet.",
        "refs": [],
        "data": {
            "task_type": value.get("task_type", ""),
            "status": value.get("status", ""),
            "substrate_id": value.get("substrate_id"),
        },
    }]
