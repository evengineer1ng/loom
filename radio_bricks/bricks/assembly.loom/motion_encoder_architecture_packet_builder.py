from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.motion_encoder_architecture_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏗️",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.motion_encoder_architecture_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "encoder", "architecture", "dual-stream"],
    "description": "Package the confidence-aware dual-stream motion encoder shape including stream dims, transformer depth, latent dims, and projection-head topology.",
}


def build_motion_encoder_architecture_packet(
    stream_dim: int,
    d_model: int,
    nhead: int,
    num_layers: int,
    dim_feedforward: int,
    latent_dim: int,
    positional_encoding: str,
    contrastive_projection: bool,
    shared_cross_view_weights: bool,
) -> dict[str, Any]:
    return {
        "stream_dim": int(stream_dim),
        "d_model": int(d_model),
        "nhead": int(nhead),
        "num_layers": int(num_layers),
        "dim_feedforward": int(dim_feedforward),
        "latent_dim": int(latent_dim),
        "positional_encoding": str(positional_encoding),
        "contrastive_projection": bool(contrastive_projection),
        "shared_cross_view_weights": bool(shared_cross_view_weights),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_motion_encoder_architecture_packet(
        stream_dim=int(payload.get("stream_dim") or 0),
        d_model=int(payload.get("d_model") or 0),
        nhead=int(payload.get("nhead") or 0),
        num_layers=int(payload.get("num_layers") or 0),
        dim_feedforward=int(payload.get("dim_feedforward") or 0),
        latent_dim=int(payload.get("latent_dim") or 0),
        positional_encoding=str(payload.get("positional_encoding") or ""),
        contrastive_projection=bool(payload.get("contrastive_projection")),
        shared_cross_view_weights=bool(payload.get("shared_cross_view_weights")),
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
        "receipt_id": "motion-encoder-architecture-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built motion-encoder architecture packet.",
        "refs": [],
        "data": {
            "stream_dim": value.get("stream_dim", 0),
            "latent_dim": value.get("latent_dim", 0),
            "num_layers": value.get("num_layers", 0),
        },
    }]
