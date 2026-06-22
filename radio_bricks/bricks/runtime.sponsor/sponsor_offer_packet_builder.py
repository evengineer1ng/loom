from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sponsor.sponsor_offer_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.sponsor_request.v1"],
    "outputs": ["runtime.sponsor_response.v1"],
    "requires": [],
    "provides": ["runtime.sponsor_offer_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "sponsor", "offer", "packet"],
    "description": "Package a sponsor offer with tier, duration, exclusivity, and infrastructure expectations.",
}


def build_sponsor_offer_packet(offer: dict[str, Any] | None) -> dict[str, Any]:
    value = dict(offer or {})
    return {
        "sponsor_id": str(value.get("sponsor_id") or ""),
        "sponsor_name": str(value.get("sponsor_name") or ""),
        "financial_tier": str(value.get("financial_tier") or value.get("tier") or ""),
        "industry": str(value.get("industry") or ""),
        "sub_industry": str(value.get("sub_industry") or ""),
        "base_payment_per_season": int(value.get("base_payment_per_season") or 0),
        "duration_seasons": int(value.get("duration_seasons") or 0),
        "contract_type": str(value.get("contract_type") or ""),
        "evaluation_cadence": int(value.get("evaluation_cadence") or 0),
        "exclusivity_clauses": list(value.get("exclusivity_clauses") or []),
        "infrastructure_demands": dict(value.get("infrastructure_demands") or {}),
        "facility_tour_events_required": int(value.get("facility_tour_events_required") or 0),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_sponsor_offer_packet(dict(payload.get("offer") or {}))
    output_packet = {
        "packet_type": "runtime.sponsor_response.v1",
        "packet_version": "runtime.sponsor_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "sponsor-offer-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built sponsor offer packet.",
        "refs": [],
        "data": {"has_infrastructure_demands": bool(value.get("infrastructure_demands"))},
    }]
