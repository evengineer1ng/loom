from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.delegation_execution_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧵",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.delegation_execution_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "delegation", "execution", "route", "completion"],
    "description": "Package a delegation execution result with completion status, provider route, worker summary, and usage telemetry.",
}


def build_delegation_execution_packet(
    delegation_id: str,
    task_type: str,
    substrate_id: str | None,
    worker_name: str,
    provider_route: dict[str, Any] | None,
    completion_status: str,
    result_summary: str,
    result_payload: dict[str, Any] | None,
    input_tokens: int | None,
    output_tokens: int | None,
    duration_ms: int | None,
) -> dict[str, Any]:
    return {
        "delegation_id": str(delegation_id),
        "task_type": str(task_type),
        "substrate_id": substrate_id,
        "worker_name": str(worker_name),
        "provider_route": dict(provider_route or {}),
        "completion_status": str(completion_status),
        "result_summary": str(result_summary),
        "result_payload": dict(result_payload or {}),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "duration_ms": duration_ms,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_delegation_execution_packet(
        delegation_id=str(payload.get("delegation_id") or payload.get("id") or ""),
        task_type=str(payload.get("task_type") or ""),
        substrate_id=payload.get("substrate_id"),
        worker_name=str(payload.get("worker_name") or ""),
        provider_route=dict(payload.get("provider_route") or {}),
        completion_status=str(payload.get("completion_status") or ""),
        result_summary=str(payload.get("result_summary") or ""),
        result_payload=dict(payload.get("result_payload") or {}),
        input_tokens=payload.get("input_tokens"),
        output_tokens=payload.get("output_tokens"),
        duration_ms=payload.get("duration_ms"),
    )
    output_packet = {
        "packet_type": "runtime.trace_response.v1",
        "packet_version": "runtime.trace_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "delegation-execution-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built delegation execution packet.",
        "refs": [],
        "data": {
            "completion_status": value.get("completion_status", ""),
            "worker_name": value.get("worker_name", ""),
            "duration_ms": value.get("duration_ms"),
        },
    }]
