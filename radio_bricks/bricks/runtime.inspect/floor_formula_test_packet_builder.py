from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.floor_formula_test_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧪",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.floor_formula_test_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "floor", "formula", "test"],
    "description": "Package formula test results for live floor editing, including target field, selected label, expression, and evaluation outcome.",
}


def build_floor_formula_test_packet(
    selected_label: str,
    formula_field: str,
    expression: str,
    result: str,
) -> dict[str, Any]:
    return {
        "selected_label": str(selected_label),
        "formula_field": str(formula_field),
        "expression": str(expression),
        "result": str(result),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_floor_formula_test_packet(
        selected_label=str(payload.get("selected_label") or ""),
        formula_field=str(payload.get("formula_field") or ""),
        expression=str(payload.get("expression") or ""),
        result=str(payload.get("result") or ""),
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
        "receipt_id": "floor-formula-test-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built floor-formula test packet.",
        "refs": [],
        "data": {
            "selected_label": value.get("selected_label", ""),
            "formula_field": value.get("formula_field", ""),
            "result": value.get("result", ""),
        },
    }]
