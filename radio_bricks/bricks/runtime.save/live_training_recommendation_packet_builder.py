from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.live_training_recommendation_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧷",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.live_training_recommendation_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "training", "recommendation", "floor"],
    "description": "Package a live trainer recommendation with target label, suggested pose gate, motion floor, and captured sample count.",
}


def build_live_training_recommendation_packet(
    label: str,
    envelope_min_coverage: float,
    motion_gate_floor: float,
    motion_gate_op: str,
    sample_count: int,
) -> dict[str, Any]:
    return {
        "label": str(label),
        "envelope_min_coverage": float(envelope_min_coverage),
        "motion_gate_floor": float(motion_gate_floor),
        "motion_gate_op": str(motion_gate_op),
        "sample_count": int(sample_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_live_training_recommendation_packet(
        label=str(payload.get("label") or ""),
        envelope_min_coverage=float(payload.get("envelope_min_coverage") or 0.0),
        motion_gate_floor=float(payload.get("motion_gate_floor") or 0.0),
        motion_gate_op=str(payload.get("motion_gate_op") or ""),
        sample_count=int(payload.get("sample_count") or 0),
    )
    output_packet = {
        "packet_type": "runtime.save_response.v1",
        "packet_version": "runtime.save_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "live-training-recommendation-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built live-training recommendation packet.",
        "refs": [],
        "data": {
            "label": value.get("label", ""),
            "motion_gate_op": value.get("motion_gate_op", ""),
            "sample_count": value.get("sample_count", 0),
        },
    }]
