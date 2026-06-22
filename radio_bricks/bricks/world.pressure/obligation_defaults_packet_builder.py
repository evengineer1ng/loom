from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.pressure.obligation_defaults_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📋",
    "deterministic": True,
    "inputs": ["world.pressure_request.v1"],
    "outputs": ["world.pressure_response.v1"],
    "requires": [],
    "provides": ["world.obligation_defaults_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "pressure", "forkuniverse", "obligation", "defaults"],
    "description": "Package concept-derived obligation defaults such as type, stakes, failure cost, success reward, due-tick delta, and pressure tags.",
}


def build_obligation_defaults_packet(
    obligation_type: str,
    stakes: float,
    failure_cost: float,
    success_reward: float,
    due_tick_delta: int,
    pressure_tags: list[str] | None,
) -> dict[str, Any]:
    return {
        "obligation_type": obligation_type,
        "stakes": float(stakes),
        "failure_cost": float(failure_cost),
        "success_reward": float(success_reward),
        "due_tick_delta": int(due_tick_delta),
        "pressure_tags": list(pressure_tags or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_obligation_defaults_packet(
        obligation_type=str(payload.get("obligation_type") or ""),
        stakes=float(payload.get("stakes") or 0.0),
        failure_cost=float(payload.get("failure_cost") or 0.0),
        success_reward=float(payload.get("success_reward") or 0.0),
        due_tick_delta=int(payload.get("due_tick_delta") or 0),
        pressure_tags=list(payload.get("pressure_tags") or []),
    )
    output_packet = {
        "packet_type": "world.pressure_response.v1",
        "packet_version": "world.pressure_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "obligation-defaults-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built obligation-defaults packet.",
        "refs": [],
        "data": {"obligation_type": value.get("obligation_type", ""), "due_tick_delta": value.get("due_tick_delta", 0)},
    }]
