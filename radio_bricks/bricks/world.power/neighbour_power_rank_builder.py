from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.power.neighbour_power_rank_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏔️",
    "deterministic": True,
    "inputs": ["world.power_request.v1"],
    "outputs": ["world.power_response.v1"],
    "requires": [],
    "provides": ["world.neighbour_power_rank"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "power", "neighbour", "stability", "anchor"],
    "description": "Build a long-horizon neighbour power-rank packet with stability, influence radius, anchor state, and diplomatic baseline.",
}


def build_neighbour_power_rank(
    kingdom_id: str,
    stability_score: float,
    influence_radius: float,
    is_regional_anchor: bool,
    diplomatic_baseline: float,
    myth_resonance: float,
    ticks_tracked: int,
) -> dict[str, Any]:
    return {
        "kingdom_id": kingdom_id,
        "stability_score": float(stability_score),
        "influence_radius": float(influence_radius),
        "is_regional_anchor": bool(is_regional_anchor),
        "diplomatic_baseline": float(diplomatic_baseline),
        "myth_resonance": float(myth_resonance),
        "ticks_tracked": int(ticks_tracked),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_neighbour_power_rank(
        kingdom_id=str(payload.get("kingdom_id") or ""),
        stability_score=float(payload.get("stability_score") or 0.0),
        influence_radius=float(payload.get("influence_radius") or 1.0),
        is_regional_anchor=bool(payload.get("is_regional_anchor", False)),
        diplomatic_baseline=float(payload.get("diplomatic_baseline") or 0.0),
        myth_resonance=float(payload.get("myth_resonance") or 0.0),
        ticks_tracked=int(payload.get("ticks_tracked") or 0),
    )
    output_packet = {
        "packet_type": "world.power_response.v1",
        "packet_version": "world.power_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "neighbour-power-rank",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built neighbour power-rank packet.",
        "refs": [],
        "data": {
            "kingdom_id": value.get("kingdom_id", ""),
            "is_regional_anchor": value.get("is_regional_anchor", False),
        },
    }]
