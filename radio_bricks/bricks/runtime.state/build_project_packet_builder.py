from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.build_project_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏗️",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.build_project_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "workspace", "project", "build"],
    "description": "Package a build-project record with workspace ownership, status, and lifecycle timestamps.",
}


def build_build_project_packet(
    project_id: str,
    workspace_id: str,
    name: str,
    description: str,
    status: str,
    created_at: str,
    updated_at: str,
) -> dict[str, Any]:
    return {
        "id": str(project_id),
        "workspace_id": str(workspace_id),
        "name": str(name),
        "description": str(description),
        "status": str(status),
        "created_at": str(created_at),
        "updated_at": str(updated_at),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_build_project_packet(
        project_id=str(payload.get("id") or ""),
        workspace_id=str(payload.get("workspace_id") or ""),
        name=str(payload.get("name") or ""),
        description=str(payload.get("description") or ""),
        status=str(payload.get("status") or ""),
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
        "receipt_id": "build-project-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built build-project packet.",
        "refs": [],
        "data": {
            "workspace_id": value.get("workspace_id", ""),
            "status": value.get("status", ""),
        },
    }]
