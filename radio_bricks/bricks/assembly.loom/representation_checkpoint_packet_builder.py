from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.representation_checkpoint_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "💾",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.representation_checkpoint_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "checkpoint", "representation", "training"],
    "description": "Package a representation-training checkpoint contract with config, epoch, best validation score, and loss-history summary.",
}


def build_representation_checkpoint_packet(
    config: dict[str, Any] | None,
    epoch: int,
    best_val: float,
    loss_history: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "config": dict(config or {}),
        "epoch": int(epoch),
        "best_val": float(best_val),
        "loss_history": [dict(item) for item in (loss_history or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_representation_checkpoint_packet(
        config=dict(payload.get("config") or {}),
        epoch=int(payload.get("epoch") or 0),
        best_val=float(payload.get("best_val") or 0.0),
        loss_history=list(payload.get("loss_history") or []),
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
        "receipt_id": "representation-checkpoint-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built representation-checkpoint packet.",
        "refs": [],
        "data": {
            "epoch": value.get("epoch", 0),
            "best_val": value.get("best_val", 0.0),
            "history_rows": len(value.get("loss_history", [])),
        },
    }]
