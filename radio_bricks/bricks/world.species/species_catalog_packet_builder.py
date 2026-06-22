from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.species.species_catalog_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧾",
    "deterministic": True,
    "inputs": ["world.species_request.v1"],
    "outputs": ["world.species_response.v1"],
    "requires": [],
    "provides": ["world.species_catalog_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "species", "catalog", "read-model", "island"],
    "description": "Package the island species catalog as a portable read model of species records.",
}


def build_species_catalog_packet(
    species: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "species": [dict(item) for item in (species or [])],
        "count": len(species or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_species_catalog_packet(
        species=list(payload.get("species") or []),
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
        "receipt_id": "species-catalog-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built species-catalog packet.",
        "refs": [],
        "data": {"count": value.get("count", 0)},
    }]
