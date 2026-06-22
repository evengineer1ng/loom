from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.profile.mountain_weight_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⛰️",
    "deterministic": True,
    "inputs": ["narrative.profile_request.v1"],
    "outputs": ["narrative.profile_response.v1"],
    "requires": [],
    "provides": ["narrative.mountain_weight_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "profile", "mountains", "weight", "tier"],
    "description": "Package tier-adjusted mountain weights for deterministic primary-global mountain sampling.",
}


def build_mountain_weight_packet(
    base_tier: str,
    instability_mountains: list[str] | None,
    containment_mountains: list[str] | None,
    weighted_codes: dict[str, float] | None,
) -> dict[str, Any]:
    return {
        "base_tier": base_tier,
        "instability_mountains": list(instability_mountains or []),
        "containment_mountains": list(containment_mountains or []),
        "weighted_codes": {str(key): float(value) for key, value in (weighted_codes or {}).items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_mountain_weight_packet(
        base_tier=str(payload.get("base_tier") or ""),
        instability_mountains=list(payload.get("instability_mountains") or []),
        containment_mountains=list(payload.get("containment_mountains") or []),
        weighted_codes=dict(payload.get("weighted_codes") or {}),
    )
    output_packet = {
        "packet_type": "narrative.profile_response.v1",
        "packet_version": "narrative.profile_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "mountain-weight-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built mountain-weight packet.",
        "refs": [],
        "data": {"base_tier": value.get("base_tier", ""), "weighted_code_count": len(value.get("weighted_codes", {}))},
    }]
