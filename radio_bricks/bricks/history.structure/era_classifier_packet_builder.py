from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.structure.era_classifier_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["history.structure_request.v1"],
    "outputs": ["history.structure_response.v1"],
    "requires": [],
    "provides": ["history.era_classifier_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "structure", "era", "classifier"],
    "description": "Package an era classification and its active modifiers into a portable structural identity packet.",
}


def build_era_classifier_packet(era: str, modifiers: dict[str, float] | None, trigger_conditions: dict[str, float] | None = None) -> dict[str, Any]:
    return {
        "era": era,
        "modifiers": dict(modifiers or {}),
        "trigger_conditions": dict(trigger_conditions or {}),
        "modifier_count": len(dict(modifiers or {})),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_era_classifier_packet(
        era=str(payload.get("era") or "STABLE"),
        modifiers=dict(payload.get("modifiers") or {}),
        trigger_conditions=dict(payload.get("trigger_conditions") or {}),
    )
    output_packet = {
        "packet_type": "history.structure_response.v1",
        "packet_version": "history.structure_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "era-classifier-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built era classifier packet.",
        "refs": [],
        "data": {"era": value.get("era", "STABLE"), "modifier_count": value.get("modifier_count", 0)},
    }]
