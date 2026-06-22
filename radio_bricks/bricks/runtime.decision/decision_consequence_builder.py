from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.decision_consequence_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.decision_consequence_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "consequence", "state"],
    "description": "Translate a decision category and chosen option into concrete state deltas and follow-on events.",
}


def build_decision_consequence_packet(category: str, option_id: str, team_name: str, tick: int) -> dict[str, Any]:
    state_delta: dict[str, Any] = {}
    follow_on_events: list[dict[str, Any]] = []
    if category == "ownership_ultimatum":
        if option_id == "accept_terms":
            state_delta = {"reputation_delta": -10, "ownership_confidence": 60.0}
        elif option_id == "seek_investor":
            state_delta = {"cash_delta": 100000.0, "ownership_confidence": 55.0}
        elif option_id == "resign":
            state_delta = {"resignation_flag": True}
    elif category == "fire_sale":
        if option_id.startswith("sell_facility_"):
            state_delta = {"facility_sale_key": option_id.replace("sell_facility_", ""), "requires_facility_sale_resolution": True}
        elif option_id == "emergency_loan":
            state_delta = {"cash_delta": 50000.0, "emergency_debt_delta": 75000.0}
            follow_on_events.append({
                "event_type": "financial",
                "category": "emergency_loan",
                "ts": int(tick),
                "priority": 85.0,
                "severity": "warning",
                "data": {"team": team_name, "loan_amount": 50000.0, "debt_incurred": 75000.0},
            })
    elif category == "sponsor_bailout":
        if option_id == "accept_bailout":
            state_delta = {"requires_bailout_offer_lookup": True, "confidence_boost": 15.0}
            follow_on_events.append({
                "event_type": "outcome",
                "category": "sponsor_bailout_accepted",
                "ts": int(tick),
                "priority": 90.0,
                "severity": "major",
                "data": {"team": team_name},
            })
        elif option_id == "decline_bailout":
            follow_on_events.append({
                "event_type": "outcome",
                "category": "sponsor_bailout_declined",
                "ts": int(tick),
                "priority": 75.0,
                "severity": "info",
                "data": {"team": team_name},
            })
    elif category == "development_risk":
        state_delta = {"development_risk_profile": option_id}
    return {"category": category, "option_id": option_id, "state_delta": state_delta, "follow_on_events": follow_on_events}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_decision_consequence_packet(
        category=str(payload.get("category") or ""),
        option_id=str(payload.get("option_id") or ""),
        team_name=str(payload.get("team_name") or ""),
        tick=int(payload.get("tick") or 0),
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
        "receipt_id": "decision-consequence-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built decision consequence packet.",
        "refs": [],
        "data": {"follow_on_event_count": len(value.get("follow_on_events", []))},
    }]
