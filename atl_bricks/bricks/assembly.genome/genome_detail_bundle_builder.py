from __future__ import annotations

import json
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.detail_bundle_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.catalog_request.v1"],
    "outputs": ["assembly.catalog_response.v1"],
    "requires": [],
    "provides": ["assembly.genome_detail_bundle"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "genome", "detail"],
    "description": "Build a rich genome detail read model from resolved genome, lineage, traits, pairings, tunnel, and awards inputs.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    if "genome" not in input_packet.get("payload", {}):
        return [{"code": "missing_genome", "message": "payload.genome is required."}]
    return []


def genome_json_list(genome: dict[str, Any], field: str) -> list[str]:
    try:
        return list(json.loads(genome.get(field) or "[]"))
    except Exception:
        return []


def build_genome_detail_bundle(
    genome: dict[str, Any] | None,
    versions: list[dict[str, Any]] | None = None,
    users: list[dict[str, Any]] | None = None,
    children: list[dict[str, Any]] | None = None,
    parent: dict[str, Any] | None = None,
    parent_name: str = "",
    traits: list[dict[str, Any]] | None = None,
    pairings: list[dict[str, Any]] | None = None,
    tunnel: dict[str, Any] | None = None,
    trophy_shelf: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    if not genome:
        return None
    row = dict(genome)
    row["tags_list"] = genome_json_list(row, "tags_produced")
    row["indicators_list"] = genome_json_list(row, "required_indicators")
    row["custom_data_list"] = genome_json_list(row, "requires_custom_data_keys")
    return {
        "genome": row,
        "versions": list(versions or []),
        "users": list(users or []),
        "children": list(children or []),
        "parent": parent,
        "parent_name": parent_name,
        "traits": list(traits or []),
        "pairings": list(pairings or []),
        "tunnel": tunnel,
        "trophy_shelf": list(trophy_shelf or []),
    }


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    bundle = build_genome_detail_bundle(
        genome=payload.get("genome"),
        versions=list(payload.get("versions") or []),
        users=list(payload.get("users") or []),
        children=list(payload.get("children") or []),
        parent=payload.get("parent"),
        parent_name=str(payload.get("parent_name") or ""),
        traits=list(payload.get("traits") or []),
        pairings=list(payload.get("pairings") or []),
        tunnel=payload.get("tunnel"),
        trophy_shelf=list(payload.get("trophy_shelf") or []),
    )
    output_packet = {
        "packet_type": "assembly.catalog_response.v1",
        "packet_version": "assembly.catalog_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": bundle,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet["payload"] or {}
    return [{
        "receipt_id": "genome-detail-bundle-built",
        "brick_id": CONCEPT["id"],
        "kind": "view_build",
        "label": "Built rich genome detail bundle.",
        "refs": [],
        "data": {
            "has_genome": bool(payload.get("genome")),
            "traits": len(payload.get("traits") or []),
            "pairings": len(payload.get("pairings") or []),
        },
    }]
