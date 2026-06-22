from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.prompt_closure_decision_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚪",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.prompt_closure_decision_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "prompt", "closure", "agent-loop"],
    "description": "Package prompt-closure decisions with answered state, reason, blocker message, and the next required action.",
}


def build_prompt_closure_decision_packet(
    answered: bool,
    reason: str,
    blocker_message: str,
    next_required_action: str,
) -> dict[str, Any]:
    return {
        "answered": bool(answered),
        "reason": str(reason),
        "blocker_message": str(blocker_message),
        "next_required_action": str(next_required_action),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_prompt_closure_decision_packet(
        answered=bool(payload.get("answered")),
        reason=str(payload.get("reason") or ""),
        blocker_message=str(payload.get("blocker_message") or ""),
        next_required_action=str(payload.get("next_required_action") or ""),
    )
    output_packet = {
        "packet_type": "runtime.decision_response.v1",
        "packet_version": "runtime.decision_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "prompt-closure-decision-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built prompt-closure decision packet.",
        "refs": [],
        "data": {
            "answered": value.get("answered", False),
            "reason": value.get("reason", ""),
        },
    }]
