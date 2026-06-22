from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.transition_rung_selection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪜",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.transition_rung_selection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "transition", "quality_ladder", "bridge", "rung"],
    "description": "Choose the active transition rung from the Loom quality ladder based on custom clips, carrier viability, and anchor availability.",
}


def build_transition_rung_selection_packet(
    has_custom_clip: bool,
    carrier_available: bool,
    same_family: bool,
    has_anchors: bool,
) -> dict[str, Any]:
    if has_custom_clip:
        rung = "custom"
        reason = "authored custom transition clip is available"
    elif carrier_available:
        rung = "carrier"
        reason = "opencv/numpy carrier path is available"
    elif has_anchors and same_family:
        rung = "morph"
        reason = "signatures share a family and both have anchors"
    elif has_anchors:
        rung = "neutral"
        reason = "anchors exist but family-specific morph is not preferred"
    else:
        rung = "hardcut"
        reason = "no richer transition path is available"
    return {
        "rung": rung,
        "reason": reason,
        "has_custom_clip": bool(has_custom_clip),
        "carrier_available": bool(carrier_available),
        "same_family": bool(same_family),
        "has_anchors": bool(has_anchors),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_transition_rung_selection_packet(
        has_custom_clip=bool(payload.get("has_custom_clip")),
        carrier_available=bool(payload.get("carrier_available")),
        same_family=bool(payload.get("same_family")),
        has_anchors=bool(payload.get("has_anchors")),
    )
    output_packet = {
        "packet_type": "runtime.decision_response.v1",
        "packet_version": "runtime.decision_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "transition-rung-selection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built transition rung-selection packet.",
        "refs": [],
        "data": {
            "rung": value.get("rung", ""),
        },
    }]
