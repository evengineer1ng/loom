from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.geopolitics.displacement_churn_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌀",
    "deterministic": True,
    "inputs": ["world.geopolitics_request.v1"],
    "outputs": ["world.geopolitics_response.v1"],
    "requires": [],
    "provides": ["world.displacement_churn_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "geopolitics", "displacement", "churn", "leaderboard"],
    "description": "Package tracked-field churn when a rising Deep Field civ displaces the weakest tracked kingdom.",
}


def build_displacement_churn_packet(
    incoming_civ_id: str,
    incoming_importance: float,
    displaced_kingdom_id: str,
    displaced_importance: float,
    displacement_margin: float,
    tick: int,
) -> dict[str, Any]:
    return {
        "incoming_civ_id": incoming_civ_id,
        "incoming_importance": float(incoming_importance),
        "displaced_kingdom_id": displaced_kingdom_id,
        "displaced_importance": float(displaced_importance),
        "displacement_margin": float(displacement_margin),
        "tick": int(tick),
        "outranked_by": float(incoming_importance) - float(displaced_importance),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_displacement_churn_packet(
        incoming_civ_id=str(payload.get("incoming_civ_id") or ""),
        incoming_importance=float(payload.get("incoming_importance") or 0.0),
        displaced_kingdom_id=str(payload.get("displaced_kingdom_id") or ""),
        displaced_importance=float(payload.get("displaced_importance") or 0.0),
        displacement_margin=float(payload.get("displacement_margin") or 5.0),
        tick=int(payload.get("tick") or 0),
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
        "receipt_id": "displacement-churn-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built displacement churn packet.",
        "refs": [],
        "data": {"incoming_civ_id": value.get("incoming_civ_id", ""), "displaced_kingdom_id": value.get("displaced_kingdom_id", "")},
    }]
