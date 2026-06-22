from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.approval_training_banner_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚦",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.approval_training_banner_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "approval", "training", "banner"],
    "description": "Package approval-training operator banner notices with title, detail, and tone so human feedback state becomes portable.",
}


def build_approval_training_banner_packet(title: str, detail: str, tone: str) -> dict[str, Any]:
    return {
        "title": str(title),
        "detail": str(detail),
        "tone": str(tone),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_approval_training_banner_packet(
        title=str(payload.get("title") or ""),
        detail=str(payload.get("detail") or ""),
        tone=str(payload.get("tone") or ""),
    )
    output_packet = {
        "packet_type": "runtime.trace_response.v1",
        "packet_version": "runtime.trace_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "approval-training-banner-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built approval-training banner packet.",
        "refs": [],
        "data": {
            "title": value.get("title", ""),
            "tone": value.get("tone", ""),
        },
    }]
