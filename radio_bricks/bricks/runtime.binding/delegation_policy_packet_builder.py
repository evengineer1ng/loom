from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.delegation_policy_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪪",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.delegation_policy_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "delegation", "policy", "routes", "budget"],
    "description": "Package a delegation policy with mode, concurrency ceiling, default budget, and per-task routing rules.",
}


def build_delegation_policy_packet(
    mode: str,
    max_live_tasks: int,
    default_budget: dict[str, Any] | None,
    task_routes: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "mode": str(mode),
        "max_live_tasks": int(max_live_tasks),
        "default_budget": dict(default_budget or {}),
        "task_routes": dict(task_routes or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_delegation_policy_packet(
        mode=str(payload.get("mode") or ""),
        max_live_tasks=int(payload.get("max_live_tasks") or 0),
        default_budget=dict(payload.get("default_budget") or {}),
        task_routes=dict(payload.get("task_routes") or {}),
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
        "receipt_id": "delegation-policy-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built delegation policy packet.",
        "refs": [],
        "data": {
            "mode": value.get("mode", ""),
            "max_live_tasks": value.get("max_live_tasks", 0),
            "route_count": len(value.get("task_routes") or {}),
        },
    }]
