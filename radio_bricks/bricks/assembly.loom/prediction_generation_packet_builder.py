from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.prediction_generation_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎯",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.prediction_generation_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "forkuniverse", "prediction", "generation"],
    "description": "Package the generated prediction rows assembled from concept claims, templates, target threads, and spawn-confidence bias.",
}


def build_prediction_generation_packet(
    brief_seed: str,
    target_count: int,
    predictions: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "brief_seed": brief_seed,
        "target_count": int(target_count),
        "predictions": [dict(item) for item in (predictions or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_prediction_generation_packet(
        brief_seed=str(payload.get("brief_seed") or ""),
        target_count=int(payload.get("target_count") or 0),
        predictions=list(payload.get("predictions") or []),
    )
    output_packet = {
        "packet_type": "assembly.loom_response.v1",
        "packet_version": "assembly.loom_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "prediction-generation-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built prediction-generation packet.",
        "refs": [],
        "data": {"target_count": value.get("target_count", 0), "row_count": len(value.get("predictions", []))},
    }]
