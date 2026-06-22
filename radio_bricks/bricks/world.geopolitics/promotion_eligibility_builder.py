from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.geopolitics.promotion_eligibility_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⬆️",
    "deterministic": True,
    "inputs": ["world.geopolitics_request.v1"],
    "outputs": ["world.geopolitics_response.v1"],
    "requires": [],
    "provides": ["world.promotion_eligibility_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "geopolitics", "promotion", "eligibility", "threshold"],
    "description": "Package a Deep Field civ's promotion eligibility against importance thresholds and tracked-field capacity.",
}


def build_promotion_eligibility_packet(
    civ_id: str,
    importance: float,
    promotion_threshold: float,
    tracked_count: int,
    max_tracked: int,
    is_promoted: bool,
) -> dict[str, Any]:
    meets_threshold = float(importance) >= float(promotion_threshold)
    has_capacity = int(tracked_count) < int(max_tracked)
    return {
        "civ_id": civ_id,
        "importance": float(importance),
        "promotion_threshold": float(promotion_threshold),
        "tracked_count": int(tracked_count),
        "max_tracked": int(max_tracked),
        "is_promoted": bool(is_promoted),
        "meets_threshold": meets_threshold,
        "has_capacity": has_capacity,
        "eligible": (not bool(is_promoted)) and meets_threshold,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_promotion_eligibility_packet(
        civ_id=str(payload.get("civ_id") or ""),
        importance=float(payload.get("importance") or 0.0),
        promotion_threshold=float(payload.get("promotion_threshold") or 45.0),
        tracked_count=int(payload.get("tracked_count") or 0),
        max_tracked=int(payload.get("max_tracked") or 20),
        is_promoted=bool(payload.get("is_promoted", False)),
    )
    output_packet = {
        "packet_type": "world.geopolitics_response.v1",
        "packet_version": "world.geopolitics_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "promotion-eligibility-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built promotion-eligibility packet.",
        "refs": [],
        "data": {"civ_id": value.get("civ_id", ""), "eligible": value.get("eligible", False)},
    }]
