from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.capture_promotion_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔁",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.capture_promotion_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "capture", "evidence", "promotion", "provenance"],
    "description": "Package a capture-promotion result that binds the processed capture to its derived evidence record.",
}


def build_capture_promotion_packet(
    capture: dict[str, Any] | None,
    evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    capture_packet = dict(capture or {})
    evidence_packet = dict(evidence or {})
    return {
        "capture": capture_packet,
        "evidence": evidence_packet,
        "workspace_id": str(capture_packet.get("workspace_id") or evidence_packet.get("workspace_id") or ""),
        "capture_id": str(capture_packet.get("id") or ""),
        "evidence_id": str(evidence_packet.get("id") or ""),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_capture_promotion_packet(
        capture=dict(payload.get("capture") or {}),
        evidence=dict(payload.get("evidence") or {}),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "capture-promotion-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built capture-promotion packet.",
        "refs": [],
        "data": {
            "capture_id": value.get("capture_id", ""),
            "evidence_id": value.get("evidence_id", ""),
        },
    }]
