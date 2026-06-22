from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "progression.tier.tier_status_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📶",
    "deterministic": True,
    "inputs": ["progression.tier_request.v1"],
    "outputs": ["progression.tier_response.v1"],
    "requires": [],
    "provides": ["progression.tier_status_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["progression", "tier", "status", "containment", "read-model"],
    "description": "Package the current and base containment tier with numeric value, descriptive text, and tick timestamp.",
}


def build_tier_status_packet(
    base_tier: str,
    current_tier: str,
    tier_value: int,
    description: str,
    tick: int,
) -> dict[str, Any]:
    return {
        "base_tier": base_tier,
        "current_tier": current_tier,
        "tier_value": int(tier_value),
        "description": description,
        "tick": int(tick),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_tier_status_packet(
        base_tier=str(payload.get("base_tier") or ""),
        current_tier=str(payload.get("current_tier") or ""),
        tier_value=int(payload.get("tier_value") or 0),
        description=str(payload.get("description") or ""),
        tick=int(payload.get("tick") or 0),
    )
    output_packet = {
        "packet_type": "progression.tier_response.v1",
        "packet_version": "progression.tier_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "tier-status-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built tier-status packet.",
        "refs": [],
        "data": {"current_tier": value.get("current_tier", ""), "tier_value": value.get("tier_value", 0)},
    }]
