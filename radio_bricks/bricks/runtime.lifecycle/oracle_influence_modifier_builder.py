from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.lifecycle.oracle_influence_modifier_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.lifecycle_request.v1"],
    "outputs": ["runtime.lifecycle_response.v1"],
    "requires": [],
    "provides": ["runtime.oracle_influence_modifiers"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "lifecycle", "oracle", "modifiers"],
    "description": "Translate oracle lifecycle state and intensity into faith, ideology, shock, and stability modifiers.",
}


def build_oracle_influence_modifiers(state: str, intensity: float) -> dict[str, Any]:
    level = max(0.0, min(1.0, float(intensity)))
    if state == "ACTIVE":
        return {
            "faith_mult": 1.0 + 0.5 * level,
            "ideology_mult": 1.0 + 0.3 * level,
            "shock_mult": max(0.5, 1.0 - 0.2 * level),
            "stability_mult": 1.0 + 0.2 * level,
            "faith_passive_decay": 0.0,
            "divergence_passive_growth": 0.0,
        }
    if state == "SLEEPING":
        return {
            "faith_mult": 1.0,
            "ideology_mult": 1.0,
            "shock_mult": 1.08,
            "stability_mult": 1.0,
            "faith_passive_decay": 0.035,
            "divergence_passive_growth": 0.02,
        }
    return {
        "faith_mult": 1.0 + 0.5 * level * 0.5,
        "ideology_mult": 1.0 + 0.3 * level * 0.5,
        "shock_mult": 1.0 + 0.08 * (1.0 - level),
        "stability_mult": 1.0 + 0.2 * level * 0.3,
        "faith_passive_decay": 0.035 * (1.0 - level),
        "divergence_passive_growth": 0.02 * (1.0 - level),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_oracle_influence_modifiers(
        state=str(payload.get("state") or "SLEEPING"),
        intensity=float(payload.get("intensity") or 0.0),
    )
    output_packet = {
        "packet_type": "runtime.lifecycle_response.v1",
        "packet_version": "runtime.lifecycle_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "oracle-influence-modifiers",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built oracle influence modifiers.",
        "refs": [],
        "data": {"shock_mult": value.get("shock_mult", 1.0)},
    }]
