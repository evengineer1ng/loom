from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.obligation_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📌",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.obligation_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "obligation", "pressure"],
    "description": "Package a ForkUniverse obligation state with due tick, stakes, rewards, status, and pressure tags.",
}


def build_obligation_state_packet(
    obligation_id: str,
    obligation_type: str,
    holder_id: str,
    counterparty_id: str,
    start_tick: int,
    due_tick: int,
    stakes: float,
    failure_cost: float,
    success_reward: float,
    status: str,
    pressure_tags: list[str] | None,
) -> dict[str, Any]:
    return {
        "obligation_id": obligation_id,
        "obligation_type": obligation_type,
        "holder_id": holder_id,
        "counterparty_id": counterparty_id,
        "start_tick": int(start_tick),
        "due_tick": int(due_tick),
        "stakes": float(stakes),
        "failure_cost": float(failure_cost),
        "success_reward": float(success_reward),
        "status": status,
        "pressure_tags": list(pressure_tags or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_obligation_state_packet(
        obligation_id=str(payload.get("obligation_id") or ""),
        obligation_type=str(payload.get("obligation_type") or ""),
        holder_id=str(payload.get("holder_id") or ""),
        counterparty_id=str(payload.get("counterparty_id") or ""),
        start_tick=int(payload.get("start_tick") or 0),
        due_tick=int(payload.get("due_tick") or 0),
        stakes=float(payload.get("stakes") or 0.0),
        failure_cost=float(payload.get("failure_cost") or 0.0),
        success_reward=float(payload.get("success_reward") or 0.0),
        status=str(payload.get("status") or ""),
        pressure_tags=list(payload.get("pressure_tags") or []),
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
        "receipt_id": "obligation-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built obligation-state packet.",
        "refs": [],
        "data": {"obligation_id": value.get("obligation_id", ""), "status": value.get("status", "")},
    }]
