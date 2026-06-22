from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.obligation_generation_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧾",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.obligation_generation_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "forkuniverse", "obligation", "generation"],
    "description": "Package the generated obligation rows built from organization counterparties and concept-shaped defaults.",
}


def build_obligation_generation_packet(
    obligation_count: int,
    obligations: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "obligation_count": int(obligation_count),
        "obligations": [dict(item) for item in (obligations or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_obligation_generation_packet(
        obligation_count=int(payload.get("obligation_count") or 0),
        obligations=list(payload.get("obligations") or []),
    )
    output_packet = {
        "packet_type": "assembly.loom_response.v1",
        "packet_version": "assembly.loom_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "obligation-generation-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built obligation-generation packet.",
        "refs": [],
        "data": {"obligation_count": value.get("obligation_count", 0), "row_count": len(value.get("obligations", []))},
    }]
