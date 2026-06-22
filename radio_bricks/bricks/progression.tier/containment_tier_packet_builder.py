from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "progression.tier.containment_tier_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📶",
    "deterministic": True,
    "inputs": ["progression.tier_request.v1"],
    "outputs": ["progression.tier_response.v1"],
    "requires": [],
    "provides": ["progression.containment_tier_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["progression", "tier", "containment", "classifier", "ratchet"],
    "description": "Package containment-tier state with current tier, triggers, and ratchet-style escalation context.",
}


def build_containment_tier_packet(
    current_tier: str,
    base_tier: str,
    anomaly_exposure: float,
    competitive_focus: float,
    research_investment: float,
    escalated: bool,
) -> dict[str, Any]:
    return {
        "current_tier": current_tier,
        "base_tier": base_tier,
        "anomaly_exposure": float(anomaly_exposure),
        "competitive_focus": float(competitive_focus),
        "research_investment": float(research_investment),
        "escalated": bool(escalated),
        "is_ratchet": True,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_containment_tier_packet(
        current_tier=str(payload.get("current_tier") or ""),
        base_tier=str(payload.get("base_tier") or ""),
        anomaly_exposure=float(payload.get("anomaly_exposure") or 0.0),
        competitive_focus=float(payload.get("competitive_focus") or 0.0),
        research_investment=float(payload.get("research_investment") or 0.0),
        escalated=bool(payload.get("escalated", False)),
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
        "receipt_id": "containment-tier-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built containment-tier packet.",
        "refs": [],
        "data": {"current_tier": value.get("current_tier", ""), "escalated": value.get("escalated", False)},
    }]
