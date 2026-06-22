from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.simulation.info_nce_loss_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧲",
    "deterministic": True,
    "inputs": ["math.simulation_request.v1"],
    "outputs": ["math.simulation_response.v1"],
    "requires": [],
    "provides": ["math.info_nce_loss_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "simulation", "loss", "contrastive", "infonce"],
    "description": "Package symmetric InfoNCE loss settings with temperature and paired-view semantics for contrastive alignment.",
}


def build_info_nce_loss_packet(temperature: float, symmetric: bool, projected_latents: bool) -> dict[str, Any]:
    return {
        "temperature": float(temperature),
        "symmetric": bool(symmetric),
        "projected_latents": bool(projected_latents),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_info_nce_loss_packet(
        temperature=float(payload.get("temperature") or 0.0),
        symmetric=bool(payload.get("symmetric")),
        projected_latents=bool(payload.get("projected_latents")),
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
        "receipt_id": "info-nce-loss-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built InfoNCE loss packet.",
        "refs": [],
        "data": {
            "temperature": value.get("temperature", 0.0),
            "symmetric": value.get("symmetric", False),
        },
    }]
