from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.capture_record_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📥",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.capture_record_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "capture", "record", "phoneclaw"],
    "description": "Package a PhoneClaw capture record with raw content, summary, project, tags, status, destination agent, and packet JSON.",
}


def build_capture_record_packet(
    capture_id: str,
    created_at: str,
    source_mode: str,
    raw_content: str,
    cleaned_summary: str,
    project: str,
    tags: list[str] | None,
    status: str,
    destination_agent: str,
    packet_json: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "capture_id": str(capture_id),
        "created_at": str(created_at),
        "source_mode": str(source_mode),
        "raw_content": str(raw_content),
        "cleaned_summary": str(cleaned_summary),
        "project": str(project),
        "tags": [str(item) for item in (tags or [])],
        "status": str(status),
        "destination_agent": str(destination_agent),
        "packet_json": dict(packet_json or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_capture_record_packet(
        capture_id=str(payload.get("capture_id") or ""),
        created_at=str(payload.get("created_at") or ""),
        source_mode=str(payload.get("source_mode") or ""),
        raw_content=str(payload.get("raw_content") or ""),
        cleaned_summary=str(payload.get("cleaned_summary") or ""),
        project=str(payload.get("project") or ""),
        tags=list(payload.get("tags") or []),
        status=str(payload.get("status") or ""),
        destination_agent=str(payload.get("destination_agent") or ""),
        packet_json=dict(payload.get("packet_json") or {}),
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
        "receipt_id": "capture-record-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built capture-record packet.",
        "refs": [],
        "data": {
            "capture_id": value.get("capture_id", ""),
            "status": value.get("status", ""),
            "tag_count": len(value.get("tags", [])),
        },
    }]
