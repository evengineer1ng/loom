from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.simulation.coefficient_row_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧪",
    "deterministic": True,
    "inputs": ["math.simulation_request.v1"],
    "outputs": ["math.simulation_response.v1"],
    "requires": [],
    "provides": ["math.coefficient_row_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "simulation", "forkuniverse", "coefficient", "row"],
    "description": "Package a concept-derived coefficient row with scoped name, numeric value, and explanatory description.",
}


def build_coefficient_row_packet(
    coefficient_id: str,
    scope: str,
    name: str,
    value: float,
    description: str,
) -> dict[str, Any]:
    return {
        "coefficient_id": coefficient_id,
        "scope": scope,
        "name": name,
        "value": float(value),
        "description": description,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_coefficient_row_packet(
        coefficient_id=str(payload.get("coefficient_id") or ""),
        scope=str(payload.get("scope") or ""),
        name=str(payload.get("name") or ""),
        value=float(payload.get("value") or 0.0),
        description=str(payload.get("description") or ""),
    )
    output_packet = {
        "packet_type": "math.simulation_response.v1",
        "packet_version": "math.simulation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "coefficient-row-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built coefficient-row packet.",
        "refs": [],
        "data": {"coefficient_id": value.get("coefficient_id", ""), "name": value.get("name", "")},
    }]
