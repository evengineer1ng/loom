from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.lifecycle.obligation_resolution_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧾",
    "deterministic": True,
    "inputs": ["runtime.lifecycle_request.v1"],
    "outputs": ["runtime.lifecycle_response.v1"],
    "requires": [],
    "provides": ["runtime.obligation_resolution_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "lifecycle", "obligation", "resolution", "contract"],
    "description": "Package obligation warning and settlement math with holder capacity, success odds, breach fallout, and spawned entropy consequences.",
}


def build_obligation_resolution_packet(
    tick: int,
    obligation_id: str,
    holder_id: str,
    counterparty_id: str,
    status_before: str,
    status_after: str,
    stakes: float,
    capacity: float,
    success_probability: float,
    emitted_event: dict[str, Any] | None,
    spawned_thread: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "obligation_id": str(obligation_id),
        "holder_id": str(holder_id),
        "counterparty_id": str(counterparty_id),
        "status_before": str(status_before),
        "status_after": str(status_after),
        "stakes": float(stakes),
        "capacity": float(capacity),
        "success_probability": float(success_probability),
        "emitted_event": dict(emitted_event or {}),
        "spawned_thread": dict(spawned_thread or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_obligation_resolution_packet(
        tick=int(payload.get("tick") or 0),
        obligation_id=str(payload.get("obligation_id") or ""),
        holder_id=str(payload.get("holder_id") or ""),
        counterparty_id=str(payload.get("counterparty_id") or ""),
        status_before=str(payload.get("status_before") or ""),
        status_after=str(payload.get("status_after") or ""),
        stakes=float(payload.get("stakes") or 0.0),
        capacity=float(payload.get("capacity") or 0.0),
        success_probability=float(payload.get("success_probability") or 0.0),
        emitted_event=dict(payload.get("emitted_event") or {}),
        spawned_thread=dict(payload.get("spawned_thread") or {}),
    )
    output_packet = {
        "packet_type": "runtime.lifecycle_response.v1",
        "packet_version": "runtime.lifecycle_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "obligation-resolution-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built obligation-resolution packet.",
        "refs": [],
        "data": {
            "obligation_id": value.get("obligation_id", ""),
            "status_after": value.get("status_after", ""),
            "spawned_followup_thread": bool(value.get("spawned_thread")),
        },
    }]
