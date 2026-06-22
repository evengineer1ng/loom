from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.assemblies_overview_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.catalog_request.v1"],
    "outputs": ["assembly.catalog_response.v1"],
    "requires": [],
    "provides": ["assembly.assemblies_overview"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "overview", "display"],
    "description": "Build assembly overview rows with resolved organ display names.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if not isinstance(payload.get("genomes"), list) or not isinstance(payload.get("assemblies"), list):
        return [{"code": "missing_inputs", "message": "payload.genomes and payload.assemblies must be lists."}]
    return []


def assemblies_overview(genomes: list[dict[str, Any]], assemblies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    name_by_slug = {g["slug"]: g["name"] for g in genomes if g.get("slug")}
    rows: list[dict[str, Any]] = []
    for assembly in assemblies:
        row = dict(assembly)
        row["entry_name"] = name_by_slug.get(row.get("entry_genome_slug") or "", "")
        row["exit_name"] = name_by_slug.get(row.get("exit_genome_slug") or "", "")
        row["mgmt_name"] = name_by_slug.get(row.get("management_genome_slug") or "", "")
        row["is_dev"] = str(row.get("source_team_id") or "").startswith("dev:")
        rows.append(row)
    return rows


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    overview = assemblies_overview(list(payload["genomes"]), list(payload["assemblies"]))
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
        "receipt_id": "assemblies-overview-built",
        "brick_id": CONCEPT["id"],
        "kind": "view_build",
        "label": "Built assembly overview rows.",
        "refs": [],
        "data": {"count": len(output_packet["payload"])},
    }]
