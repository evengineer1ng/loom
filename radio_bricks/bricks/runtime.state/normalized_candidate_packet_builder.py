from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.normalized_candidate_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🩸",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.normalized_candidate_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "candidate", "bus", "event", "normalization"],
    "description": "Package the locked normalized candidate that rides the federation bus between organs and narration surfaces.",
}


def build_normalized_candidate_packet(
    post_id: str,
    source: str,
    title: str,
    body: str,
    priority: float,
    ts: float,
    type_name: str,
    tags: list[str] | tuple[str, ...] | None,
) -> dict[str, Any]:
    return {
        "post_id": str(post_id),
        "source": str(source),
        "title": str(title),
        "body": str(body),
        "priority": float(priority),
        "ts": float(ts),
        "type": str(type_name),
        "tags": [str(item) for item in (tags or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_normalized_candidate_packet(
        post_id=str(payload.get("post_id") or ""),
        source=str(payload.get("source") or ""),
        title=str(payload.get("title") or ""),
        body=str(payload.get("body") or ""),
        priority=float(payload.get("priority") or 0.0),
        ts=float(payload.get("ts") or 0.0),
        type_name=str(payload.get("type") or payload.get("type_name") or "event"),
        tags=list(payload.get("tags") or []),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "normalized-candidate-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built normalized candidate packet.",
        "refs": [],
        "data": {
            "post_id": value.get("post_id", ""),
            "source": value.get("source", ""),
            "priority": value.get("priority", 0.0),
        },
    }]
