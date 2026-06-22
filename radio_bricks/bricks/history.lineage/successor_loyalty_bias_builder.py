from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.lineage.successor_loyalty_bias_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🫀",
    "deterministic": True,
    "inputs": ["history.lineage_request.v1"],
    "outputs": ["history.lineage_response.v1"],
    "requires": [],
    "provides": ["history.successor_loyalty_bias_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "lineage", "successor", "loyalty", "health", "era"],
    "description": "Package successor oracle-loyalty bias from kingdom health, trend, and era-memory conditions.",
}


def build_successor_loyalty_bias_packet(
    successor_id: str,
    era: str,
    health_composite: float,
    health_trend: str,
    loyalty_bias: float,
) -> dict[str, Any]:
    return {
        "successor_id": successor_id,
        "era": era,
        "health_composite": float(health_composite),
        "health_trend": health_trend,
        "oracle_loyalty_bias": float(loyalty_bias),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_successor_loyalty_bias_packet(
        successor_id=str(payload.get("successor_id") or ""),
        era=str(payload.get("era") or ""),
        health_composite=float(payload.get("health_composite") or 0.0),
        health_trend=str(payload.get("health_trend") or ""),
        loyalty_bias=float(payload.get("loyalty_bias") or 0.0),
    )
    output_packet = {
        "packet_type": "history.lineage_response.v1",
        "packet_version": "history.lineage_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "successor-loyalty-bias",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built successor loyalty-bias packet.",
        "refs": [],
        "data": {"successor_id": value.get("successor_id", ""), "era": value.get("era", "")},
    }]
