from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.geopolitics.tracked_kingdom_importance_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏛️",
    "deterministic": True,
    "inputs": ["world.geopolitics_request.v1"],
    "outputs": ["world.geopolitics_response.v1"],
    "requires": [],
    "provides": ["world.tracked_kingdom_importance_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "geopolitics", "importance", "tracked", "demotion"],
    "description": "Package a tracked kingdom's comparable importance score from economic, military, volatility, trade, and threat components.",
}


def build_tracked_kingdom_importance_packet(
    kingdom_id: str,
    economic_score: float,
    military_score: float,
    volatility_score: float,
    trade_dependency_score: float,
    threat_score: float,
    recency_bonus: float,
    total_importance: float,
) -> dict[str, Any]:
    return {
        "kingdom_id": kingdom_id,
        "components": {
            "economic": float(economic_score),
            "military": float(military_score),
            "volatility": float(volatility_score),
            "trade_dependency": float(trade_dependency_score),
            "threat": float(threat_score),
            "shock_recency_bonus": float(recency_bonus),
        },
        "total_importance": float(total_importance),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_tracked_kingdom_importance_packet(
        kingdom_id=str(payload.get("kingdom_id") or ""),
        economic_score=float(payload.get("economic_score") or 0.0),
        military_score=float(payload.get("military_score") or 0.0),
        volatility_score=float(payload.get("volatility_score") or 0.0),
        trade_dependency_score=float(payload.get("trade_dependency_score") or 0.0),
        threat_score=float(payload.get("threat_score") or 0.0),
        recency_bonus=float(payload.get("recency_bonus") or 0.0),
        total_importance=float(payload.get("total_importance") or 0.0),
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
        "receipt_id": "tracked-kingdom-importance-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built tracked-kingdom importance packet.",
        "refs": [],
        "data": {"kingdom_id": value.get("kingdom_id", ""), "total_importance": value.get("total_importance", 0.0)},
    }]
