from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.scheduler_eligibility_context_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪪",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.scheduler_eligibility_context_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "scheduler", "eligibility", "context"],
    "description": "Package scheduler eligibility context with idle tier, active runs, job last-run table, attention profile, and pastime type map.",
}


def build_scheduler_eligibility_context_packet(
    idle_tier: int,
    active_run_session_ids: list[str] | None,
    now_iso: str,
    job_last_run: dict[str, str] | None,
    attention_profile: dict[str, Any] | None,
    pastime_types_by_key: dict[str, str] | None,
) -> dict[str, Any]:
    return {
        "idle_tier": int(idle_tier),
        "active_run_session_ids": [str(item) for item in (active_run_session_ids or [])],
        "now_iso": str(now_iso),
        "job_last_run": {str(key): str(value) for key, value in (job_last_run or {}).items()},
        "attention_profile": dict(attention_profile or {}),
        "pastime_types_by_key": {str(key): str(value) for key, value in (pastime_types_by_key or {}).items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_scheduler_eligibility_context_packet(
        idle_tier=int(payload.get("idle_tier") or 0),
        active_run_session_ids=list(payload.get("active_run_session_ids") or []),
        now_iso=str(payload.get("now_iso") or ""),
        job_last_run=dict(payload.get("job_last_run") or {}),
        attention_profile=dict(payload.get("attention_profile") or {}),
        pastime_types_by_key=dict(payload.get("pastime_types_by_key") or {}),
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
        "receipt_id": "scheduler-eligibility-context-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built scheduler eligibility-context packet.",
        "refs": [],
        "data": {
            "idle_tier": value.get("idle_tier", 0),
            "active_run_count": len(value.get("active_run_session_ids", [])),
        },
    }]
