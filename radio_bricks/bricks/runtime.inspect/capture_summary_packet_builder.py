from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.capture_summary_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗒️",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.capture_summary_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "capture", "summary", "phoneclaw"],
    "description": "Package a cleaned capture summary with project, status, destination agent, and tags for inbox display surfaces.",
}


def build_capture_summary_packet(
    cleaned_summary: str,
    project: str,
    status: str,
    destination_agent: str,
    tags: list[str] | None,
) -> dict[str, Any]:
    return {
        "cleaned_summary": str(cleaned_summary),
        "project": str(project),
        "status": str(status),
        "destination_agent": str(destination_agent),
        "tags": [str(item) for item in (tags or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_capture_summary_packet(
        cleaned_summary=str(payload.get("cleaned_summary") or ""),
        project=str(payload.get("project") or ""),
        status=str(payload.get("status") or ""),
        destination_agent=str(payload.get("destination_agent") or ""),
        tags=list(payload.get("tags") or []),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "capture-summary-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built capture-summary packet.",
        "refs": [],
        "data": {
            "project": value.get("project", ""),
            "status": value.get("status", ""),
            "tag_count": len(value.get("tags", [])),
        },
    }]
