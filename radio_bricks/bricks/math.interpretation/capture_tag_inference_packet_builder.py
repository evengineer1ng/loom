from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.capture_tag_inference_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏷️",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.capture_tag_inference_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "capture", "tags", "inference"],
    "description": "Package inferred capture tags from project slugging and ranked content words for lightweight inbox routing.",
}


def build_capture_tag_inference_packet(project_slug: str, tags: list[str] | None) -> dict[str, Any]:
    return {
        "project_slug": str(project_slug),
        "tags": [str(item) for item in (tags or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_capture_tag_inference_packet(
        project_slug=str(payload.get("project_slug") or ""),
        tags=list(payload.get("tags") or []),
    )
    output_packet = {
        "packet_type": "math.interpretation_response.v1",
        "packet_version": "math.interpretation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "capture-tag-inference-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built capture tag-inference packet.",
        "refs": [],
        "data": {
            "project_slug": value.get("project_slug", ""),
            "tag_count": len(value.get("tags", [])),
        },
    }]
