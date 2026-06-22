from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.elite_action_step_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⌨️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.elite_action_step_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "elite", "action", "step"],
    "description": "Package one Elite action step with key tuple, hold duration, and post-step delay.",
}


def build_elite_action_step_packet(keys: list[str] | None, hold_ms: int, after_ms: int) -> dict[str, Any]:
    return {
        "keys": [str(item) for item in (keys or [])],
        "hold_ms": int(hold_ms),
        "after_ms": int(after_ms),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_elite_action_step_packet(
        keys=list(payload.get("keys") or []),
        hold_ms=int(payload.get("hold_ms") or 0),
        after_ms=int(payload.get("after_ms") or 0),
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
        "receipt_id": "elite-action-step-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Elite action-step packet.",
        "refs": [],
        "data": {
            "key_count": len(value.get("keys", [])),
            "hold_ms": value.get("hold_ms", 0),
        },
    }]
