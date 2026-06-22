from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.lineage_view_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.catalog_request.v1"],
    "outputs": ["assembly.catalog_response.v1"],
    "requires": [],
    "provides": ["assembly.genome_lineage_view"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "genome", "lineage"],
    "description": "Build parent-child lineage and usage views for a genome.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if "slug" not in payload or not isinstance(payload.get("genomes"), list) or not isinstance(payload.get("assemblies"), list):
        return [{"code": "missing_inputs", "message": "payload.slug, payload.genomes, and payload.assemblies are required."}]
    return []


def genome_lineage_view(slug: str, genomes: list[dict[str, Any]], assemblies: list[dict[str, Any]]) -> dict[str, Any]:
    name_by_slug = {g["slug"]: g["name"] for g in genomes if g.get("slug")}
    parent = next((g for g in genomes if g.get("slug") == next((x.get("parent_genome_slug") for x in genomes if x.get("slug") == slug), "")), None)
    children = [dict(g) for g in genomes if g.get("parent_genome_slug") == slug]
    users: list[dict[str, Any]] = []
    for assembly in assemblies:
        roles = [
            role for role, key in (
                ("entry", "entry_genome_slug"),
                ("exit", "exit_genome_slug"),
                ("management", "management_genome_slug"),
            ) if assembly.get(key) == slug
        ]
        if roles:
            users.append({"assembly": assembly, "roles": roles})
    return {
        "slug": slug,
        "parent": parent,
        "parent_name": name_by_slug.get((parent or {}).get("slug", ""), ""),
        "children": children,
        "users": users,
    }


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    value = genome_lineage_view(str(payload["slug"]), list(payload["genomes"]), list(payload["assemblies"]))
    output_packet = {
        "packet_type": "assembly.catalog_response.v1",
        "packet_version": "assembly.catalog_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet["payload"]
    return [{
        "receipt_id": "genome-lineage-view-built",
        "brick_id": CONCEPT["id"],
        "kind": "view_build",
        "label": "Built genome lineage view.",
        "refs": [],
        "data": {"children": len(payload.get("children") or []), "users": len(payload.get("users") or [])},
    }]
