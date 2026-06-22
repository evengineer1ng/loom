from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.motion_accuracy_library_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📐",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.motion_accuracy_library_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "motion", "accuracy", "library"],
    "description": "Package motion-accuracy library state with selected features, checkpoint count, distance scale, and normalized template length.",
}


def build_motion_accuracy_library_packet(
    label: str,
    selected_feature_names: list[str] | None,
    checkpoint_count: int,
    scale: float,
    length: int,
) -> dict[str, Any]:
    return {
        "label": str(label),
        "selected_feature_names": [str(item) for item in (selected_feature_names or [])],
        "checkpoint_count": int(checkpoint_count),
        "scale": float(scale),
        "length": int(length),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_motion_accuracy_library_packet(
        label=str(payload.get("label") or ""),
        selected_feature_names=list(payload.get("selected_feature_names") or []),
        checkpoint_count=int(payload.get("checkpoint_count") or 0),
        scale=float(payload.get("scale") or 0.0),
        length=int(payload.get("length") or 0),
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
        "receipt_id": "motion-accuracy-library-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built motion-accuracy library packet.",
        "refs": [],
        "data": {
            "label": value.get("label", ""),
            "checkpoint_count": value.get("checkpoint_count", 0),
            "length": value.get("length", 0),
        },
    }]
