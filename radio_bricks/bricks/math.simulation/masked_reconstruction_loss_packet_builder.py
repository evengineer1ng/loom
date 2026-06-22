from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.simulation.masked_reconstruction_loss_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎭",
    "deterministic": True,
    "inputs": ["math.simulation_request.v1"],
    "outputs": ["math.simulation_response.v1"],
    "requires": [],
    "provides": ["math.masked_reconstruction_loss_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "simulation", "loss", "reconstruction", "mask"],
    "description": "Package masked reconstruction loss semantics where only masked positions contribute to MSE and empty masks short-circuit to zero.",
}


def build_masked_reconstruction_loss_packet(mask_only: bool, empty_mask_zero: bool, metric: str) -> dict[str, Any]:
    return {
        "mask_only": bool(mask_only),
        "empty_mask_zero": bool(empty_mask_zero),
        "metric": str(metric),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_masked_reconstruction_loss_packet(
        mask_only=bool(payload.get("mask_only")),
        empty_mask_zero=bool(payload.get("empty_mask_zero")),
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
        "receipt_id": "masked-reconstruction-loss-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built masked reconstruction-loss packet.",
        "refs": [],
        "data": {
            "metric": value.get("metric", ""),
            "mask_only": value.get("mask_only", False),
        },
    }]
