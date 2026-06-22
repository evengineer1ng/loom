from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.simulation.family_hard_negative_loss_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪢",
    "deterministic": True,
    "inputs": ["math.simulation_request.v1"],
    "outputs": ["math.simulation_response.v1"],
    "requires": [],
    "provides": ["math.family_hard_negative_loss_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "simulation", "loss", "family", "negative"],
    "description": "Package within-family hard-negative loss settings with temperature, same-label positives, and same-family different-label negatives.",
}


def build_family_hard_negative_loss_packet(
    temperature: float,
    requires_distinct_labels: bool,
    returns_zero_without_pairs: bool,
) -> dict[str, Any]:
    return {
        "temperature": float(temperature),
        "requires_distinct_labels": bool(requires_distinct_labels),
        "returns_zero_without_pairs": bool(returns_zero_without_pairs),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_family_hard_negative_loss_packet(
        temperature=float(payload.get("temperature") or 0.0),
        requires_distinct_labels=bool(payload.get("requires_distinct_labels")),
        returns_zero_without_pairs=bool(payload.get("returns_zero_without_pairs")),
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
        "receipt_id": "family-hard-negative-loss-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built family hard-negative loss packet.",
        "refs": [],
        "data": {
            "temperature": value.get("temperature", 0.0),
            "returns_zero_without_pairs": value.get("returns_zero_without_pairs", False),
        },
    }]
