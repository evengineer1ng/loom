from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.exit_roi_ladder_evaluator",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.value_request.v1"],
    "outputs": ["math.value_response.v1"],
    "requires": [],
    "provides": ["math.exit_roi_ladder"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "exit", "roi"],
    "description": "Evaluate the ROI ladder exit rule for one profit/minutes observation.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def exit_roi_ladder(profit: float, minutes: float, is_short: bool) -> str | None:
    for floor_min, roi in ((60, 0.01), (30, 0.025), (0, 0.05)):
        if minutes >= floor_min and profit >= roi:
            return "roi"
    return None


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    result = exit_roi_ladder(float(payload.get("profit") or 0.0), float(payload.get("minutes") or 0.0), bool(payload.get("is_short")))
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
        "receipt_id": "exit-roi-ladder-evaluated",
        "brick_id": CONCEPT["id"],
        "kind": "analytics",
        "label": "Evaluated ROI ladder exit.",
        "refs": [],
        "data": output_packet["payload"],
    }]
