from __future__ import annotations

from typing import Any


ALLOWED_FIELDS = {
    "max_input_tokens",
    "max_output_tokens",
    "max_cost_usd",
    "max_duration_seconds",
}


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.delegation_budget_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "💸",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.delegation_budget_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "delegation", "budget", "normalization", "limits"],
    "description": "Normalize a delegation budget by keeping only supported positive limit fields.",
}


def build_delegation_budget_packet(raw_budget: dict[str, Any] | None) -> dict[str, Any]:
    budget = dict(raw_budget or {})
    normalized: dict[str, Any] = {}
    for key, value in budget.items():
        if key not in ALLOWED_FIELDS or value in (None, ""):
            continue
        if key in {"max_input_tokens", "max_output_tokens", "max_duration_seconds"} and isinstance(value, int) and value > 0:
            normalized[key] = value
        elif key == "max_cost_usd" and isinstance(value, (int, float)) and float(value) > 0:
            normalized[key] = float(value)
    return {
        "budget": normalized,
        "field_count": len(normalized),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_delegation_budget_packet(
        raw_budget=dict(payload.get("budget") or payload.get("raw_budget") or {}),
    )
    output_packet = {
        "packet_type": "math.interpretation_response.v1",
        "packet_version": "math.interpretation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "delegation-budget-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built delegation budget packet.",
        "refs": [],
        "data": {
            "field_count": value.get("field_count", 0),
        },
    }]
