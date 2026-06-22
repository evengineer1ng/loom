from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.species.species_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🦎",
    "deterministic": True,
    "inputs": ["world.species_request.v1"],
    "outputs": ["world.species_response.v1"],
    "requires": [],
    "provides": ["world.species_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "species", "creature", "evolution", "stats"],
    "description": "Package a Neikos species template with typing, rarity, base stats, passive trait, and evolution metadata.",
}


def build_species_packet(
    species_id: str,
    name: str,
    primary_type: str,
    secondary_type: str | None,
    rarity: str,
    bst: int,
    stats: tuple[int, ...] | list[int] | None,
    archetype: str,
    passive: str,
    evo_stage: int,
    evo_line: str,
    evolves_to: str | None,
    evolves_from: str | None,
    evo_level: int | None,
) -> dict[str, Any]:
    return {
        "species_id": species_id,
        "name": name,
        "primary_type": primary_type,
        "secondary_type": secondary_type,
        "rarity": rarity,
        "bst": int(bst),
        "stats": list(stats or []),
        "archetype": archetype,
        "passive": passive,
        "evo_stage": int(evo_stage),
        "evo_line": evo_line,
        "evolves_to": evolves_to,
        "evolves_from": evolves_from,
        "evo_level": evo_level,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_species_packet(
        species_id=str(payload.get("species_id") or ""),
        name=str(payload.get("name") or ""),
        primary_type=str(payload.get("primary_type") or ""),
        secondary_type=payload.get("secondary_type"),
        rarity=str(payload.get("rarity") or ""),
        bst=int(payload.get("bst") or 0),
        stats=payload.get("stats") or [],
        archetype=str(payload.get("archetype") or ""),
        passive=str(payload.get("passive") or ""),
        evo_stage=int(payload.get("evo_stage") or 0),
        evo_line=str(payload.get("evo_line") or ""),
        evolves_to=payload.get("evolves_to"),
        evolves_from=payload.get("evolves_from"),
        evo_level=payload.get("evo_level"),
    )
    output_packet = {
        "packet_type": "world.species_response.v1",
        "packet_version": "world.species_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "species-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built species packet.",
        "refs": [],
        "data": {"species_id": value.get("species_id", ""), "rarity": value.get("rarity", "")},
    }]
