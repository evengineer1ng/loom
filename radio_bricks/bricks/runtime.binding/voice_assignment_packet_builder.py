from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.voice_assignment_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗣️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.voice_assignment_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "voice", "assignment", "role", "speaker"],
    "description": "Package a Loom voice-assignment map from narrative roles to concrete voices.",
}


def build_voice_assignment_packet(
    provider: str,
    assignments: dict[str, str] | None,
    order: list[str] | tuple[str, ...] | None,
) -> dict[str, Any]:
    return {
        "provider": str(provider),
        "assignments": {str(key): str(value) for key, value in dict(assignments or {}).items()},
        "order": [str(item) for item in (order or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_voice_assignment_packet(
        provider=str(payload.get("provider") or ""),
        assignments=dict(payload.get("assignments") or {}),
        order=list(payload.get("order") or []),
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
        "receipt_id": "voice-assignment-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built voice assignment packet.",
        "refs": [],
        "data": {
            "provider": value.get("provider", ""),
            "assignment_count": len(value.get("assignments", {})),
        },
    }]
