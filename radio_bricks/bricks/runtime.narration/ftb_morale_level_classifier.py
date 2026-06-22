from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.ftb_morale_level_classifier",
    "kind": "evaluator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.ftb_morale_level"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "ftb", "morale", "classifier"],
    "description": "Classify morale into a narrator-facing state band.",
}


def classify_morale_level(morale: float) -> str:
    if float(morale) < 40:
        return "low"
    if float(morale) > 70:
        return "high"
    return "stable"


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {"morale_level": classify_morale_level(float(payload.get("morale") or 0.0))}
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
        "receipt_id": "ftb-morale-level",
        "brick_id": CONCEPT["id"],
        "kind": "evaluate",
        "label": "Classified FTB morale level.",
        "refs": [],
        "data": {"morale_level": value.get("morale_level", "unknown")},
    }]
