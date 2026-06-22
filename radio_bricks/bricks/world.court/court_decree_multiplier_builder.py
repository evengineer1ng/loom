from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.court.court_decree_multiplier_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["world.court_request.v1"],
    "outputs": ["world.court_response.v1"],
    "requires": [],
    "provides": ["world.court_decree_multiplier_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "court", "decree", "multiplier"],
    "description": "Apply location-based decree multipliers to a policy vector before world propagation.",
}


def build_court_decree_multiplier_packet(policy_vector: dict[str, float] | None, location_multipliers: dict[str, float] | None) -> dict[str, Any]:
    base = dict(policy_vector or {})
    multipliers = dict(location_multipliers or {})
    modified = {axis: float(value) * float(multipliers.get(axis, 1.0)) for axis, value in base.items()}
    return {
        "base_policy_vector": base,
        "location_multipliers": multipliers,
        "modified_policy_vector": modified,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_court_decree_multiplier_packet(
        policy_vector=dict(payload.get("policy_vector") or {}),
        location_multipliers=dict(payload.get("location_multipliers") or {}),
    )
    output_packet = {
        "packet_type": "world.court_response.v1",
        "packet_version": "world.court_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "court-decree-multiplier",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built court decree multiplier packet.",
        "refs": [],
        "data": {"axis_count": len(value.get("modified_policy_vector", {}))},
    }]
