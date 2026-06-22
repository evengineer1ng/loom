from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.workspace_evidence_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧾",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.workspace_evidence_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "workspace", "evidence", "archive", "record"],
    "description": "Package a workspace evidence record with summary, content, tags, provenance, and lifecycle timestamps.",
}


def build_workspace_evidence_packet(
    evidence_id: str,
    workspace_id: str,
    session_id: str | None,
    build_project_id: str | None,
    evidence_type: str,
    title: str,
    summary: str,
    content: str,
    source_kind: str,
    status: str,
    tags: list[str] | None,
    metadata: dict[str, Any] | None,
    created_at: str,
    updated_at: str,
) -> dict[str, Any]:
    return {
        "id": str(evidence_id),
        "workspace_id": str(workspace_id),
        "session_id": session_id,
        "build_project_id": build_project_id,
        "evidence_type": str(evidence_type),
        "title": str(title),
        "summary": str(summary),
        "content": str(content),
        "source_kind": str(source_kind),
        "status": str(status),
        "tags": [str(item) for item in (tags or [])],
        "metadata": dict(metadata or {}),
        "created_at": str(created_at),
        "updated_at": str(updated_at),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_workspace_evidence_packet(
        evidence_id=str(payload.get("id") or ""),
        workspace_id=str(payload.get("workspace_id") or ""),
        session_id=payload.get("session_id"),
        build_project_id=payload.get("build_project_id"),
        evidence_type=str(payload.get("evidence_type") or ""),
        title=str(payload.get("title") or ""),
        summary=str(payload.get("summary") or ""),
        content=str(payload.get("content") or ""),
        source_kind=str(payload.get("source_kind") or ""),
        status=str(payload.get("status") or ""),
        tags=list(payload.get("tags") or []),
        metadata=dict(payload.get("metadata") or {}),
        created_at=str(payload.get("created_at") or ""),
        updated_at=str(payload.get("updated_at") or ""),
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
        "receipt_id": "workspace-evidence-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built workspace evidence packet.",
        "refs": [],
        "data": {
            "evidence_type": value.get("evidence_type", ""),
            "status": value.get("status", ""),
            "tag_count": len(value.get("tags") or []),
        },
    }]
