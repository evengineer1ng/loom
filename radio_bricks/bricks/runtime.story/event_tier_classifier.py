from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.event_tier_classifier",
    "kind": "classifier",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.story_event_tier"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "event", "tier"],
    "description": "Classify events into core, context, world-signal, or noise tiers against a focal team identity.",
}


US_CORE_CATEGORIES = {
    "race_result", "qualifying_result", "dnf", "incident", "entity_birthday", "contract_expiry",
    "staff_change", "driver_hired", "driver_fired", "engineer_hired", "engineer_fired",
    "season_overachievement", "season_underperformance",
}
US_CONTEXT_CATEGORIES = {
    "financial_update", "budget_crisis", "ultimatum", "ownership_change", "regulation_change",
    "economic_warning", "hiring_freeze", "development_cancellation", "fire_sale", "administration",
    "ownership_ultimatum", "prize_money",
}
WORLD_SIGNAL_CATEGORIES = {
    "championship_result", "season_end", "tier_promotion", "tier_relegation", "team_liquidation",
    "team_promotion", "team_relegation", "offseason_end", "enter_race_weekend",
}


def classify_story_event(event: dict[str, Any] | None, player_team_name: str) -> dict[str, Any]:
    row = dict(event or {})
    category = str(row.get("category") or "")
    data = dict(row.get("data") or {})
    event_team = str(data.get("team") or "")
    if event_team == player_team_name and category in US_CORE_CATEGORIES:
        tier = "us_core"
    elif category in US_CONTEXT_CATEGORIES and (event_team == player_team_name or not event_team):
        tier = "us_context"
    elif category in WORLD_SIGNAL_CATEGORIES:
        tier = "world_signal"
    else:
        tier = "noise"
    return {"tier": tier, "category": category, "event_team": event_team}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = classify_story_event(
        event=dict(payload.get("event") or {}),
        player_team_name=str(payload.get("player_team_name") or ""),
    )
    output_packet = {
        "packet_type": "runtime.story_response.v1",
        "packet_version": "runtime.story_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "event-tier-classifier",
        "brick_id": CONCEPT["id"],
        "kind": "classification",
        "label": "Classified story event tier.",
        "refs": [],
        "data": {"tier": value.get("tier", "noise")},
    }]
