from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.project_delivery_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📦",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.project_delivery_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "workspace", "delivery", "artifact", "device"],
    "description": "Package a project delivery record with artifact identity, delivery state, device scope, and acknowledgement links.",
}


def build_project_delivery_packet(
    delivery_id: str,
    workspace_id: str,
    build_project_id: str | None,
    session_id: str | None,
    capture_id: str | None,
    target_device_id: str | None,
    artifact_kind: str,
    file_name: str,
    mime_type: str,
    size_bytes: int,
    status: str,
    metadata: dict[str, Any] | None,
    created_at: str,
    updated_at: str,
    downloaded_at: str | None,
    installed_at: str | None,
    download_url: str,
    ack_url: str,
) -> dict[str, Any]:
    return {
        "id": str(delivery_id),
        "workspace_id": str(workspace_id),
        "build_project_id": build_project_id,
        "session_id": session_id,
        "capture_id": capture_id,
        "target_device_id": target_device_id,
        "artifact_kind": str(artifact_kind),
        "file_name": str(file_name),
        "mime_type": str(mime_type),
        "size_bytes": int(size_bytes),
        "status": str(status),
        "metadata": dict(metadata or {}),
        "created_at": str(created_at),
        "updated_at": str(updated_at),
        "downloaded_at": downloaded_at,
        "installed_at": installed_at,
        "download_url": str(download_url),
        "ack_url": str(ack_url),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_project_delivery_packet(
        delivery_id=str(payload.get("id") or ""),
        workspace_id=str(payload.get("workspace_id") or ""),
        build_project_id=payload.get("build_project_id"),
        session_id=payload.get("session_id"),
        capture_id=payload.get("capture_id"),
        target_device_id=payload.get("target_device_id"),
        artifact_kind=str(payload.get("artifact_kind") or ""),
        file_name=str(payload.get("file_name") or ""),
        mime_type=str(payload.get("mime_type") or ""),
        size_bytes=int(payload.get("size_bytes") or 0),
        status=str(payload.get("status") or ""),
        metadata=dict(payload.get("metadata") or {}),
        created_at=str(payload.get("created_at") or ""),
        updated_at=str(payload.get("updated_at") or ""),
        downloaded_at=payload.get("downloaded_at"),
        installed_at=payload.get("installed_at"),
        download_url=str(payload.get("download_url") or ""),
        ack_url=str(payload.get("ack_url") or ""),
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
        "receipt_id": "project-delivery-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built project delivery packet.",
        "refs": [],
        "data": {
            "artifact_kind": value.get("artifact_kind", ""),
            "status": value.get("status", ""),
            "target_device_id": value.get("target_device_id"),
        },
    }]
