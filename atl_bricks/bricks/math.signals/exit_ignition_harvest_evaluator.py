from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.exit_ignition_harvest_evaluator",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.value_request.v1"],
    "outputs": ["math.value_response.v1"],
    "requires": [],
    "provides": ["math.exit_ignition_harvest"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "exit", "ignition"],
    "description": "Evaluate the ignition harvest exit rule for one profit/minutes observation.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def exit_ignition_harvest(profit: float, minutes: float, is_short: bool) -> str | None:
    if profit > 0.012 and minutes <= 5:
        return "ignition_scalp"
    if profit > 0.025 and minutes > 5:
        return "ignition_runner"
    if minutes >= 20:
        return "ignition_time"
    if minutes >= 8 and abs(profit) < 0.003:
        return "ignition_time"
    return None


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    result = exit_ignition_harvest(float(payload.get("profit") or 0.0), float(payload.get("minutes") or 0.0), bool(payload.get("is_short")))
    output_packet = {
        "packet_type": "math.value_response.v1",
        "packet_version": "math.value_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"exit_reason": result},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "exit-ignition-harvest-evaluated",
        "brick_id": CONCEPT["id"],
        "kind": "analytics",
        "label": "Evaluated ignition harvest exit.",
        "refs": [],
        "data": output_packet["payload"],
    }]
