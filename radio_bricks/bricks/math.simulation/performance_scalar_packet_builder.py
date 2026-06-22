from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.simulation.performance_scalar_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📈",
    "deterministic": True,
    "inputs": ["math.simulation_request.v1"],
    "outputs": ["math.simulation_response.v1"],
    "requires": [],
    "provides": ["math.performance_scalar_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "simulation", "performance", "scalar", "smoothing"],
    "description": "Package a smoothed performance scalar with weighted metric contributions, budget normalization, and final bounded value in [-1, 1].",
}


def build_performance_scalar_packet(
    raw_scalar: float,
    smoothed_scalar: float,
    morale_weight: float,
    reputation_weight: float,
    legitimacy_weight: float,
    position_weight: float,
    budget_weight: float,
) -> dict[str, Any]:
    return {
        "raw_scalar": float(raw_scalar),
        "smoothed_scalar": float(smoothed_scalar),
        "morale_weight": float(morale_weight),
        "reputation_weight": float(reputation_weight),
        "legitimacy_weight": float(legitimacy_weight),
        "position_weight": float(position_weight),
        "budget_weight": float(budget_weight),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_performance_scalar_packet(
        raw_scalar=float(payload.get("raw_scalar") or 0.0),
        smoothed_scalar=float(payload.get("smoothed_scalar") or 0.0),
        morale_weight=float(payload.get("morale_weight") or 0.0),
        reputation_weight=float(payload.get("reputation_weight") or 0.0),
        legitimacy_weight=float(payload.get("legitimacy_weight") or 0.0),
        position_weight=float(payload.get("position_weight") or 0.0),
        budget_weight=float(payload.get("budget_weight") or 0.0),
    )
    output_packet = {
        "packet_type": "math.simulation_response.v1",
        "packet_version": "math.simulation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "performance-scalar-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built performance-scalar packet.",
        "refs": [],
        "data": {
            "raw_scalar": value.get("raw_scalar", 0.0),
            "smoothed_scalar": value.get("smoothed_scalar", 0.0),
        },
    }]
