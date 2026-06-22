from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.control_param_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎛️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.control_param_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "control", "param", "live-edit"],
    "description": "Package a live-editable control parameter with bounds, fine/coarse steps, integer mode, display format, and modified state.",
}


def build_control_param_packet(
    label: str,
    min_val: float,
    max_val: float,
    step: float,
    coarse_step: float,
    fmt: str,
    is_int: bool,
    modified: bool,
) -> dict[str, Any]:
    return {
        "label": str(label),
        "min_val": float(min_val),
        "max_val": float(max_val),
        "step": float(step),
        "coarse_step": float(coarse_step),
        "fmt": str(fmt),
        "is_int": bool(is_int),
        "modified": bool(modified),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_control_param_packet(
        label=str(payload.get("label") or ""),
        min_val=float(payload.get("min_val") or 0.0),
        max_val=float(payload.get("max_val") or 0.0),
        step=float(payload.get("step") or 0.0),
        coarse_step=float(payload.get("coarse_step") or 0.0),
        fmt=str(payload.get("fmt") or ""),
        is_int=bool(payload.get("is_int")),
        modified=bool(payload.get("modified")),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "control-param-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built control-param packet.",
        "refs": [],
        "data": {
            "label": value.get("label", ""),
            "is_int": value.get("is_int", False),
            "modified": value.get("modified", False),
        },
    }]
