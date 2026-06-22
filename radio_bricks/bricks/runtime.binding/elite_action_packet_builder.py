from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.elite_action_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚀",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.elite_action_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "elite", "action", "catalog"],
    "description": "Package an Elite action with label, hint, group, tone, and ordered action-step packets.",
}


def build_elite_action_packet(
    action_id: str,
    label: str,
    hint: str,
    group_id: str,
    tone: str,
    steps: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "action_id": str(action_id),
        "label": str(label),
        "hint": str(hint),
        "group_id": str(group_id),
        "tone": str(tone),
        "steps": [dict(item) for item in (steps or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_elite_action_packet(
        action_id=str(payload.get("action_id") or ""),
        label=str(payload.get("label") or ""),
        hint=str(payload.get("hint") or ""),
        group_id=str(payload.get("group_id") or ""),
        tone=str(payload.get("tone") or ""),
        steps=list(payload.get("steps") or []),
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
        "receipt_id": "elite-action-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Elite action packet.",
        "refs": [],
        "data": {
            "action_id": value.get("action_id", ""),
            "group_id": value.get("group_id", ""),
            "step_count": len(value.get("steps", [])),
        },
    }]
