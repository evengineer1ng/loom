from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.workspace_capture_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📸",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.workspace_capture_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "workspace", "capture", "event", "media"],
    "description": "Package a workspace capture record with source, event typing, media linkage, processing state, and timestamps.",
}


def build_workspace_capture_packet(
    capture_id: str,
    workspace_id: str,
    build_project_id: str | None,
    session_id: str | None,
    run_id: str | None,
    source: str,
    event_type: str,
    content: str,
    media_url: str | None,
    metadata: dict[str, Any] | None,
    status: str,
    received_at: str,
    processed_at: str | None,
) -> dict[str, Any]:
    return {
        "id": str(capture_id),
        "workspace_id": str(workspace_id),
        "build_project_id": build_project_id,
        "session_id": session_id,
        "run_id": run_id,
        "source": str(source),
        "event_type": str(event_type),
        "content": str(content),
        "media_url": media_url,
        "metadata": dict(metadata or {}),
        "status": str(status),
        "received_at": str(received_at),
        "processed_at": processed_at,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_workspace_capture_packet(
        capture_id=str(payload.get("id") or ""),
        workspace_id=str(payload.get("workspace_id") or ""),
        build_project_id=payload.get("build_project_id"),
        session_id=payload.get("session_id"),
        run_id=payload.get("run_id"),
        source=str(payload.get("source") or ""),
        event_type=str(payload.get("event_type") or ""),
        content=str(payload.get("content") or ""),
        media_url=payload.get("media_url"),
        metadata=dict(payload.get("metadata") or {}),
        status=str(payload.get("status") or ""),
        received_at=str(payload.get("received_at") or ""),
        processed_at=payload.get("processed_at"),
    )
    output_packet = {
        "packet_type": "runtime.save_response.v1",
        "packet_version": "runtime.save_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "workspace-capture-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built workspace capture packet.",
        "refs": [],
        "data": {
            "source": value.get("source", ""),
            "event_type": value.get("event_type", ""),
            "status": value.get("status", ""),
        },
    }]
