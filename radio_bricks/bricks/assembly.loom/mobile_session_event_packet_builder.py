from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.mobile_session_event_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📡",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.mobile_session_event_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "mobile", "event", "session", "timeline"],
    "description": "Package a mobile-facing session event packet with workspace/project lineage and parsed event data.",
}


def build_mobile_session_event_packet(
    event_id: str,
    session_id: str,
    workspace_id: str,
    build_project_id: str | None,
    run_id: str | None,
    event_type: str,
    data: dict[str, Any] | None,
    created_at: str,
) -> dict[str, Any]:
    return {
        "id": str(event_id),
        "session_id": str(session_id),
        "workspace_id": str(workspace_id),
        "build_project_id": build_project_id,
        "run_id": run_id,
        "type": str(event_type),
        "data": dict(data or {}),
        "created_at": str(created_at),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_mobile_session_event_packet(
        event_id=str(payload.get("id") or ""),
        session_id=str(payload.get("session_id") or ""),
        workspace_id=str(payload.get("workspace_id") or ""),
        build_project_id=payload.get("build_project_id"),
        run_id=payload.get("run_id"),
        event_type=str(payload.get("type") or payload.get("event_type") or ""),
        data=dict(payload.get("data") or {}),
        created_at=str(payload.get("created_at") or ""),
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
        "receipt_id": "mobile-session-event-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built mobile session-event packet.",
        "refs": [],
        "data": {
            "workspace_id": value.get("workspace_id", ""),
            "type": value.get("type", ""),
            "has_data": bool(value.get("data")),
        },
    }]
