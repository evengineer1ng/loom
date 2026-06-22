from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.lineage.intergenerational_trait_bias_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧬",
    "deterministic": True,
    "inputs": ["history.lineage_request.v1"],
    "outputs": ["history.lineage_response.v1"],
    "requires": [],
    "provides": ["history.intergenerational_trait_bias_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "lineage", "generation", "traits", "era"],
    "description": "Package era-shaped successor trait drift as a reusable intergenerational bias packet.",
}


def build_intergenerational_trait_bias_packet(
    era: str,
    successor_id: str,
    trait_biases: dict[str, float] | None,
) -> dict[str, Any]:
    biases = {str(key): float(value) for key, value in (trait_biases or {}).items()}
    return {
        "era": era,
        "successor_id": successor_id,
        "trait_biases": biases,
        "traits_affected": sorted(biases.keys()),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_intergenerational_trait_bias_packet(
        era=str(payload.get("era") or ""),
        successor_id=str(payload.get("successor_id") or ""),
        trait_biases=dict(payload.get("trait_biases") or {}),
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
        "receipt_id": "intergenerational-trait-bias",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built intergenerational trait-bias packet.",
        "refs": [],
        "data": {"era": value.get("era", ""), "traits_affected": value.get("traits_affected", [])},
    }]
