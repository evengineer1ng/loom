from __future__ import annotations

from collections import defaultdict
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.trophy_shelf_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.catalog_request.v1"],
    "outputs": ["assembly.catalog_response.v1"],
    "requires": [],
    "provides": ["assembly.genome_trophy_shelf"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "genome", "awards", "trophy"],
    "description": "Organize strategy-award rows into a genome trophy shelf with grouped award types and season counts.",
}


def build_genome_trophy_shelf(awards: list[dict[str, Any]] | None) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for award in list(awards or []):
        row = dict(award)
        grouped[str(row.get("award_type") or "unknown")].append(row)
    award_types = []
    for award_type in sorted(grouped.keys()):
        rows = sorted(grouped[award_type], key=lambda row: (str(row.get("season_label") or ""), str(row.get("awarded_at") or "")), reverse=True)
        award_types.append({
            "award_type": award_type,
            "count": len(rows),
            "awards": rows,
        })
    return {
        "award_types": award_types,
        "total_awards": sum(item["count"] for item in award_types),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    shelf = build_genome_trophy_shelf([dict(item) for item in (payload.get("awards") or []) if isinstance(item, dict)])
    output_packet = {
        "packet_type": "assembly.catalog_response.v1",
        "packet_version": "assembly.catalog_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": shelf,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet.get("payload") or {}
    return [{
        "receipt_id": "genome-trophy-shelf-built",
        "brick_id": CONCEPT["id"],
        "kind": "view_build",
        "label": "Built genome trophy shelf view.",
        "refs": [],
        "data": {"award_types": len(payload.get("award_types") or []), "total_awards": payload.get("total_awards", 0)},
    }]
