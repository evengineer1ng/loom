from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.mobile_bootstrap_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📱",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.mobile_bootstrap_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "mobile", "bootstrap", "workspace", "delivery"],
    "description": "Package a mobile bootstrap payload with workspace, project, delivery, session, capture, and event collections.",
}


def build_mobile_bootstrap_packet(
    device_id: str,
    workspaces: list[dict[str, Any]] | None,
    projects_by_workspace: dict[str, list[dict[str, Any]]] | None,
    deliveries_by_workspace: dict[str, list[dict[str, Any]]] | None,
    sessions_by_workspace: dict[str, list[dict[str, Any]]] | None,
    recent_captures: list[dict[str, Any]] | None,
    recent_session_events: list[dict[str, Any]] | None,
    generated_at: str,
) -> dict[str, Any]:
    return {
        "device_id": str(device_id),
        "workspaces": [dict(item) for item in (workspaces or [])],
        "projects_by_workspace": {
            str(key): [dict(item) for item in value]
            for key, value in dict(projects_by_workspace or {}).items()
        },
        "deliveries_by_workspace": {
            str(key): [dict(item) for item in value]
            for key, value in dict(deliveries_by_workspace or {}).items()
        },
        "sessions_by_workspace": {
            str(key): [dict(item) for item in value]
            for key, value in dict(sessions_by_workspace or {}).items()
        },
        "recent_captures": [dict(item) for item in (recent_captures or [])],
        "recent_session_events": [dict(item) for item in (recent_session_events or [])],
        "generated_at": str(generated_at),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_mobile_bootstrap_packet(
        device_id=str(payload.get("device_id") or ""),
        workspaces=list(payload.get("workspaces") or []),
        projects_by_workspace=dict(payload.get("projects_by_workspace") or {}),
        deliveries_by_workspace=dict(payload.get("deliveries_by_workspace") or {}),
        sessions_by_workspace=dict(payload.get("sessions_by_workspace") or {}),
        recent_captures=list(payload.get("recent_captures") or []),
        recent_session_events=list(payload.get("recent_session_events") or []),
        generated_at=str(payload.get("generated_at") or ""),
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
        "receipt_id": "mobile-bootstrap-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built mobile bootstrap packet.",
        "refs": [],
        "data": {
            "device_id": value.get("device_id", ""),
            "workspace_count": len(value.get("workspaces") or []),
            "capture_count": len(value.get("recent_captures") or []),
        },
    }]
