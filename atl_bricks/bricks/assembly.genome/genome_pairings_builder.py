from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.pairings_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.catalog_request.v1"],
    "outputs": ["assembly.catalog_response.v1"],
    "requires": [],
    "provides": ["assembly.genome_pairings"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "genome", "pairings"],
    "description": "Build partner pairing summaries for a genome from evidence rows.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if not payload.get("slug") or not isinstance(payload.get("evidence"), list) or not isinstance(payload.get("genomes"), list):
        return [{"code": "missing_inputs", "message": "payload.slug, payload.evidence, and payload.genomes are required."}]
    return []


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def genome_pairings(slug: str, evidence: list[dict[str, Any]], genomes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    name_by_slug = {g["slug"]: g["name"] for g in genomes if g.get("slug")}
    pair_agg: dict[str, dict[str, Any]] = {}
    for row in evidence:
        if slug not in (row.get("entry_key"), row.get("exit_key"), row.get("management_key")):
            continue
        partner = row.get("exit_key") if row.get("entry_key") == slug else row.get("entry_key")
        if not partner or partner == slug:
            continue
        agg = pair_agg.setdefault(str(partner), {"vals": [], "tiers": set()})
        agg["vals"].append(float(row.get("pnl") or 0))
        agg["tiers"].add(str(row.get("tier") or ""))
    pairings = sorted(
        (
            {
                "slug": partner,
                "name": name_by_slug.get(partner, partner),
                "pnl": round(mean(agg["vals"]), 2),
                "n": len(agg["vals"]),
                "tier": "+".join(sorted(t for t in agg["tiers"] if t)),
            }
            for partner, agg in pair_agg.items()
        ),
        key=lambda row: row["pnl"],
        reverse=True,
    )
    return pairings


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    value = genome_pairings(str(payload["slug"]), list(payload["evidence"]), list(payload["genomes"]))
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
    return [{
        "receipt_id": "genome-pairings-built",
        "brick_id": CONCEPT["id"],
        "kind": "view_build",
        "label": "Built genome pairing summaries.",
        "refs": [],
        "data": {"count": len(output_packet["payload"])},
    }]
