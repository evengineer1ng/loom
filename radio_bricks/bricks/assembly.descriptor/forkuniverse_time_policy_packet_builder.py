from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.descriptor.forkuniverse_time_policy_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⏳",
    "deterministic": True,
    "inputs": ["assembly.descriptor_request.v1"],
    "outputs": ["assembly.descriptor_response.v1"],
    "requires": [],
    "provides": ["assembly.forkuniverse_time_policy_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "descriptor", "forkuniverse", "time", "policy"],
    "description": "Package the ForkUniverse execution model and world-time conversion policy.",
}


def build_forkuniverse_time_policy_packet(
    execution_model: str,
    preset: str,
    world_seconds_per_real_second: float,
) -> dict[str, Any]:
    return {
        "execution_model": execution_model,
        "preset": preset,
        "world_seconds_per_real_second": float(world_seconds_per_real_second),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_time_policy_packet(
        execution_model=str(payload.get("execution_model") or ""),
        preset=str(payload.get("preset") or ""),
        world_seconds_per_real_second=float(payload.get("world_seconds_per_real_second") or 0.0),
    )
    output_packet = {
        "packet_type": "assembly.descriptor_response.v1",
        "packet_version": "assembly.descriptor_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "forkuniverse-time-policy-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse time-policy packet.",
        "refs": [],
        "data": {"execution_model": value.get("execution_model", ""), "preset": value.get("preset", "")},
    }]
