from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.power.power_gradient_modifier_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📈",
    "deterministic": True,
    "inputs": ["world.power_request.v1"],
    "outputs": ["world.power_response.v1"],
    "requires": [],
    "provides": ["world.power_gradient_modifier_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "power", "gradient", "influence", "anchor"],
    "description": "Package how a stored power rank amplifies influence vectors, diplomatic stance, and regional-anchor myth pressure.",
}


def build_power_gradient_modifier_packet(
    kingdom_id: str,
    influence_radius: float,
    diplomatic_baseline: float,
    is_regional_anchor: bool,
    myth_resonance: float,
) -> dict[str, Any]:
    myth_pressure_bonus = float(myth_resonance) * 0.5 if is_regional_anchor else 0.0
    return {
        "kingdom_id": kingdom_id,
        "influence_radius_multiplier": float(influence_radius),
        "diplomatic_baseline_shift": float(diplomatic_baseline),
        "regional_anchor_active": bool(is_regional_anchor),
        "myth_pressure_bonus": myth_pressure_bonus,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_power_gradient_modifier_packet(
        kingdom_id=str(payload.get("kingdom_id") or ""),
        influence_radius=float(payload.get("influence_radius") or 1.0),
        diplomatic_baseline=float(payload.get("diplomatic_baseline") or 0.0),
        is_regional_anchor=bool(payload.get("is_regional_anchor", False)),
        myth_resonance=float(payload.get("myth_resonance") or 0.0),
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
        "receipt_id": "power-gradient-modifier",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built power-gradient modifier packet.",
        "refs": [],
        "data": {"kingdom_id": value.get("kingdom_id", ""), "regional_anchor_active": value.get("regional_anchor_active", False)},
    }]
