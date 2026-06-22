from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.simulation.future_latent_loss_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔮",
    "deterministic": True,
    "inputs": ["math.simulation_request.v1"],
    "outputs": ["math.simulation_response.v1"],
    "requires": [],
    "provides": ["math.future_latent_loss_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "simulation", "loss", "future", "latent"],
    "description": "Package future-latent prediction loss semantics using cosine alignment between predicted and actual future window latents.",
}


def build_future_latent_loss_packet(normalized_prediction: bool, normalized_target: bool, metric: str) -> dict[str, Any]:
    return {
        "normalized_prediction": bool(normalized_prediction),
        "normalized_target": bool(normalized_target),
        "metric": str(metric),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_future_latent_loss_packet(
        normalized_prediction=bool(payload.get("normalized_prediction")),
        normalized_target=bool(payload.get("normalized_target")),
        metric=str(payload.get("metric") or ""),
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
        "receipt_id": "future-latent-loss-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built future-latent loss packet.",
        "refs": [],
        "data": {
            "metric": value.get("metric", ""),
        },
    }]
