from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.control_param_group_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗂️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.control_param_group_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "control", "group", "assembly"],
    "description": "Package a control-surface parameter group with name, pose-gate flag, and parameter count for live runtime assembly.",
}


def build_control_param_group_packet(
    name: str,
    is_pose_gates: bool,
    param_count: int,
) -> dict[str, Any]:
    return {
        "name": str(name),
        "is_pose_gates": bool(is_pose_gates),
        "param_count": int(param_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_control_param_group_packet(
        name=str(payload.get("name") or ""),
        is_pose_gates=bool(payload.get("is_pose_gates")),
        param_count=int(payload.get("param_count") or 0),
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
        "receipt_id": "control-param-group-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built control-param group packet.",
        "refs": [],
        "data": {
            "name": value.get("name", ""),
            "is_pose_gates": value.get("is_pose_gates", False),
            "param_count": value.get("param_count", 0),
        },
    }]
