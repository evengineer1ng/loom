from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.workspace_pastime_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪁",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.workspace_pastime_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "workspace", "pastime", "scheduler", "candidate"],
    "description": "Package a workspace pastime record with candidate identity, cooldowns, cost, status, and scheduling metadata.",
}


def build_workspace_pastime_packet(
    pastime_id: str,
    workspace_id: str,
    key: str,
    title: str,
    description: str,
    pastime_type: str,
    source_kind: str,
    candidate_type: str | None,
    status: str,
    priority: int,
    cooldown_seconds: int,
    compute_cost: int,
    metadata: dict[str, Any] | None,
    config: dict[str, Any] | None,
    created_at: str,
    updated_at: str,
    last_selected_at: str | None,
    last_completed_at: str | None,
) -> dict[str, Any]:
    return {
        "id": str(pastime_id),
        "workspace_id": str(workspace_id),
        "key": str(key),
        "title": str(title),
        "description": str(description),
        "pastime_type": str(pastime_type),
        "source_kind": str(source_kind),
        "candidate_type": candidate_type,
        "status": str(status),
        "priority": int(priority),
        "cooldown_seconds": int(cooldown_seconds),
        "compute_cost": int(compute_cost),
        "metadata": dict(metadata or {}),
        "config": dict(config or {}),
        "created_at": str(created_at),
        "updated_at": str(updated_at),
        "last_selected_at": last_selected_at,
        "last_completed_at": last_completed_at,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_workspace_pastime_packet(
        pastime_id=str(payload.get("id") or ""),
        workspace_id=str(payload.get("workspace_id") or ""),
        key=str(payload.get("key") or ""),
        title=str(payload.get("title") or ""),
        description=str(payload.get("description") or ""),
        pastime_type=str(payload.get("pastime_type") or ""),
        source_kind=str(payload.get("source_kind") or ""),
        candidate_type=payload.get("candidate_type"),
        status=str(payload.get("status") or ""),
        priority=int(payload.get("priority") or 0),
        cooldown_seconds=int(payload.get("cooldown_seconds") or 0),
        compute_cost=int(payload.get("compute_cost") or 0),
        metadata=dict(payload.get("metadata") or {}),
        config=dict(payload.get("config") or {}),
        created_at=str(payload.get("created_at") or ""),
        updated_at=str(payload.get("updated_at") or ""),
        last_selected_at=payload.get("last_selected_at"),
        last_completed_at=payload.get("last_completed_at"),
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
        "receipt_id": "workspace-pastime-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built workspace pastime packet.",
        "refs": [],
        "data": {
            "key": value.get("key", ""),
            "status": value.get("status", ""),
            "priority": value.get("priority", 0),
        },
    }]
