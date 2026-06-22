from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.forkuniverse_character_bias_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧍",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.forkuniverse_character_bias_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "forkuniverse", "character", "bias"],
    "description": "Package the concept-derived character biases that shape resources, desires, fears, stress, myth tags, and starting promises.",
}


def build_forkuniverse_character_bias_packet(
    resource_state: dict[str, float] | None,
    desire_vector: dict[str, float] | None,
    fear_vector: dict[str, float] | None,
    stress_profile: dict[str, float] | None,
    myth_tags: list[str] | None,
    starting_promises: list[str] | None,
) -> dict[str, Any]:
    return {
        "resource_state": {str(key): float(value) for key, value in (resource_state or {}).items()},
        "desire_vector": {str(key): float(value) for key, value in (desire_vector or {}).items()},
        "fear_vector": {str(key): float(value) for key, value in (fear_vector or {}).items()},
        "stress_profile": {str(key): float(value) for key, value in (stress_profile or {}).items()},
        "myth_tags": list(myth_tags or []),
        "starting_promises": list(starting_promises or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_character_bias_packet(
        resource_state=dict(payload.get("resource_state") or {}),
        desire_vector=dict(payload.get("desire_vector") or {}),
        fear_vector=dict(payload.get("fear_vector") or {}),
        stress_profile=dict(payload.get("stress_profile") or {}),
        myth_tags=list(payload.get("myth_tags") or []),
        starting_promises=list(payload.get("starting_promises") or []),
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
        "receipt_id": "forkuniverse-character-bias-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse character-bias packet.",
        "refs": [],
        "data": {"myth_tag_count": len(value.get("myth_tags", [])), "starting_promise_count": len(value.get("starting_promises", []))},
    }]
