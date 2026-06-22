from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.encoder_loader_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📦",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.encoder_loader_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "encoder", "loader", "checkpoint"],
    "description": "Package encoder-loading requirements from a saved checkpoint, including config keys needed to reconstruct the MotionEncoder before state load.",
}


def build_encoder_loader_packet(
    stream_dim: int,
    d_model: int,
    nhead: int,
    num_layers: int,
    dim_feedforward: int,
    latent_dim: int,
) -> dict[str, Any]:
    return {
        "stream_dim": int(stream_dim),
        "d_model": int(d_model),
        "nhead": int(nhead),
        "num_layers": int(num_layers),
        "dim_feedforward": int(dim_feedforward),
        "latent_dim": int(latent_dim),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_encoder_loader_packet(
        stream_dim=int(payload.get("stream_dim") or 0),
        d_model=int(payload.get("d_model") or 0),
        nhead=int(payload.get("nhead") or 0),
        num_layers=int(payload.get("num_layers") or 0),
        dim_feedforward=int(payload.get("dim_feedforward") or 0),
        latent_dim=int(payload.get("latent_dim") or 0),
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
        "receipt_id": "encoder-loader-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built encoder-loader packet.",
        "refs": [],
        "data": {
            "stream_dim": value.get("stream_dim", 0),
            "latent_dim": value.get("latent_dim", 0),
        },
    }]
