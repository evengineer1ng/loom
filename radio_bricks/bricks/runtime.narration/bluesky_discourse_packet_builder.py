from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.bluesky_discourse_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🫧",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.bluesky_discourse_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "bluesky", "discourse", "social"],
    "description": "Package Bluesky hashtag discourse synthesis with author framing, engagement context, discussion angle, and key points.",
}


def build_bluesky_discourse_packet(
    post_id: str,
    title: str,
    body: str,
    angle: str,
    key_points: list[str] | None,
) -> dict[str, Any]:
    return {
        "post_id": str(post_id),
        "title": str(title),
        "body": str(body),
        "angle": str(angle),
        "key_points": [str(item) for item in (key_points or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_bluesky_discourse_packet(
        post_id=str(payload.get("post_id") or ""),
        title=str(payload.get("title") or ""),
        body=str(payload.get("body") or ""),
        angle=str(payload.get("angle") or ""),
        key_points=list(payload.get("key_points") or []),
    )
    output_packet = {
        "packet_type": "runtime.narration_response.v1",
        "packet_version": "runtime.narration_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "bluesky-discourse-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Bluesky-discourse packet.",
        "refs": [],
        "data": {
            "post_id": value.get("post_id", ""),
            "key_point_count": len(value.get("key_points", [])),
        },
    }]
