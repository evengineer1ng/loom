from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.note_capture_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📓",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.note_capture_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "notes", "capture", "annotation"],
    "description": "Package a captured note with title, body, tags, source attribution, and linked segment id.",
}


def build_note_capture_packet(
    title: str,
    body: str,
    tags: list[str] | None,
    source: str,
    seg_id: str,
) -> dict[str, Any]:
    return {
        "title": str(title),
        "body": str(body),
        "tags": [str(item) for item in (tags or [])],
        "source": str(source),
        "seg_id": str(seg_id),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_note_capture_packet(
        title=str(payload.get("title") or ""),
        body=str(payload.get("body") or ""),
        tags=list(payload.get("tags") or []),
        source=str(payload.get("source") or ""),
        seg_id=str(payload.get("seg_id") or ""),
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
        "receipt_id": "note-capture-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built note-capture packet.",
        "refs": [],
        "data": {
            "title": value.get("title", ""),
            "source": value.get("source", ""),
            "tag_count": len(value.get("tags", [])),
        },
    }]
