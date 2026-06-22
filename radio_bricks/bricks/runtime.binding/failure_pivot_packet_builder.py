from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.failure_pivot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔀",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.failure_pivot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "failure", "pivot", "governor"],
    "description": "Package a failure pivot with repeated pattern, attempt count, tool name, and the next pivot hint.",
}


def build_failure_pivot_packet(
    tool_name: str,
    repeated_pattern: str,
    attempt_count: int,
    pivot_hint: str,
) -> dict[str, Any]:
    return {
        "tool_name": str(tool_name),
        "repeated_pattern": str(repeated_pattern),
        "attempt_count": int(attempt_count),
        "pivot_hint": str(pivot_hint),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_failure_pivot_packet(
        tool_name=str(payload.get("tool_name") or ""),
        repeated_pattern=str(payload.get("repeated_pattern") or ""),
        attempt_count=int(payload.get("attempt_count") or 0),
        pivot_hint=str(payload.get("pivot_hint") or ""),
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
        "receipt_id": "failure-pivot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built failure pivot packet.",
        "refs": [],
        "data": {
            "tool_name": value.get("tool_name", ""),
            "attempt_count": value.get("attempt_count", 0),
        },
    }]
