from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.score_pool_normalization_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🫧",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.score_pool_normalization_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "score", "pool", "normalization"],
    "description": "Package shared-pool score normalization with neutral/negative priors, temperature, label count, and probability-space threshold scaling.",
}


def build_score_pool_normalization_packet(
    neutral_prior: float,
    negative_prior: float,
    temperature: float,
    label_count: int,
    pooled_sum: float,
) -> dict[str, Any]:
    return {
        "neutral_prior": float(neutral_prior),
        "negative_prior": float(negative_prior),
        "temperature": float(temperature),
        "label_count": int(label_count),
        "pooled_sum": float(pooled_sum),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_score_pool_normalization_packet(
        neutral_prior=float(payload.get("neutral_prior") or 0.0),
        negative_prior=float(payload.get("negative_prior") or 0.0),
        temperature=float(payload.get("temperature") or 0.0),
        label_count=int(payload.get("label_count") or 0),
        pooled_sum=float(payload.get("pooled_sum") or 0.0),
    )
    output_packet = {
        "packet_type": "math.interpretation_response.v1",
        "packet_version": "math.interpretation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "score-pool-normalization-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built score-pool normalization packet.",
        "refs": [],
        "data": {
            "label_count": value.get("label_count", 0),
            "temperature": value.get("temperature", 0.0),
            "pooled_sum": value.get("pooled_sum", 0.0),
        },
    }]
