from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.genetics.population_gene_pool_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧫",
    "deterministic": True,
    "inputs": ["math.genetics_request.v1"],
    "outputs": ["math.genetics_response.v1"],
    "requires": [],
    "provides": ["math.population_gene_pool_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "genetics", "population", "diversity", "drift"],
    "description": "Package population gene-pool drift state for a species, including average genes, trait frequencies, and diversity variance.",
}


def build_population_gene_pool_packet(
    species_id: str,
    avg_stat_genes: list[float] | None,
    trait_frequency: dict[str, float] | None,
    diversity_variance: float,
    population_count: int,
) -> dict[str, Any]:
    return {
        "species_id": species_id,
        "avg_stat_genes": [float(g) for g in (avg_stat_genes or [])],
        "trait_frequency": {str(key): float(value) for key, value in (trait_frequency or {}).items()},
        "diversity_variance": float(diversity_variance),
        "population_count": int(population_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_population_gene_pool_packet(
        species_id=str(payload.get("species_id") or ""),
        avg_stat_genes=list(payload.get("avg_stat_genes") or []),
        trait_frequency=dict(payload.get("trait_frequency") or {}),
        diversity_variance=float(payload.get("diversity_variance") or 0.0),
        population_count=int(payload.get("population_count") or 0),
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
        "receipt_id": "population-gene-pool-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built population gene-pool packet.",
        "refs": [],
        "data": {"species_id": value.get("species_id", ""), "population_count": value.get("population_count", 0)},
    }]
