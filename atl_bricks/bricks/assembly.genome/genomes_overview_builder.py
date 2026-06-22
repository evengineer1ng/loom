from __future__ import annotations

import json
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.genomes_overview_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.catalog_request.v1"],
    "outputs": ["assembly.catalog_response.v1"],
    "requires": [],
    "provides": ["assembly.genomes_overview"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "genome", "overview"],
    "description": "Build grouped genome overviews with usage counts and decoded tag lists.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if not isinstance(payload.get("genomes"), list) or not isinstance(payload.get("assemblies"), list):
        return [{"code": "missing_inputs", "message": "payload.genomes and payload.assemblies must be lists."}]
    return []


def genome_json_list(genome: dict[str, Any], field: str) -> list[str]:
    try:
        return list(json.loads(genome.get(field) or "[]"))
    except Exception:
        return []


def assembly_genome_usage(assemblies: list[dict[str, Any]]) -> dict[str, int]:
    use: dict[str, int] = {}
    for assembly in assemblies:
        for key in ("entry_genome_slug", "exit_genome_slug", "management_genome_slug"):
            slug = assembly.get(key)
            if slug:
                use[slug] = use.get(slug, 0) + 1
    return use


def genomes_overview(genomes: list[dict[str, Any]], assemblies: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    use = assembly_genome_usage(assemblies)
    by_kind: dict[str, list[dict[str, Any]]] = {"entry": [], "exit": [], "management": [], "monolithic": []}
    for genome in genomes:
        row = dict(genome)
        row["used_by"] = use.get(row["slug"], 0)
        row["tags_list"] = genome_json_list(row, "tags_produced")
        by_kind.setdefault(str(row.get("genome_kind") or ""), []).append(row)
    return by_kind


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    overview = genomes_overview(list(payload["genomes"]), list(payload["assemblies"]))
    output_packet = {
        "packet_type": "assembly.catalog_response.v1",
        "packet_version": "assembly.catalog_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": overview,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "genomes-overview-built",
        "brick_id": CONCEPT["id"],
        "kind": "view_build",
        "label": "Built grouped genome overview.",
        "refs": [],
        "data": {"kinds": sorted(output_packet["payload"].keys())},
    }]
