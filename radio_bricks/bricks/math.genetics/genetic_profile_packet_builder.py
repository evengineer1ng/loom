from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.genetics.genetic_profile_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧬",
    "deterministic": True,
    "inputs": ["math.genetics_request.v1"],
    "outputs": ["math.genetics_response.v1"],
    "requires": [],
    "provides": ["math.genetic_profile_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "genetics", "profile", "cluster", "lineage"],
    "description": "Package a Neikos genetic profile with stat genes, trait genes, cluster totals, variance seed, and lineage depth.",
}


def build_genetic_profile_packet(
    stat_genes: list[int] | None,
    trait_genes: list[str] | None,
    variance_seed: int,
    lineage_depth: int,
) -> dict[str, Any]:
    genes = [int(g) for g in (stat_genes or [])]
    return {
        "stat_genes": genes,
        "trait_genes": list(trait_genes or []),
        "variance_seed": int(variance_seed),
        "lineage_depth": int(lineage_depth),
        "physical_cluster": sum(genes[:2]) if len(genes) >= 2 else 0,
        "tempo_cluster": (genes[2] + genes[5]) if len(genes) >= 6 else 0,
        "cognitive_cluster": (genes[3] + genes[4]) if len(genes) >= 5 else 0,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_genetic_profile_packet(
        stat_genes=list(payload.get("stat_genes") or []),
        trait_genes=list(payload.get("trait_genes") or []),
        variance_seed=int(payload.get("variance_seed") or 0),
        lineage_depth=int(payload.get("lineage_depth") or 0),
    )
    output_packet = {
        "packet_type": "math.genetics_response.v1",
        "packet_version": "math.genetics_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "genetic-profile-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built genetic-profile packet.",
        "refs": [],
        "data": {"lineage_depth": value.get("lineage_depth", 0)},
    }]
