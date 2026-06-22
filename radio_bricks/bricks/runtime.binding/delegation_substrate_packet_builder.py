from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.delegation_substrate_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧰",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.delegation_substrate_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "delegation", "substrate", "worker", "routing"],
    "description": "Package a delegation substrate descriptor with execution mode, worker identity, capabilities, and health posture.",
}


def build_delegation_substrate_packet(
    substrate_id: str,
    label: str,
    description: str,
    family: str,
    execution_mode: str,
    worker_name: str,
    supports_tool_use: bool,
    supports_mutation: bool,
    frontier: bool,
    available: bool,
    dispatchable: bool,
    health_status: str,
    command: str | None = None,
) -> dict[str, Any]:
    return {
        "id": str(substrate_id),
        "label": str(label),
        "description": str(description),
        "family": str(family),
        "execution_mode": str(execution_mode),
        "worker_name": str(worker_name),
        "supports_tool_use": bool(supports_tool_use),
        "supports_mutation": bool(supports_mutation),
        "frontier": bool(frontier),
        "available": bool(available),
        "dispatchable": bool(dispatchable),
        "health_status": str(health_status),
        "command": command,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_delegation_substrate_packet(
        substrate_id=str(payload.get("id") or ""),
        label=str(payload.get("label") or ""),
        description=str(payload.get("description") or ""),
        family=str(payload.get("family") or ""),
        execution_mode=str(payload.get("execution_mode") or ""),
        worker_name=str(payload.get("worker_name") or ""),
        supports_tool_use=bool(payload.get("supports_tool_use")),
        supports_mutation=bool(payload.get("supports_mutation")),
        frontier=bool(payload.get("frontier")),
        available=bool(payload.get("available")),
        dispatchable=bool(payload.get("dispatchable")),
        health_status=str(payload.get("health_status") or ""),
        command=payload.get("command"),
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
        "receipt_id": "delegation-substrate-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built delegation substrate packet.",
        "refs": [],
        "data": {
            "id": value.get("id", ""),
            "execution_mode": value.get("execution_mode", ""),
            "health_status": value.get("health_status", ""),
        },
    }]
