from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.idle_tier_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⏳",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.idle_tier_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "idle", "tier", "scheduler"],
    "description": "Package idle-tier thresholds and the currently detected tier for scheduler gating and background work arbitration.",
}


def build_idle_tier_packet(
    current_tier: int,
    brief_threshold_seconds: float,
    medium_threshold_seconds: float,
    long_threshold_seconds: float,
    extended_threshold_seconds: float,
) -> dict[str, Any]:
    return {
        "current_tier": int(current_tier),
        "brief_threshold_seconds": float(brief_threshold_seconds),
        "medium_threshold_seconds": float(medium_threshold_seconds),
        "long_threshold_seconds": float(long_threshold_seconds),
        "extended_threshold_seconds": float(extended_threshold_seconds),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_idle_tier_packet(
        current_tier=int(payload.get("current_tier") or 0),
        brief_threshold_seconds=float(payload.get("brief_threshold_seconds") or 0.0),
        medium_threshold_seconds=float(payload.get("medium_threshold_seconds") or 0.0),
        long_threshold_seconds=float(payload.get("long_threshold_seconds") or 0.0),
        extended_threshold_seconds=float(payload.get("extended_threshold_seconds") or 0.0),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "idle-tier-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built idle-tier packet.",
        "refs": [],
        "data": {
            "current_tier": value.get("current_tier", 0),
            "extended_threshold_seconds": value.get("extended_threshold_seconds", 0.0),
        },
    }]
