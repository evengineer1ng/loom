from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.descriptor.forkuniverse_constraints_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧷",
    "deterministic": True,
    "inputs": ["assembly.descriptor_request.v1"],
    "outputs": ["assembly.descriptor_response.v1"],
    "requires": [],
    "provides": ["assembly.forkuniverse_constraints_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "descriptor", "forkuniverse", "constraints"],
    "description": "Package ForkUniverse creation constraints such as ceilings, density, harshness, and entropy rate.",
}


def build_forkuniverse_constraints_packet(
    violence_ceiling: float,
    romance_ceiling: float,
    absurdity_ceiling: float,
    institutional_density: float,
    economic_harshness: float,
    entropy_rate: float,
) -> dict[str, Any]:
    return {
        "violence_ceiling": float(violence_ceiling),
        "romance_ceiling": float(romance_ceiling),
        "absurdity_ceiling": float(absurdity_ceiling),
        "institutional_density": float(institutional_density),
        "economic_harshness": float(economic_harshness),
        "entropy_rate": float(entropy_rate),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_constraints_packet(
        violence_ceiling=float(payload.get("violence_ceiling") or 0.0),
        romance_ceiling=float(payload.get("romance_ceiling") or 0.0),
        absurdity_ceiling=float(payload.get("absurdity_ceiling") or 0.0),
        institutional_density=float(payload.get("institutional_density") or 0.0),
        economic_harshness=float(payload.get("economic_harshness") or 0.0),
        entropy_rate=float(payload.get("entropy_rate") or 0.0),
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
        "receipt_id": "forkuniverse-constraints-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse constraints packet.",
        "refs": [],
        "data": {"entropy_rate": value.get("entropy_rate", 0.0), "economic_harshness": value.get("economic_harshness", 0.0)},
    }]
