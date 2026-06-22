from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.transient_rule_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪟",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.transient_rule_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "transient", "rule", "surface", "priority"],
    "description": "Package a transient surface rule with title, priority threshold, and body-template contract.",
}


def build_transient_rule_packet(
    name: str,
    title: str,
    min_priority: float,
    body_template: str,
) -> dict[str, Any]:
    return {
        "name": str(name),
        "title": str(title),
        "min_priority": float(min_priority),
        "body_template": str(body_template),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_transient_rule_packet(
        name=str(payload.get("name") or ""),
        title=str(payload.get("title") or ""),
        min_priority=float(payload.get("min_priority") or 0.0),
        body_template=str(payload.get("body_template") or ""),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "transient-rule-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built transient rule packet.",
        "refs": [],
        "data": {
            "name": value.get("name", ""),
            "min_priority": value.get("min_priority", 0.0),
        },
    }]
