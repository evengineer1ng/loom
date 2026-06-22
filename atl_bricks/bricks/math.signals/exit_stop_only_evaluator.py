from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.exit_stop_only_evaluator",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.value_request.v1"],
    "outputs": ["math.value_response.v1"],
    "requires": [],
    "provides": ["math.exit_stop_only"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "exit", "stop"],
    "description": "Represent the stop-only exit evaluator, which never emits a signal itself.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def exit_stop_only(profit: float, minutes: float, is_short: bool) -> str | None:
    return None


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {"exit_reason": exit_stop_only(0.0, 0.0, False)}
    output_packet = {
        "packet_type": "math.value_response.v1",
        "packet_version": "math.value_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": payload,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "exit-stop-only-evaluated",
        "brick_id": CONCEPT["id"],
        "kind": "analytics",
        "label": "Evaluated stop-only exit.",
        "refs": [],
        "data": output_packet["payload"],
    }]
