from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.scheduler_job_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗓️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.scheduler_job_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "scheduler", "job", "manager"],
    "description": "Package a persisted scheduler job with schedule, cooldown, run timestamps, status, and metadata.",
}


def build_scheduler_job_packet(
    job_id: str,
    job_type: str,
    workspace_id: str,
    session_id: str,
    source: str,
    schedule: str,
    last_run_at: str,
    next_run_at: str,
    cooldown_seconds: int,
    status: str,
    metadata: dict[str, Any] | None,
    created_at: str,
    updated_at: str,
) -> dict[str, Any]:
    return {
        "job_id": str(job_id),
        "job_type": str(job_type),
        "workspace_id": str(workspace_id),
        "session_id": str(session_id),
        "source": str(source),
        "schedule": str(schedule),
        "last_run_at": str(last_run_at),
        "next_run_at": str(next_run_at),
        "cooldown_seconds": int(cooldown_seconds),
        "status": str(status),
        "metadata": dict(metadata or {}),
        "created_at": str(created_at),
        "updated_at": str(updated_at),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_scheduler_job_packet(
        job_id=str(payload.get("job_id") or ""),
        job_type=str(payload.get("job_type") or ""),
        workspace_id=str(payload.get("workspace_id") or ""),
        session_id=str(payload.get("session_id") or ""),
        source=str(payload.get("source") or ""),
        schedule=str(payload.get("schedule") or ""),
        last_run_at=str(payload.get("last_run_at") or ""),
        next_run_at=str(payload.get("next_run_at") or ""),
        cooldown_seconds=int(payload.get("cooldown_seconds") or 0),
        status=str(payload.get("status") or ""),
        metadata=dict(payload.get("metadata") or {}),
        created_at=str(payload.get("created_at") or ""),
        updated_at=str(payload.get("updated_at") or ""),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "scheduler-job-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built scheduler job packet.",
        "refs": [],
        "data": {
            "job_type": value.get("job_type", ""),
            "status": value.get("status", ""),
            "cooldown_seconds": value.get("cooldown_seconds", 0),
        },
    }]
