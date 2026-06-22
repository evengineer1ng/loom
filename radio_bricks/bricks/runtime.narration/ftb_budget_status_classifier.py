from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.ftb_budget_status_classifier",
    "kind": "evaluator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.ftb_budget_status"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "ftb", "budget", "classifier"],
    "description": "Classify team budget state for narrator use from cash and budget limit.",
}


def classify_budget_status(cash: float, budget_limit: float) -> str:
    if float(cash) < 0:
        return "critical"
    ratio = float(cash) / max(float(budget_limit), 1.0)
    if ratio < 0.2:
        return "strained"
    return "healthy"


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {"budget_status": classify_budget_status(float(payload.get("cash") or 0.0), float(payload.get("budget_limit") or 0.0))}
    output_packet = {
        "packet_type": "runtime.narration_response.v1",
        "packet_version": "runtime.narration_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "ftb-budget-status",
        "brick_id": CONCEPT["id"],
        "kind": "evaluate",
        "label": "Classified FTB budget status.",
        "refs": [],
        "data": {"budget_status": value.get("budget_status", "unknown")},
    }]
