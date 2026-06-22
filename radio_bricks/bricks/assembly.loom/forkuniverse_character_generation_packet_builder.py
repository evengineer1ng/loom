from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.forkuniverse_character_generation_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "👥",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.forkuniverse_character_generation_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "forkuniverse", "character", "generation"],
    "description": "Package the generated character rows built from naming banks, archetypes, location/org assignment, and concept-shaped biases.",
}


def build_forkuniverse_character_generation_packet(
    canonical_seed: str,
    total_characters: int,
    location_ids: list[str] | None,
    organization_ids: list[str] | None,
    characters: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "canonical_seed": canonical_seed,
        "total_characters": int(total_characters),
        "location_ids": list(location_ids or []),
        "organization_ids": list(organization_ids or []),
        "characters": [dict(item) for item in (characters or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_character_generation_packet(
        canonical_seed=str(payload.get("canonical_seed") or ""),
        total_characters=int(payload.get("total_characters") or 0),
        location_ids=list(payload.get("location_ids") or []),
        organization_ids=list(payload.get("organization_ids") or []),
        characters=list(payload.get("characters") or []),
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
        "receipt_id": "forkuniverse-character-generation-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse character-generation packet.",
        "refs": [],
        "data": {"total_characters": value.get("total_characters", 0), "row_count": len(value.get("characters", []))},
    }]
