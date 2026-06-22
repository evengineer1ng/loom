from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.segment_queue_record_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧾",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.segment_queue_record_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "segment", "queue", "persistence"],
    "description": "Package an enqueued segment record with queue status, source metadata, reaction framing, and serialized key-point payload.",
}


def build_segment_queue_record_packet(
    segment_id: str,
    created_ts: int,
    priority: float,
    status: str,
    post_id: str,
    source: str,
    event_type: str,
    title: str,
    body: str,
    angle: str,
    why: str,
    key_points: list[str] | None,
    host_hint: str,
) -> dict[str, Any]:
    return {
        "segment_id": str(segment_id),
        "created_ts": int(created_ts),
        "priority": float(priority),
        "status": str(status),
        "post_id": str(post_id),
        "source": str(source),
        "event_type": str(event_type),
        "title": str(title),
        "body": str(body),
        "angle": str(angle),
        "why": str(why),
        "key_points": [str(item) for item in (key_points or [])],
        "host_hint": str(host_hint),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_segment_queue_record_packet(
        segment_id=str(payload.get("segment_id") or ""),
        created_ts=int(payload.get("created_ts") or 0),
        priority=float(payload.get("priority") or 0.0),
        status=str(payload.get("status") or ""),
        post_id=str(payload.get("post_id") or ""),
        source=str(payload.get("source") or ""),
        event_type=str(payload.get("event_type") or ""),
        title=str(payload.get("title") or ""),
        body=str(payload.get("body") or ""),
        angle=str(payload.get("angle") or ""),
        why=str(payload.get("why") or ""),
        key_points=list(payload.get("key_points") or []),
        host_hint=str(payload.get("host_hint") or ""),
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
        "receipt_id": "segment-queue-record-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built segment queue-record packet.",
        "refs": [],
        "data": {
            "segment_id": value.get("segment_id", ""),
            "status": value.get("status", ""),
            "source": value.get("source", ""),
        },
    }]
