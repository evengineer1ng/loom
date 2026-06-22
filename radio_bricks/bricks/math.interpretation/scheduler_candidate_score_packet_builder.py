from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.scheduler_candidate_score_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📐",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.scheduler_candidate_score_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "scheduler", "candidate", "score"],
    "description": "Package a deterministic scheduler candidate score with urgency, priority, idle bonus, compute penalty, interruption risk, and mode bias outputs.",
}


def build_scheduler_candidate_score_packet(
    score: float,
    urgency: float,
    priority: float,
    idle_tier: int,
    compute_cost: float,
    interruption_risk: float,
    mode_bias: float,
    priority_bias: float,
) -> dict[str, Any]:
    return {
        "score": float(score),
        "urgency": float(urgency),
        "priority": float(priority),
        "idle_tier": int(idle_tier),
        "compute_cost": float(compute_cost),
        "interruption_risk": float(interruption_risk),
        "mode_bias": float(mode_bias),
        "priority_bias": float(priority_bias),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_scheduler_candidate_score_packet(
        score=float(payload.get("score") or 0.0),
        urgency=float(payload.get("urgency") or 0.0),
        priority=float(payload.get("priority") or 0.0),
        idle_tier=int(payload.get("idle_tier") or 0),
        compute_cost=float(payload.get("compute_cost") or 0.0),
        interruption_risk=float(payload.get("interruption_risk") or 0.0),
        mode_bias=float(payload.get("mode_bias") or 0.0),
        priority_bias=float(payload.get("priority_bias") or 0.0),
    )
    output_packet = {
        "packet_type": "math.interpretation_response.v1",
        "packet_version": "math.interpretation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "scheduler-candidate-score-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built scheduler candidate-score packet.",
        "refs": [],
        "data": {
            "score": value.get("score", 0.0),
            "idle_tier": value.get("idle_tier", 0),
        },
    }]
