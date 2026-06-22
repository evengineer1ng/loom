from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.governor_decision_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧭",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.governor_decision_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "governor", "capsule", "terminal"],
    "description": "Package a governor decision with capsule injection intent, terminal reason, message role/content, and any pivot or terminal payload.",
}


def build_governor_decision_packet(
    inject_capsule: bool,
    message_role: str,
    message_kind: str,
    message_content: str,
    terminal_reason: str,
    terminal_error: str,
    terminal_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "inject_capsule": bool(inject_capsule),
        "message_role": str(message_role),
        "message_kind": str(message_kind),
        "message_content": str(message_content),
        "terminal_reason": str(terminal_reason),
        "terminal_error": str(terminal_error),
        "terminal_payload": dict(terminal_payload or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_governor_decision_packet(
        inject_capsule=bool(payload.get("inject_capsule")),
        message_role=str(payload.get("message_role") or ""),
        message_kind=str(payload.get("message_kind") or ""),
        message_content=str(payload.get("message_content") or ""),
        terminal_reason=str(payload.get("terminal_reason") or ""),
        terminal_error=str(payload.get("terminal_error") or ""),
        terminal_payload=dict(payload.get("terminal_payload") or {}),
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
        "receipt_id": "governor-decision-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built governor decision packet.",
        "refs": [],
        "data": {
            "inject_capsule": value.get("inject_capsule", False),
            "terminal_reason": value.get("terminal_reason", ""),
        },
    }]
