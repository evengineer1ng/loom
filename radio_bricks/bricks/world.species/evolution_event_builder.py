from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.species.evolution_event_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🦋",
    "deterministic": True,
    "inputs": ["world.species_request.v1"],
    "outputs": ["world.species_response.v1"],
    "requires": [],
    "provides": ["world.evolution_event_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "species", "evolution", "event", "level"],
    "description": "Package a single Neikos evolution event from old species to new species at the triggering level.",
}


def build_evolution_event_packet(
    instance_id: str,
    old_species_id: str,
    old_species_name: str,
    new_species_id: str,
    new_species_name: str,
    new_evo_stage: int,
    level: int,
) -> dict[str, Any]:
    return {
        "instance_id": instance_id,
        "old_species_id": old_species_id,
        "old_species_name": old_species_name,
        "new_species_id": new_species_id,
        "new_species_name": new_species_name,
        "new_evo_stage": int(new_evo_stage),
        "level": int(level),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_evolution_event_packet(
        instance_id=str(payload.get("instance_id") or ""),
        old_species_id=str(payload.get("old_species_id") or ""),
        old_species_name=str(payload.get("old_species_name") or ""),
        new_species_id=str(payload.get("new_species_id") or ""),
        new_species_name=str(payload.get("new_species_name") or ""),
        new_evo_stage=int(payload.get("new_evo_stage") or 0),
        level=int(payload.get("level") or 0),
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
        "receipt_id": "evolution-event-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built evolution event packet.",
        "refs": [],
        "data": {"instance_id": value.get("instance_id", ""), "new_species_id": value.get("new_species_id", "")},
    }]
