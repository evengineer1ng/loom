from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.approval_feedback_pending_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📝",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.approval_feedback_pending_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "approval", "feedback", "pending"],
    "description": "Package pending approval-feedback state with event id, action, source camera, candidate list, and human-feedback category.",
}


def build_approval_feedback_pending_packet(
    event_id: str,
    action: str,
    source_camera: str,
    top_candidates: list[dict[str, Any]] | None,
    created_at_ms: int,
    awaiting_expected_action: bool,
    feedback_category: str,
) -> dict[str, Any]:
    return {
        "event_id": str(event_id),
        "action": str(action),
        "source_camera": str(source_camera),
        "top_candidates": [dict(item) for item in (top_candidates or [])],
        "created_at_ms": int(created_at_ms),
        "awaiting_expected_action": bool(awaiting_expected_action),
        "feedback_category": str(feedback_category),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_approval_feedback_pending_packet(
        event_id=str(payload.get("event_id") or ""),
        action=str(payload.get("action") or ""),
        source_camera=str(payload.get("source_camera") or ""),
        top_candidates=list(payload.get("top_candidates") or []),
        created_at_ms=int(payload.get("created_at_ms") or 0),
        awaiting_expected_action=bool(payload.get("awaiting_expected_action")),
        feedback_category=str(payload.get("feedback_category") or ""),
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
        "receipt_id": "approval-feedback-pending-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built pending approval-feedback packet.",
        "refs": [],
        "data": {
            "event_id": value.get("event_id", ""),
            "action": value.get("action", ""),
            "candidate_count": len(value.get("top_candidates", [])),
        },
    }]
