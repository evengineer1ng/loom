from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.capture_packet_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📦",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.capture_packet_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "capture", "packet", "inbox"],
    "description": "Package the PhoneClaw inbox handoff packet with source device, input mode, project, requested action, preferred agent, tags, summary, and raw content.",
}


def build_capture_packet_packet(
    packet_id: str,
    created_at: str,
    source_device: str,
    input_mode: str,
    project: str,
    task_type: str,
    urgency: str,
    local_summary: str,
    raw_input_ref: str,
    tags: list[str] | None,
    requested_action: str,
    preferred_agent: str,
    requires_confirmation: bool,
    raw_content: str,
) -> dict[str, Any]:
    return {
        "packet_id": str(packet_id),
        "created_at": str(created_at),
        "source_device": str(source_device),
        "input_mode": str(input_mode),
        "project": str(project),
        "task_type": str(task_type),
        "urgency": str(urgency),
        "local_summary": str(local_summary),
        "raw_input_ref": str(raw_input_ref),
        "tags": [str(item) for item in (tags or [])],
        "requested_action": str(requested_action),
        "preferred_agent": str(preferred_agent),
        "requires_confirmation": bool(requires_confirmation),
        "raw_content": str(raw_content),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_capture_packet_packet(
        packet_id=str(payload.get("packet_id") or ""),
        created_at=str(payload.get("created_at") or ""),
        source_device=str(payload.get("source_device") or ""),
        input_mode=str(payload.get("input_mode") or ""),
        project=str(payload.get("project") or ""),
        task_type=str(payload.get("task_type") or ""),
        urgency=str(payload.get("urgency") or ""),
        local_summary=str(payload.get("local_summary") or ""),
        raw_input_ref=str(payload.get("raw_input_ref") or ""),
        tags=list(payload.get("tags") or []),
        requested_action=str(payload.get("requested_action") or ""),
        preferred_agent=str(payload.get("preferred_agent") or ""),
        requires_confirmation=bool(payload.get("requires_confirmation")),
        raw_content=str(payload.get("raw_content") or ""),
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
        "receipt_id": "capture-packet-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built capture-packet packet.",
        "refs": [],
        "data": {
            "packet_id": value.get("packet_id", ""),
            "project": value.get("project", ""),
            "preferred_agent": value.get("preferred_agent", ""),
        },
    }]
