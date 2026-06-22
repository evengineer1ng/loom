from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "progression.profile.saved_behavioral_profile_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "💾",
    "deterministic": True,
    "inputs": ["progression.profile_request.v1"],
    "outputs": ["progression.profile_response.v1"],
    "requires": [],
    "provides": ["progression.saved_behavioral_profile_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["progression", "profile", "behavioral", "saved", "ngp"],
    "description": "Package the saved NGP+ behavioral profile with cumulative anomaly history, ecological disruption pattern, dominance bias, echo seeds, and run count.",
}


def build_saved_behavioral_profile_packet(
    behavioral_axis: str,
    anomaly_engagement_history: float,
    ecological_disruption_pattern: float,
    dominance_harmony_bias: float,
    completed_tier: int,
    echo_seeds: list[int] | None,
    run_count: int,
) -> dict[str, Any]:
    return {
        "behavioral_axis": behavioral_axis,
        "anomaly_engagement_history": float(anomaly_engagement_history),
        "ecological_disruption_pattern": float(ecological_disruption_pattern),
        "dominance_harmony_bias": float(dominance_harmony_bias),
        "completed_tier": int(completed_tier),
        "echo_seeds": [int(seed) for seed in (echo_seeds or [])],
        "run_count": int(run_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_saved_behavioral_profile_packet(
        behavioral_axis=str(payload.get("behavioral_axis") or ""),
        anomaly_engagement_history=float(payload.get("anomaly_engagement_history") or 0.0),
        ecological_disruption_pattern=float(payload.get("ecological_disruption_pattern") or 0.0),
        dominance_harmony_bias=float(payload.get("dominance_harmony_bias") or 0.0),
        completed_tier=int(payload.get("completed_tier") or 0),
        echo_seeds=list(payload.get("echo_seeds") or []),
        run_count=int(payload.get("run_count") or 0),
    )
    output_packet = {
        "packet_type": "progression.profile_response.v1",
        "packet_version": "progression.profile_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "saved-behavioral-profile-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built saved behavioral-profile packet.",
        "refs": [],
        "data": {"behavioral_axis": value.get("behavioral_axis", ""), "run_count": value.get("run_count", 0)},
    }]
