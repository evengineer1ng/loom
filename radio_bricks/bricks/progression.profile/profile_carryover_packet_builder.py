from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "progression.profile.profile_carryover_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔁",
    "deterministic": True,
    "inputs": ["progression.profile_request.v1"],
    "outputs": ["progression.profile_response.v1"],
    "requires": [],
    "provides": ["progression.profile_carryover_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["progression", "profile", "carryover", "ngp", "tier"],
    "description": "Package the additive carryover effects an NGP+ profile applies to a fresh Neikos island run.",
}


def build_profile_carryover_packet(
    ecological_balance_delta: float,
    urbanization_level_delta: float,
    anomaly_stability_delta: float,
    competitive_focus_delta: float,
    exploration_depth_delta: float,
    tier_floor_raised: bool,
    resulting_base_tier: str,
) -> dict[str, Any]:
    return {
        "ecological_balance_delta": float(ecological_balance_delta),
        "urbanization_level_delta": float(urbanization_level_delta),
        "anomaly_stability_delta": float(anomaly_stability_delta),
        "competitive_focus_delta": float(competitive_focus_delta),
        "exploration_depth_delta": float(exploration_depth_delta),
        "tier_floor_raised": bool(tier_floor_raised),
        "resulting_base_tier": resulting_base_tier,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_profile_carryover_packet(
        ecological_balance_delta=float(payload.get("ecological_balance_delta") or 0.0),
        urbanization_level_delta=float(payload.get("urbanization_level_delta") or 0.0),
        anomaly_stability_delta=float(payload.get("anomaly_stability_delta") or 0.0),
        competitive_focus_delta=float(payload.get("competitive_focus_delta") or 0.0),
        exploration_depth_delta=float(payload.get("exploration_depth_delta") or 0.0),
        tier_floor_raised=bool(payload.get("tier_floor_raised", False)),
        resulting_base_tier=str(payload.get("resulting_base_tier") or ""),
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
        "receipt_id": "profile-carryover-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built profile-carryover packet.",
        "refs": [],
        "data": {"tier_floor_raised": value.get("tier_floor_raised", False), "resulting_base_tier": value.get("resulting_base_tier", "")},
    }]
