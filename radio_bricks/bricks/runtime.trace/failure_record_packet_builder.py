from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.failure_record_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "💥",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.failure_record_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "failure", "governor", "recovery"],
    "description": "Package a deterministic failure record with tool, category, subgoal, strategy, signature, facts, and command detail.",
}


def build_failure_record_packet(
    call_id: str,
    tool_name: str,
    category: str,
    subgoal: str,
    strategy: str,
    signature: str,
    detail: str,
    command: str,
    facts: list[str] | None,
) -> dict[str, Any]:
    return {
        "call_id": str(call_id),
        "tool_name": str(tool_name),
        "category": str(category),
        "subgoal": str(subgoal),
        "strategy": str(strategy),
        "signature": str(signature),
        "detail": str(detail),
        "command": str(command),
        "facts": [str(item) for item in (facts or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_failure_record_packet(
        call_id=str(payload.get("call_id") or ""),
        tool_name=str(payload.get("tool_name") or ""),
        category=str(payload.get("category") or ""),
        subgoal=str(payload.get("subgoal") or ""),
        strategy=str(payload.get("strategy") or ""),
        signature=str(payload.get("signature") or ""),
        detail=str(payload.get("detail") or ""),
        command=str(payload.get("command") or ""),
        facts=list(payload.get("facts") or []),
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
        "receipt_id": "failure-record-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built failure record packet.",
        "refs": [],
        "data": {
            "tool_name": value.get("tool_name", ""),
            "category": value.get("category", ""),
            "fact_count": len(value.get("facts", [])),
        },
    }]
