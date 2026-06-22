from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.approval_feedback_gate_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚦",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.approval_feedback_gate_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "approval", "feedback", "gate"],
    "description": "Package approval-training gate state with prompt text, blocking flag, pending feedback, pending nudge, and banner notice payload.",
}


def build_approval_feedback_gate_packet(
    prompt: str,
    blocking_feedback: bool,
    pending_feedback_action: str,
    pending_nudge: bool,
    banner_notice: dict[str, str] | None,
) -> dict[str, Any]:
    return {
        "prompt": str(prompt),
        "blocking_feedback": bool(blocking_feedback),
        "pending_feedback_action": str(pending_feedback_action),
        "pending_nudge": bool(pending_nudge),
        "banner_notice": {str(k): str(v) for k, v in dict(banner_notice or {}).items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_approval_feedback_gate_packet(
        prompt=str(payload.get("prompt") or ""),
        blocking_feedback=bool(payload.get("blocking_feedback")),
        pending_feedback_action=str(payload.get("pending_feedback_action") or ""),
        pending_nudge=bool(payload.get("pending_nudge")),
        banner_notice=dict(payload.get("banner_notice") or {}),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "approval-feedback-gate-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built approval-feedback gate packet.",
        "refs": [],
        "data": {
            "blocking_feedback": value.get("blocking_feedback", False),
            "pending_feedback_action": value.get("pending_feedback_action", ""),
            "pending_nudge": value.get("pending_nudge", False),
        },
    }]
