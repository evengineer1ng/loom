from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.genetics.breeding_outcome_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🥚",
    "deterministic": True,
    "inputs": ["math.genetics_request.v1"],
    "outputs": ["math.genetics_response.v1"],
    "requires": [],
    "provides": ["math.breeding_outcome_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "genetics", "breeding", "mutation", "offspring"],
    "description": "Package a breeding outcome with offspring genes, mutation band, cluster suppression, and inherited traits.",
}


def build_breeding_outcome_packet(
    offspring_stat_genes: list[int] | None,
    inherited_traits: list[str] | None,
    mutation_band: int,
    lineage_depth: int,
) -> dict[str, Any]:
    genes = [int(g) for g in (offspring_stat_genes or [])]
    return {
        "offspring_stat_genes": genes,
        "inherited_traits": list(inherited_traits or []),
        "mutation_band": int(mutation_band),
        "lineage_depth": int(lineage_depth),
        "cluster_suppression_active": any(total > 50 for total in [
            sum(genes[:2]) if len(genes) >= 2 else 0,
            (genes[2] + genes[5]) if len(genes) >= 6 else 0,
            (genes[3] + genes[4]) if len(genes) >= 5 else 0,
        ]),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_breeding_outcome_packet(
        offspring_stat_genes=list(payload.get("offspring_stat_genes") or []),
        inherited_traits=list(payload.get("inherited_traits") or []),
        mutation_band=int(payload.get("mutation_band") or 0),
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
        "receipt_id": "breeding-outcome-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built breeding-outcome packet.",
        "refs": [],
        "data": {"mutation_band": value.get("mutation_band", 0), "lineage_depth": value.get("lineage_depth", 0)},
    }]
