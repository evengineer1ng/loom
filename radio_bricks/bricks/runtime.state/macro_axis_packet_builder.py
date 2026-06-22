from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.macro_axis_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📈",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.macro_axis_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "macro", "axis"],
    "description": "Package a ForkUniverse macro axis with baseline, current value, normalization bias, and drift rate.",
}


def build_macro_axis_packet(
    axis_id: str,
    baseline: float,
    current_value: float,
    normalization_bias: float,
    drift_rate: float,
) -> dict[str, Any]:
    return {
        "axis_id": axis_id,
        "baseline": float(baseline),
        "current_value": float(current_value),
        "normalization_bias": float(normalization_bias),
        "drift_rate": float(drift_rate),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_macro_axis_packet(
        axis_id=str(payload.get("axis_id") or ""),
        baseline=float(payload.get("baseline") or 0.0),
        current_value=float(payload.get("current_value") or 0.0),
        normalization_bias=float(payload.get("normalization_bias") or 0.0),
        drift_rate=float(payload.get("drift_rate") or 0.0),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "macro-axis-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built macro-axis packet.",
        "refs": [],
        "data": {"axis_id": value.get("axis_id", ""), "current_value": value.get("current_value", 0.0)},
    }]
