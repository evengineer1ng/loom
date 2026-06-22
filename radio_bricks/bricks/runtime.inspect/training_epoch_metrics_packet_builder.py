from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.training_epoch_metrics_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📊",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.training_epoch_metrics_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "training", "epoch", "metrics"],
    "description": "Package one epoch of representation-training metrics with train/val loss parts and scheduler learning rate context.",
}


def build_training_epoch_metrics_packet(
    epoch: int,
    train: dict[str, float] | None,
    val: dict[str, float] | None,
    learning_rate: float,
) -> dict[str, Any]:
    return {
        "epoch": int(epoch),
        "train": {str(key): float(value) for key, value in (train or {}).items()},
        "val": {str(key): float(value) for key, value in (val or {}).items()},
        "learning_rate": float(learning_rate),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_training_epoch_metrics_packet(
        epoch=int(payload.get("epoch") or 0),
        train=dict(payload.get("train") or {}),
        val=dict(payload.get("val") or {}),
        learning_rate=float(payload.get("learning_rate") or 0.0),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "training-epoch-metrics-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built training-epoch metrics packet.",
        "refs": [],
        "data": {
            "epoch": value.get("epoch", 0),
            "train_total": value.get("train", {}).get("total", 0.0),
            "val_total": value.get("val", {}).get("total", 0.0),
        },
    }]
