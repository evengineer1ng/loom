from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.simulation.type_effectiveness_matrix",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.simulation_request.v1"],
    "outputs": ["math.simulation_response.v1"],
    "requires": [],
    "provides": ["math.type_effectiveness_matrix"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "simulation", "matrix", "type"],
    "description": "Build a balanced ring-of-advantages interaction matrix from a type count and declared advantage offsets.",
}


def build_type_effectiveness_matrix(type_count: int, advantage_offsets: list[int] | None = None) -> dict[str, Any]:
    n = max(int(type_count), 1)
    offsets = [int(item) for item in (advantage_offsets or [1, 5, 8])]
    matrix = [[1.0] * n for _ in range(n)]
    for i in range(n):
        for offset in offsets:
            j = (i + offset) % n
            matrix[i][j] = 1.25
            matrix[j][i] = 0.75
    advantages = {i: sum(1 for value in row if value == 1.25) for i, row in enumerate(matrix)}
    weaknesses = {i: sum(1 for value in row if value == 0.75) for i, row in enumerate(matrix)}
    return {"type_count": n, "offsets": offsets, "matrix": matrix, "advantages": advantages, "weaknesses": weaknesses}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_type_effectiveness_matrix(
        type_count=int(payload.get("type_count") or 18),
        advantage_offsets=list(payload.get("advantage_offsets") or [1, 5, 8]),
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
        "receipt_id": "type-effectiveness-matrix",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built type effectiveness matrix.",
        "refs": [],
        "data": {"type_count": value.get("type_count", 0)},
    }]
