from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.metrics.team_pulse_metric_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["history.metrics_request.v1"],
    "outputs": ["history.metrics_response.v1"],
    "requires": [],
    "provides": ["history.team_pulse_metric_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "metrics", "pulse", "math"],
    "description": "Blend trend, finances, development, and league percentile into a team pulse narrative state.",
}


def build_team_pulse_metric_packet(
    performance_trend: float,
    financial_stability: float,
    development_speed: float,
    league_percentile: float,
    tick: int,
) -> dict[str, Any]:
    team_pulse = (
        float(performance_trend) * 0.35 +
        float(financial_stability) * 0.25 +
        float(development_speed) * 0.20 +
        float(league_percentile) * 0.20
    )

    if league_percentile >= 95:
        competitive_tier = "dominant"
    elif league_percentile >= 80:
        competitive_tier = "contender"
    elif league_percentile >= 60:
        competitive_tier = "upper_midfield"
    elif league_percentile >= 40:
        competitive_tier = "midfield"
    elif league_percentile >= 20:
        competitive_tier = "lower_midfield"
    elif league_percentile >= 5:
        competitive_tier = "backmarker"
    else:
        competitive_tier = "crisis"

    if team_pulse >= 80:
        narrative_temperature = "surging"
    elif team_pulse >= 65:
        narrative_temperature = "tense"
    elif team_pulse >= 35:
        narrative_temperature = "stable"
    elif team_pulse >= 20:
        narrative_temperature = "fragile"
    elif team_pulse >= 10:
        narrative_temperature = "volatile"
    else:
        narrative_temperature = "desperate"

    return {
        "team_pulse": team_pulse,
        "performance_trend_component": float(performance_trend),
        "financial_stability_component": float(financial_stability),
        "development_speed_component": float(development_speed),
        "league_percentile_component": float(league_percentile),
        "competitive_tier": competitive_tier,
        "narrative_temperature": narrative_temperature,
        "last_updated_tick": int(tick),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_team_pulse_metric_packet(
        performance_trend=float(payload.get("performance_trend") or 0.0),
        financial_stability=float(payload.get("financial_stability") or 50.0),
        development_speed=float(payload.get("development_speed") or 50.0),
        league_percentile=float(payload.get("league_percentile") or 50.0),
        tick=int(payload.get("tick") or 0),
    )
    output_packet = {
        "packet_type": "history.metrics_response.v1",
        "packet_version": "history.metrics_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "team-pulse-metric-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built team pulse metric packet.",
        "refs": [],
        "data": {"team_pulse": value.get("team_pulse", 0.0), "temperature": value.get("narrative_temperature", "stable")},
    }]
