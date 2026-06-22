from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sponsor.sponsor_confidence_evaluator",
    "kind": "evaluator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.sponsor_request.v1"],
    "outputs": ["runtime.sponsor_response.v1"],
    "requires": [],
    "provides": ["runtime.sponsor_confidence_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "sponsor", "confidence", "math"],
    "description": "Evaluate sponsor confidence from standings, points rate, reputation, media, and infrastructure gaps.",
}


def evaluate_sponsor_confidence(
    championship_position: int,
    total_teams: int,
    points: float,
    races_run: int,
    reputation: float,
    media_mentions: float,
    infrastructure_gaps: list[float] | None = None,
    performance_dependency: float = 0.5,
    reputation_dependency: float = 0.4,
    volatility: float = 0.5,
) -> dict[str, Any]:
    teams = max(1, int(total_teams))
    pos = max(1, min(int(championship_position), teams))
    position_percentile = 1.0 - ((pos - 1) / max(1, teams - 1))
    if pos <= 3:
        position_factor = 0.20 + (position_percentile * 0.20)
    elif position_percentile > 0.5:
        position_factor = 0.05
    else:
        position_factor = -0.15 * (1.0 - position_percentile * 2)

    races = max(1, int(races_run))
    points_per_race = float(points) / races
    expected_ppr = max(2.0, 18.0 - (pos - 1) * (14.0 / max(1, teams - 1)))
    points_gap = (points_per_race - expected_ppr) / max(1.0, expected_ppr)
    points_factor = max(-0.20, min(0.20, points_gap * 0.20))

    rep_factor = ((float(reputation) - 50.0) / 100.0) * 0.15
    media_factor = ((float(media_mentions) - 5.0) / 5.0) * 0.10

    gaps = list(infrastructure_gaps or [])
    avg_gap = (sum(gaps) / len(gaps)) if gaps else 0.0
    infrastructure_factor = max(-0.40, min(0.15, (avg_gap / 10.0) * 0.05)) if gaps else 0.0

    base_weight = 0.85 if gaps else 1.0
    weighted_total = (
        position_factor * 0.40 * float(performance_dependency) * base_weight +
        points_factor * 0.30 * float(performance_dependency) * base_weight +
        rep_factor * 0.20 * float(reputation_dependency) * base_weight +
        media_factor * 0.10 * float(reputation_dependency) * base_weight +
        infrastructure_factor * 0.15
    )
    confidence_delta = weighted_total * 25.0
    volatility_multiplier = 0.7 + (float(volatility) * 0.8)
    if confidence_delta < 0:
        volatility_multiplier = min(volatility_multiplier, 1.3)
    confidence_delta *= volatility_multiplier
    return {
        "confidence_delta": confidence_delta,
        "factors": {
            "championship_position": position_factor,
            "points_rate": points_factor,
            "reputation": rep_factor,
            "media_mentions": media_factor,
            "infrastructure": infrastructure_factor,
        },
        "weighted_total": weighted_total,
        "volatility_multiplier": volatility_multiplier,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = evaluate_sponsor_confidence(
        championship_position=int(payload.get("championship_position") or 1),
        total_teams=int(payload.get("total_teams") or 1),
        points=float(payload.get("points") or 0.0),
        races_run=int(payload.get("races_run") or 1),
        reputation=float(payload.get("reputation") or 50.0),
        media_mentions=float(payload.get("media_mentions") or 5.0),
        infrastructure_gaps=list(payload.get("infrastructure_gaps") or []),
        performance_dependency=float(payload.get("performance_dependency") or 0.5),
        reputation_dependency=float(payload.get("reputation_dependency") or 0.4),
        volatility=float(payload.get("volatility") or 0.5),
    )
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
        "receipt_id": "sponsor-confidence-packet",
        "brick_id": CONCEPT["id"],
        "kind": "evaluate",
        "label": "Evaluated sponsor confidence.",
        "refs": [],
        "data": {"confidence_delta": value.get("confidence_delta", 0.0)},
    }]
